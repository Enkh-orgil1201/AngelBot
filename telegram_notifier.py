import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

API_BASE = "https://api.telegram.org"


def send_notification(title: str, fb_post_url: str, source_url: str, source_name: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    text = (
        f"✅ <b>Шинэ пост орлоо</b>\n\n"
        f"<b>{_esc(title)}</b>\n\n"
        f"📰 Эх сурвалж: {_esc(source_name)}\n"
        f"🔗 <a href=\"{source_url}\">Оригинал мэдээ</a>\n"
        f"📘 <a href=\"{fb_post_url}\">Facebook дээрх пост</a>"
    )

    url = f"{API_BASE}/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": "false",
            },
            timeout=15,
        )
        r.raise_for_status()
    except Exception as e:
        print(f"     telegram notify error: {e}")


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
