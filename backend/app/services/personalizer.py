import json
import requests
from bs4 import BeautifulSoup
from app.core.claude_client import get_claude_client, CLAUDE_MODEL
from app.models.schemas import AdSignals, PageElements, PersonalizedPage, ChangeItem
from app.core.exceptions import PersonalizationError, InvalidURLError

SYSTEM_PROMPT = """You are a senior conversion rate optimization (CRO) specialist and copywriter.
You personalize landing pages to match the tone, message, and audience of a specific ad creative.
Your goal is message match — the visitor who clicked the ad should feel the page was made for them.
Always respond with valid JSON only. No markdown, no explanation, just raw JSON."""

# CRO principles to guide the model
CRO_PRINCIPLES = [
    "Message Match: Mirror the exact language and promise from the ad",
    "Specificity: Use numbers, timeframes, and concrete details from the ad",
    "Audience Alignment: Speak directly to the target audience's pain point",
    "Value First: Lead with the benefit, not the feature",
    "Urgency: Match the urgency level of the ad's tone",
    "Trust: Keep claims believable and grounded",
]

PERSONALIZATION_PROMPT = """You are personalizing a landing page to match a specific ad creative.

AD SIGNALS (what the user saw in the ad):
- Headline: {headline}
- CTA Text: {cta_text}
- Tone: {tone}
- Target Audience: {target_audience}
- Value Proposition: {value_proposition}
- Emotional Hook: {emotional_hook}
- Color Mood: {color_mood}

CURRENT LANDING PAGE ELEMENTS:
- Page Title: {page_title}
- H1: {h1}
- H2: {h2}
- Hero Paragraph: {hero_paragraph}
- CTA Button: {cta_button_text}

CRO PRINCIPLES TO APPLY:
{principles}

TASK:
Rewrite ONLY the elements that exist in the landing page (don't invent elements that aren't there).
For each element you change, explain which CRO principle you applied and why.

Return ONLY a valid JSON object with exactly this structure:
{{
  "new_elements": {{
    "h1": "rewritten h1 or null if not present",
    "h2": "rewritten h2 or null if not present",
    "hero_paragraph": "rewritten hero paragraph or null if not present",
    "cta_button_text": "rewritten cta or null if not present",
    "page_title": "rewritten page title or null if not present"
  }},
  "changes": [
    {{
      "element": "H1 Headline",
      "original": "the original text",
      "updated": "the new text",
      "cro_principle": "Message Match",
      "reason": "one sentence explaining the specific change"
    }}
  ]
}}

Rules:
- Only include elements that actually changed in the "changes" array
- Keep the same general length as the original — don't make it much longer
- Never fabricate facts. Build on what's already there
- The tone must match: {tone}
- The audience must feel seen: {target_audience}"""


def _fetch_page_html(url: str) -> str:
    """Fetch raw HTML of the landing page."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        raise InvalidURLError(f"Could not re-fetch landing page for modification: {str(e)}")


def _inject_changes_into_html(
    original_html: str,
    page_elements: PageElements,
    new_elements: PageElements,
) -> str:
    """
    Surgically replace only the changed text nodes in the original HTML.
    The page structure, styles, images — everything else stays intact.
    """
    try:
        soup = BeautifulSoup(original_html, "lxml")
    except Exception:
        soup = BeautifulSoup(original_html, "html.parser")

    def replace_text(tag, original_text: str | None, new_text: str | None):
        """Find a tag by its text content and replace it."""
        if not original_text or not new_text or original_text == new_text:
            return
        found = soup.find(tag, string=lambda t: t and original_text.lower() in t.lower())
        if found:
            found.string = new_text

    # Replace H1
    replace_text("h1", page_elements.h1, new_elements.h1)

    # Replace H2
    replace_text("h2", page_elements.h2, new_elements.h2)

    # Replace title tag
    if page_elements.page_title and new_elements.page_title:
        title_tag = soup.find("title")
        if title_tag:
            title_tag.string = new_elements.page_title

    # Replace hero paragraph — find by partial match since paragraphs can be complex
    if page_elements.hero_paragraph and new_elements.hero_paragraph:
        for p in soup.find_all("p"):
            if page_elements.hero_paragraph[:50].lower() in p.get_text().lower():
                p.string = new_elements.hero_paragraph
                break

    # Replace CTA button text
    if page_elements.cta_button_text and new_elements.cta_button_text:
        for btn in soup.find_all(["button", "a"]):
            if page_elements.cta_button_text.lower() in btn.get_text(strip=True).lower():
                btn.string = new_elements.cta_button_text
                break

    return str(soup)


def personalize_page(
    ad_signals: AdSignals,
    page_elements: PageElements,
    landing_page_url: str,
) -> PersonalizedPage:
    """
    Layer 3: Use Claude to generate personalized copy based on ad signals.
    Then inject changes into the real HTML. Returns PersonalizedPage.
    """
    client = get_claude_client()
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
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        raise PersonalizationError(f"Claude API error: {str(e)}")

    raw_text = response.content[0].text.strip()

    # Strip accidental markdown fences
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise PersonalizationError(f"Could not parse Claude's response as JSON: {str(e)}")

    # Parse new_elements and changes
    try:
        new_elements = PageElements(**data["new_elements"])
        changes = [ChangeItem(**c) for c in data.get("changes", [])]
    except Exception as e:
        raise PersonalizationError(f"Response structure invalid: {str(e)}")

    # Fetch original HTML and inject changes
    original_html = _fetch_page_html(landing_page_url)
    modified_html = _inject_changes_into_html(original_html, page_elements, new_elements)

    return PersonalizedPage(
        modified_html=modified_html,
        changes=changes,
        new_elements=new_elements,
    )