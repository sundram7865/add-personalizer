from fastapi import APIRouter
from app.models.schemas import (
    AnalyzeAdRequest, AnalyzeAdResponse, PersonalizeFullRequest, PersonalizeFullResponse,
    ScrapePageRequest, ScrapePageResponse,
    PersonalizeRequest, PersonalizeResponse,
)
from app.services.ad_analyzer import analyze_ad
from app.services.page_scraper import scrape_page
from app.services.personalizer import personalize_page

router = APIRouter(prefix="/api", tags=["personalization"])


@router.post("/analyze-ad", response_model=AnalyzeAdResponse)
def analyze_ad_route(body: AnalyzeAdRequest) -> AnalyzeAdResponse:
    """
    Layer 1: Analyze the ad creative image using Claude Vision.
    Returns structured ad signals.
    """
    ad_signals = analyze_ad(body.ad_image_url)
    return AnalyzeAdResponse(success=True, ad_signals=ad_signals)


@router.post("/scrape-page", response_model=ScrapePageResponse)
def scrape_page_route(body: ScrapePageRequest) -> ScrapePageResponse:
    """
    Layer 2: Scrape the landing page and extract key copy elements.
    Returns structured page elements. No AI used.
    """
    page_elements = scrape_page(body.landing_page_url)
    return ScrapePageResponse(success=True, page_elements=page_elements)


@router.post("/personalize", response_model=PersonalizeResponse)
def personalize_route(body: PersonalizeRequest) -> PersonalizeResponse:
    """
    Layer 3: Generate personalized copy using Claude, then inject into real HTML.
    Returns modified HTML + list of changes with CRO reasoning.
    """
    personalized = personalize_page(
        ad_signals=body.ad_signals,
        page_elements=body.page_elements,
        landing_page_url=body.landing_page_url,
    )
    return PersonalizeResponse(success=True, personalized_page=personalized)

@router.post("/personalize-full", response_model=PersonalizeFullResponse)
def personalize_full_route(body: PersonalizeFullRequest) -> PersonalizeFullResponse:
    """
    Unified endpoint: chains all 3 layers.
    Frontend only needs to call this one.
    """
    ad_signals = analyze_ad(body.ad_image_url)
    page_elements = scrape_page(body.landing_page_url)
    personalized = personalize_page(
        ad_signals=ad_signals,
        page_elements=page_elements,
        landing_page_url=body.landing_page_url,
    )
    return PersonalizeFullResponse(
        success=True,
        ad_signals=ad_signals,
        page_elements=page_elements,
        personalized_page=personalized,
    )