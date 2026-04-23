from typing import Optional
import requests
from config import FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN

GRAPH_URL = "https://graph.facebook.com/v21.0"


def post_to_page(message: str, link: Optional[str] = None) -> dict:
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


def verify_token() -> bool:
    url = f"{GRAPH_URL}/me"
    r = requests.get(url, params={"access_token": FB_PAGE_ACCESS_TOKEN}, timeout=15)
    return r.ok
