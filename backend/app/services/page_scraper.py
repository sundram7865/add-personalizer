import requests
from bs4 import BeautifulSoup
from app.models.schemas import PageElements
from app.core.exceptions import PageScrapingError, InvalidURLError

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT = 15  # seconds


def _find_cta_button(soup: BeautifulSoup) -> str | None:
    """
    Find the most prominent CTA button on the page.
    Priority: <button> → <a> with 'btn'/'button' class → any <a> in hero/header.
    """
    cta_keywords = ["get started", "sign up", "buy now", "try free", "learn more",
                    "shop now", "start", "join", "subscribe", "book", "download"]

    # Look for buttons first
    for btn in soup.find_all("button"):
        text = btn.get_text(strip=True)
        if text and len(text) < 60:
            return text

    # Look for anchor tags styled as buttons
    for a in soup.find_all("a", class_=True):
        classes = " ".join(a.get("class", [])).lower()
        if "btn" in classes or "button" in classes or "cta" in classes:
            text = a.get_text(strip=True)
            if text and len(text) < 60:
                return text

    # Fallback: find any anchor whose text matches CTA keywords
    for a in soup.find_all("a"):
        text = a.get_text(strip=True).lower()
        if any(kw in text for kw in cta_keywords) and len(text) < 60:
            return a.get_text(strip=True)

    return None


def _find_hero_paragraph(soup: BeautifulSoup) -> str | None:
    """
    Find the hero/subheadline paragraph — typically the first meaningful <p>
    near the top of the page, not in nav/footer.
    """
    # Remove nav, footer, header, script, style to avoid noise
    for tag in soup.find_all(["nav", "footer", "script", "style", "header"]):
        tag.decompose()

    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        # Must be a real sentence, not a fragment or nav text
        if len(text) > 40 and len(text) < 400:
            return text

    return None


def scrape_page(landing_page_url: str) -> PageElements:
    """
    Layer 2: Fetch the landing page and extract key copy elements.
    Returns a PageElements object. No AI involved.
    """
    try:
        response = requests.get(landing_page_url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise InvalidURLError(f"Landing page returned HTTP error: {str(e)}")
    except requests.exceptions.ConnectionError:
        raise InvalidURLError("Could not connect to the landing page URL.")
    except requests.exceptions.Timeout:
        raise PageScrapingError("Landing page took too long to respond.")
    except requests.exceptions.RequestException as e:
        raise PageScrapingError(f"Failed to fetch landing page: {str(e)}")

    try:
        soup = BeautifulSoup(response.text, "lxml")
    except Exception:
        soup = BeautifulSoup(response.text, "html.parser")

    # Extract page title
    page_title = None
    title_tag = soup.find("title")
    if title_tag:
        page_title = title_tag.get_text(strip=True)

    # Extract H1
    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(strip=True) if h1_tag else None

    # Extract first H2
    h2_tag = soup.find("h2")
    h2 = h2_tag.get_text(strip=True) if h2_tag else None

    # Extract hero paragraph
    hero_paragraph = _find_hero_paragraph(soup)

    # Extract CTA button
    cta_button_text = _find_cta_button(soup)

    return PageElements(
        h1=h1,
        h2=h2,
        hero_paragraph=hero_paragraph,
        cta_button_text=cta_button_text,
        page_title=page_title,
    )