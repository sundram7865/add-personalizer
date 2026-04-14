from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional


# ─── Request models ──────────────────────────────────────────────────────────

class AnalyzeAdRequest(BaseModel):
    ad_image_url: str

    @field_validator("ad_image_url")
    @classmethod
    def must_be_valid_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("ad_image_url must be a valid http/https URL")
        return v


class ScrapePageRequest(BaseModel):
    landing_page_url: str

    @field_validator("landing_page_url")
    @classmethod
    def must_be_valid_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("landing_page_url must be a valid http/https URL")
        return v


class PersonalizeRequest(BaseModel):
    ad_signals: "AdSignals"
    page_elements: "PageElements"
    landing_page_url: str


# ─── Domain models ───────────────────────────────────────────────────────────

class AdSignals(BaseModel):
    headline: str
    cta_text: str
    tone: str
    target_audience: str
    value_proposition: str
    emotional_hook: str
    color_mood: str


class PageElements(BaseModel):
    h1: Optional[str] = None
    h2: Optional[str] = None
    hero_paragraph: Optional[str] = None
    cta_button_text: Optional[str] = None
    page_title: Optional[str] = None


class ChangeItem(BaseModel):
    element: str          # e.g. "H1 Headline"
    original: str
    updated: str
    cro_principle: str    # e.g. "Message Match"
    reason: str


class PersonalizedPage(BaseModel):
    modified_html: str
    changes: list[ChangeItem]
    new_elements: "PageElements"


# ─── Response models ─────────────────────────────────────────────────────────

class AnalyzeAdResponse(BaseModel):
    success: bool
    ad_signals: AdSignals


class ScrapePageResponse(BaseModel):
    success: bool
    page_elements: PageElements


class PersonalizeResponse(BaseModel):
    success: bool
    personalized_page: PersonalizedPage


class ErrorResponse(BaseModel):
    success: bool = False
    error: str