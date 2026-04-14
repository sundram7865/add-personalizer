import json
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
from app.core.gemini_client import get_gemini_model
from app.models.schemas import AdSignals, PageElements, PersonalizedPage, ChangeItem
from app.core.exceptions import PersonalizationError


SYSTEM_PROMPT = """You are a senior conversion rate optimization (CRO) specialist and copywriter.
You personalize landing pages to match the tone, message, and audience of a specific ad creative.
Your goal is message match — the visitor who clicked the ad should feel the page was made for them.
Always respond with valid JSON only. No markdown, no explanation, just raw JSON."""


CRO_PRINCIPLES = [
    "Message Match: Mirror the exact language and promise from the ad",
    "Specificity: Use numbers, timeframes, and concrete details from the ad",
    "Audience Alignment: Speak directly to the target audience's pain point",
    "Value First: Lead with the benefit, not the feature",
    "Urgency: Match the urgency level of the ad's tone",
    "Trust: Keep claims believable and grounded",
]


PERSONALIZATION_PROMPT = """You are personalizing a landing page to match a specific ad creative.

AD SIGNALS:
- Headline: {headline}
- CTA Text: {cta_text}
- Tone: {tone}
- Target Audience: {target_audience}
- Value Proposition: {value_proposition}
- Emotional Hook: {emotional_hook}
- Color Mood: {color_mood}

CURRENT LANDING PAGE:
- Page Title: {page_title}
- H1: {h1}
- H2: {h2}
- Hero Paragraph: {hero_paragraph}
- CTA Button: {cta_button_text}

CRO PRINCIPLES:
{principles}

Return ONLY valid JSON in this structure:
{{
  "new_elements": {{
    "h1": "...",
    "h2": "...",
    "hero_paragraph": "...",
    "cta_button_text": "...",
    "page_title": "..."
  }},
  "changes": []
}}
"""


def _fix_asset_paths(html: str, base_url: str) -> str:
    parsed = urlparse(base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    html = html.replace('src="/', f'src="{base}/')
    html = html.replace('href="/', f'href="{base}/')

    return html

def personalize_with_dom(url: str, new_elements: PageElements) -> str:
    """
    Use Playwright to:
    - Load REAL page (JS rendered)
    - Modify DOM safely
    - Return full working HTML
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url, wait_until="networkidle")

        # ✅ Wait for React to fully render
        page.wait_for_timeout(3000)  # important!

        # ✅ Inject script that runs AFTER page loads
        page.evaluate(
            """(data) => {
                setTimeout(() => {
                    if (data.h1) {
                        document.querySelectorAll('h1').forEach(el => el.innerText = data.h1);
                    }

                    if (data.h2) {
                        document.querySelectorAll('h2').forEach(el => el.innerText = data.h2);
                    }

                    if (data.hero_paragraph) {
                        document.querySelectorAll('p').forEach(el => {
                            if (el.innerText.length > 40) {
                                el.innerText = data.hero_paragraph;
                            }
                        });
                    }

                    if (data.cta_button_text) {
                        document.querySelectorAll('button, a').forEach(el => {
                            if (el.innerText.length < 40) {
                                el.innerText = data.cta_button_text;
                            }
                        });
                    }

                    if (data.page_title) {
                        document.title = data.page_title;
                    }
                }, 1000); // delay after React render
            }""",
            {
                "h1": new_elements.h1,
                "h2": new_elements.h2,
                "hero_paragraph": new_elements.hero_paragraph,
                "cta_button_text": new_elements.cta_button_text,
                "page_title": new_elements.page_title,
            },
        )

        # ✅ wait again so changes stick
        page.wait_for_timeout(2000)

        html = page.content()
        browser.close()

        return html

def personalize_page(
    ad_signals: AdSignals,
    page_elements: PageElements,
    landing_page_url: str,
) -> PersonalizedPage:

    model = get_gemini_model()

    principles_str = "\n".join(f"- {p}" for p in CRO_PRINCIPLES)

    prompt = PERSONALIZATION_PROMPT.format(
        headline=ad_signals.headline,
        cta_text=ad_signals.cta_text,
        tone=ad_signals.tone,
        target_audience=ad_signals.target_audience,
        value_proposition=ad_signals.value_proposition,
        emotional_hook=ad_signals.emotional_hook,
        color_mood=ad_signals.color_mood,
        page_title=page_elements.page_title or "N/A",
        h1=page_elements.h1 or "N/A",
        h2=page_elements.h2 or "N/A",
        hero_paragraph=page_elements.hero_paragraph or "N/A",
        cta_button_text=page_elements.cta_button_text or "N/A",
        principles=principles_str,
    )

    try:
        response = model.generate_content(
            [SYSTEM_PROMPT, prompt],
            generation_config={"response_mime_type": "application/json"},
        )
    except Exception as e:
        raise PersonalizationError(f"Gemini API error: {str(e)}")

    raw_text = response.text.strip()

    try:
        data = json.loads(raw_text)
    except Exception as e:
        raise PersonalizationError(f"Invalid JSON from Gemini: {str(e)}")

    try:
        new_elements = PageElements(**data["new_elements"])
        changes = []
        
        for c in data.get("changes", []):
           if isinstance(c, dict):
                changes.append(ChangeItem(**c))
    except Exception as e:
        raise PersonalizationError(f"Response structure invalid: {str(e)}")

    # ✅ REAL FIX → render + modify DOM
    modified_html = personalize_with_dom(landing_page_url, new_elements)

    # ✅ Fix assets so preview works
    modified_html = _fix_asset_paths(modified_html, landing_page_url)

    return PersonalizedPage(
        modified_html=modified_html,
        changes=changes,
        new_elements=new_elements,
    )