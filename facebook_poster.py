from typing import Optional
import requests
from config import FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN

GRAPH_URL = "https://graph.facebook.com/v21.0"


def post_to_page(
    message: str,
    link: Optional[str] = None,
    image_url: Optional[str] = None,
) -> dict:
    """Post to page. If image_url is given, publish as a photo post with caption."""
    if image_url:
        return _post_photo(message, image_url)

    url = f"{GRAPH_URL}/{FB_PAGE_ID}/feed"
    payload = {
        "message": message,
        "access_token": FB_PAGE_ACCESS_TOKEN,
    }
    if link:
        payload["link"] = link
    r = requests.post(url, data=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def _post_photo(caption: str, image_url: str) -> dict:
    """Ask FB to fetch the image by URL and attach it to a new feed post."""
    url = f"{GRAPH_URL}/{FB_PAGE_ID}/photos"
    payload = {
        "url": image_url,
        "caption": caption,
        "access_token": FB_PAGE_ACCESS_TOKEN,
    }
    r = requests.post(url, data=payload, timeout=60)
    if not r.ok:
        # Fall back to plain text post if image upload fails
        print(f"     photo post failed ({r.status_code}): {r.text[:200]}")
        return post_to_page(caption)
    data = r.json()
    # /photos returns {id, post_id} — surface post_id for linking to the feed story
    if "post_id" in data:
        data["id"] = data["post_id"]
    return data


def verify_token() -> bool:
    url = f"{GRAPH_URL}/me"
    r = requests.get(url, params={"access_token": FB_PAGE_ACCESS_TOKEN}, timeout=15)
    return r.ok
