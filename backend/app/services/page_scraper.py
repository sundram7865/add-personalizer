from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from app.models.schemas import PageElements
from app.core.exceptions import PageScrapingError, InvalidURLError

from playwright.sync_api import sync_playwright

def _fetch_rendered_html(url: str) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, wait_until="networkidle")
            html = page.content()

            browser.close()
            return html
    except Exception as e:
        raise Exception(f"Playwright error: {str(e)}")
    
def _fetch_rendered_html(url: str) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, timeout=30000)

            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)

            # ✅ THIS FIXES EVERYTHING
            html = page.content()

            # ✅ Convert relative URLs to absolute
            html = html.replace('src="/', f'src="{url}/')
            html = html.replace('href="/', f'href="{url}/')

            browser.close()
            return html

    except Exception as e:
        raise Exception(f"Playwright error: {str(e)}")

def _find_cta_button(soup: BeautifulSoup) -> str | None:
    cta_keywords = [
        "get started", "sign up", "buy now", "try free",
        "learn more", "shop now", "start", "join",
        "subscribe", "book", "download"
    ]

    for btn in soup.find_all("button"):
        text = btn.get_text(strip=True)
        if text and len(text) < 60:
            return text

    for a in soup.find_all("a", class_=True):
        classes = " ".join(a.get("class", [])).lower()
        if "btn" in classes or "button" in classes or "cta" in classes:
            text = a.get_text(strip=True)
            if text and len(text) < 60:
                return text

    for a in soup.find_all("a"):
        text = a.get_text(strip=True).lower()
        if any(kw in text for kw in cta_keywords) and len(text) < 60:
            return a.get_text(strip=True)

    return None


def _find_hero_paragraph(soup: BeautifulSoup) -> str | None:
    for tag in soup.find_all(["nav", "footer", "script", "style", "header"]):
        tag.decompose()

    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if 40 < len(text) < 400:
            return text

    return None


def scrape_page(landing_page_url: str) -> PageElements:
    """
    Layer 2: Fetch rendered landing page and extract content.
    """

    # ✅ KEY CHANGE: use Playwright instead of requests
    html = _fetch_rendered_html(landing_page_url)

    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    # Extract title
    title_tag = soup.find("title")
    page_title = title_tag.get_text(strip=True) if title_tag else None

    # Extract H1
    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(strip=True) if h1_tag else None

    # Extract H2
    h2_tag = soup.find("h2")
    h2 = h2_tag.get_text(strip=True) if h2_tag else None

    # Extract hero paragraph
    hero_paragraph = _find_hero_paragraph(soup)

    # Extract CTA
    cta_button_text = _find_cta_button(soup)

    return PageElements(
        h1=h1,
        h2=h2,
        hero_paragraph=hero_paragraph,
        cta_button_text=cta_button_text,
        page_title=page_title,
    )