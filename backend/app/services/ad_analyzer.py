import json
import httpx
import base64
from app.core.claude_client import get_claude_client, CLAUDE_MODEL
from app.models.schemas import AdSignals
from app.core.exceptions import AdAnalysisError, InvalidURLError

SYSTEM_PROMPT = """You are an expert advertising analyst and conversion rate optimization (CRO) specialist.
You will analyze ad creatives and extract structured signals for landing page personalization.
Always respond with valid JSON only. No markdown, no explanation, just raw JSON."""

ANALYSIS_PROMPT = """Analyze this ad creative image carefully and extract the following signals.
Return ONLY a valid JSON object with exactly these fields:

{
  "headline": "the main headline or key message of the ad",
  "cta_text": "the call-to-action text (e.g. 'Get Started Free', 'Shop Now')",
  "tone": "the emotional tone (e.g. 'urgent', 'friendly', 'professional', 'playful', 'luxury')",
  "target_audience": "who this ad targets (e.g. 'budget-conscious homeowners', 'startup founders')",
  "value_proposition": "the core benefit or promise being made",
  "emotional_hook": "the emotional trigger being used (e.g. 'fear of missing out', 'aspiration', 'trust')",
  "color_mood": "describe the visual mood from colors (e.g. 'warm and energetic', 'calm and professional')"
}

Be specific and concise. Each value should be 3-15 words maximum."""


def _fetch_image_as_base64(image_url: str) -> tuple[str, str]:
    """Download the image and return (base64_data, media_type)."""
    try:
        response = httpx.get(image_url, timeout=15, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise InvalidURLError(f"Could not fetch ad image: HTTP {e.response.status_code}")
    except httpx.RequestError as e:
        raise InvalidURLError(f"Could not reach ad image URL: {str(e)}")

    content_type = response.headers.get("content-type", "image/jpeg")
    # Normalize content type
    if "png" in content_type:
        media_type = "image/png"
    elif "gif" in content_type:
        media_type = "image/gif"
    elif "webp" in content_type:
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"

    image_data = base64.standard_b64encode(response.content).decode("utf-8")
    return image_data, media_type


def analyze_ad(ad_image_url: str) -> AdSignals:
    """
    Layer 1: Send the ad image to Claude Vision and extract structured signals.
    Returns an AdSignals object.
    """
    image_data, media_type = _fetch_image_as_base64(ad_image_url)
    client = get_claude_client()

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": ANALYSIS_PROMPT,
                        },
                    ],
                }
            ],
        )
    except Exception as e:
        raise AdAnalysisError(f"Claude Vision API error: {str(e)}")

    raw_text = response.content[0].text.strip()

    # Strip accidental markdown fences if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        data = json.loads(raw_text)
        return AdSignals(**data)
    except (json.JSONDecodeError, Exception) as e:
        raise AdAnalysisError(f"Could not parse Claude's response as JSON: {str(e)}")