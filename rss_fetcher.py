from typing import Optional
import feedparser
import requests
from bs4 import BeautifulSoup


def fetch_feed(url: str, limit: int = 5):
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:limit]:
        items.append({
            "id": entry.get("id") or entry.get("link"),
            "title": entry.get("title", "").strip(),
            "summary": _clean_html(entry.get("summary", "")),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
        })
    return items


def fetch_article(url: str, max_chars: int = 4000) -> dict:
    """Fetch article text and main image URL in a single HTTP call."""
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        image_url = _extract_image(soup)

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        text = "\n".join(p for p in paragraphs if len(p) > 40)

        return {"text": text[:max_chars], "image": image_url}
    except Exception as e:
        print(f"[fetch_article] failed {url}: {e}")
        return {"text": "", "image": None}


def fetch_article_text(url: str, max_chars: int = 4000) -> str:
    """Back-compat wrapper — text only."""
    return fetch_article(url, max_chars)["text"]


def _extract_image(soup: BeautifulSoup) -> Optional[str]:
    # Try Open Graph / Twitter card first (most reliable main image)
    for selector in [
        ("meta", {"property": "og:image"}),
        ("meta", {"name": "og:image"}),
        ("meta", {"property": "og:image:secure_url"}),
        ("meta", {"name": "twitter:image"}),
        ("meta", {"name": "twitter:image:src"}),
    ]:
        tag = soup.find(*selector)
        if tag and tag.get("content"):
            return tag["content"].strip()

    # Fallback — first large <img> in article
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src and src.startswith("http"):
            return src
    return None


def _clean_html(html: str) -> str:
    if not html:
        return ""
    return BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
