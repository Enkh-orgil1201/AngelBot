import json
import time
import requests
from config import GEMINI_API_KEY, GEMINI_MODEL

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
FALLBACK_MODELS = [GEMINI_MODEL, "gemini-2.5-flash-lite", "gemini-2.0-flash-lite"]


def _call_gemini_with_retry(payload: dict) -> dict:
    last_err = None
    for model in FALLBACK_MODELS:
        url = f"{GEMINI_BASE}/{model}:generateContent"
        for attempt in range(3):
            try:
                r = requests.post(
                    url, params={"key": GEMINI_API_KEY}, json=payload, timeout=60
                )
                if r.status_code == 200:
                    return r.json()
                if r.status_code in (429, 503):
                    delay = 2 ** attempt * 5
                    print(f"     {model} {r.status_code}, retry in {delay}s")
                    time.sleep(delay)
                    continue
                r.raise_for_status()
            except requests.exceptions.RequestException as e:
                last_err = e
                time.sleep(2 ** attempt * 2)
        print(f"     {model} exhausted, trying next model")
    raise RuntimeError(f"All Gemini models failed. Last: {last_err}")

SYSTEM_PROMPT = """Чи бол сэтгэл сэргээх, оюун санааны (spiritual) бичвэрээс
хамгийн гол мэдрэмжийг монгол хэлээр СОНГОН ГАРГАДАГ зохиолч.

ХЭТ ЧУХАЛ — Facebook "See more"-д тасрахгүй байхын тулд бичлэг МАШ БОГИНО.
  ✔ Title: 50 тэмдэгтээс богино
  ✔ Body: ЗӨВХӨН 2-3 өгүүлбэр, 150-220 тэмдэгт
  ✔ Нэг гол ишлэл/санааг гаргаж, үлдсэнийг хасна

Арга:
- Өгүүллийг бүхэлд нь дамжуулахгүй. Уншигчийн зүрхэнд хүрэх 1 гол санааг сонгож,
  уянгалаг монголоор яруу тод хэлнэ.
- Англи эх зохиол дахь ишлэлийг монголоор сайхан хэлбэрт оруулж ашигла.
- Дулаахан үгс: "сэтгэл", "амар амгалан", "талархал", "өөрийгөө хайрлах",
  "итгэл", "урам зориг", "ухамсар".
- 3-5 hashtag нэмнэ: #сэтгэл #урам #оюунсанаа #өөрийгөөхайрла #амарамгалан гэх мэт.

Хариултаа ЗӨВХӨН доорх JSON форматаар буцаана:
{"title": "...", "body": "...", "hashtags": ["#tag1", "#tag2"]}"""


def _truncate_body(body: str, max_chars: int = 230) -> str:
    if len(body) <= max_chars:
        return body
    cut = body[:max_chars]
    # snap to last sentence boundary if possible
    for marker in [". ", "! ", "? ", "\n"]:
        idx = cut.rfind(marker)
        if idx > max_chars * 0.6:
            return cut[: idx + 1].rstrip()
    return cut.rstrip() + "…"


def translate_article(title: str, body: str, source_name: str, source_url: str) -> dict:
    user_msg = (
        f"Эх гарчиг: {title}\n\n"
        f"Эх мэдээ:\n{body}\n\n"
        f"Эх сурвалж: {source_name}\n"
        f"Холбоос: {source_url}\n\n"
        f"JSON хариултыг буцаа."
    )

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_msg}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7,
            "maxOutputTokens": 3000,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }

    resp = _call_gemini_with_retry(payload)

    try:
        text = resp["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Gemini response malformed: {resp}") from e

    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"title": title, "body": text, "hashtags": []}

    return {
        "title": data.get("title", title),
        "body": _truncate_body(data.get("body", "")),
        "hashtags": data.get("hashtags", []),
    }


def format_fb_post(translated: dict, source_name: str, source_url: str) -> str:
    parts = [
        translated["title"],
        "",
        translated["body"],
        "",
        f"📖 {source_name}: {source_url}",
    ]
    if translated.get("hashtags"):
        parts.append("")
        parts.append(" ".join(translated["hashtags"]))
    return "\n".join(parts)
