import json
import httpx
import base64
from app.core.gemini_client import get_gemini_model
from app.models.schemas import AdSignals
from app.core.exceptions import AdAnalysisError, InvalidURLError

SYSTEM_PROMPT = """You are an expert advertising analyst and conversion rate optimization (CRO) specialist.
You will analyze ad creatives and extract structured signals for landing page personalization.
Always respond with valid JSON only. No markdown, no explanation, just raw JSON."""

ANALYSIS_PROMPT = """Analyze this ad creative image carefully.

IMPORTANT:
- Read ALL visible text (headlines, buttons, captions, small text)
- Pay attention to colors, layout, and emotional cues

Return ONLY a valid JSON object with exactly these fields:

{
  "headline": "the main headline or key message of the ad",
  "cta_text": "the call-to-action text (e.g. 'Get Started Free', 'Shop Now')",
  "tone": "the emotional tone (e.g. 'urgent', 'friendly', 'professional', 'playful', 'luxury')",
  "target_audience": "who this ad targets",
  "value_proposition": "the core benefit or promise being made",
  "emotional_hook": "the emotional trigger being used",
  "color_mood": "describe the visual mood from colors"
}

Each value should be 3-15 words maximum.
"""


def _fetch_image_as_base64(image_url: str) -> tuple[str, str]:
    try:
        response = httpx.get(image_url, timeout=15, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise InvalidURLError(f"Could not fetch ad image: HTTP {e.response.status_code}")
    except httpx.RequestError as e:
        raise InvalidURLError(f"Could not reach ad image URL: {str(e)}")

    content_type = response.headers.get("content-type", "image/jpeg")

    if "png" in content_type:
        media_type = "image/png"
    elif "gif" in content_type:
        media_type = "image/gif"
    elif "webp" in content_type:
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"

    image_data = base64.b64encode(response.content).decode("utf-8")
    return image_data, media_type


def analyze_ad(ad_image_url: str) -> AdSignals:
    image_data, media_type = _fetch_image_as_base64(ad_image_url)

    model = get_gemini_model()

    try:
        response = model.generate_content(
            [
                SYSTEM_PROMPT,
                ANALYSIS_PROMPT,
                {
                    "mime_type": media_type,
                    "data": image_data,
                },
            ],
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.2,  # ✅ more consistent JSON
            },
        )
    except Exception as e:
        raise AdAnalysisError(f"Gemini Vision API error: {str(e)}")

    # ✅ SAFETY: Gemini can sometimes return None
    if not response or not response.text:
        raise AdAnalysisError("Empty response from Gemini Vision")

    raw_text = response.text.strip()

    try:
        data = json.loads(raw_text)
        return AdSignals(**data)
    except Exception as e:
        raise AdAnalysisError(f"Invalid JSON from Gemini: {str(e)} | Raw: {raw_text}")