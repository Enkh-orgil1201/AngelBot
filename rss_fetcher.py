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


def fetch_article_text(url: str, max_chars: int = 4000) -> str:
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        text = "\n".join(p for p in paragraphs if len(p) > 40)
        return text[:max_chars]
    except Exception as e:
        print(f"[fetch_article_text] failed {url}: {e}")
        return ""


def _clean_html(html: str) -> str:
    if not html:
        return ""
    return BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
