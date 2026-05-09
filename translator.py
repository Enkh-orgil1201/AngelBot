import json
import re
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
                    url, params={"key": GEMINI_API_KEY}, json=payload, timeout=90
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

SYSTEM_PROMPT = """Чи бол сэтгэл сэргээх, оюун санааны (spiritual) бичвэрийг
монгол хэл рүү дулаахан, нинжин сэтгэлтэйгээр орчуулдаг зохиолч.
Mindfulness, meditation, self-love, motivation сэдвийг уншигчдын зүрхэнд хүргэнэ.

Дүрэм:
- Гарчгийг богино, сэтгэл хөдөлгөм (80 тэмдэгтээс бага)
- Body-г 4-7 параграф, нийт 1500-2500 тэмдэгт болгоно
- Үг бус санаа, сэтгэлийг голчлон, уран яруу хэлээр орчуулна
- Зохиогчийн ишлэлийг хашилтаар хадгална
- Дулаахан үгс: "сэтгэл", "дотоод амар амгалан", "талархал", "ухамсар",
  "өөрийгөө хайрлах", "итгэл", "урам зориг", "анхаарал"
- 4-6 spiritual hashtag нэмнэ
  (жишээ: #сэтгэл #урам #медитаци #оюунсанаа #өөрийгөөхайрла #амарамгалан)

ЧУХАЛ — JSON-ийн хүчинтэй байх:
- Body-н бичвэрт онгойсон хашилт, хаагдаагүй параграф үлдээж болохгүй
- Бичвэрийг үргэлж бүтэн өгүүлбэрээр төгсгөж, цэг тавьж дуусгана
- ХАРИУЛТ ЗӨВХӨН зөв JSON форматтай байна:
  {"title": "...", "body": "...", "hashtags": ["#tag1", "#tag2"]}"""


MAX_OUTPUT_TOKENS = 16000


def translate_article(title: str, body: str, source_name: str, source_url: str) -> dict:
    user_msg = (
        f"Эх гарчиг: {title}\n\n"
        f"Эх мэдээ:\n{body}\n\n"
        f"Эх сурвалж: {source_name}\n"
        f"Холбоос: {source_url}\n\n"
        f"JSON хариултыг бүтэн, хүчинтэй байдлаар буцаа."
    )

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_msg}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7,
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }

    resp = _call_gemini_with_retry(payload)

    candidate = (resp.get("candidates") or [{}])[0]
    finish = candidate.get("finishReason", "")
    try:
        text = candidate["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Gemini response malformed: {resp}") from e

    if finish and finish != "STOP":
        print(f"     ⚠ Gemini finishReason={finish} — output may be truncated")

    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    parsed = _parse_json_lenient(text)

    title_out = parsed.get("title") or title
    body_out = (parsed.get("body") or "").strip()
    hashtags = parsed.get("hashtags") or []

    if not body_out or len(body_out) < 80:
        raise RuntimeError(
            f"Translation body too short or empty (finish={finish}, "
            f"raw_len={len(text)}). Raw: {text[:200]}"
        )

    body_out = _ensure_clean_ending(body_out)

    return {
        "title": title_out,
        "body": body_out,
        "hashtags": hashtags,
    }


def _parse_json_lenient(text: str) -> dict:
    """Parse JSON. If response is truncated, salvage title/body/hashtags from regex."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Salvage attempt — try to extract fields manually
    out: dict = {}
    title_match = re.search(r'"title"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
    if title_match:
        out["title"] = _unescape_json_string(title_match.group(1))

    body_match = re.search(r'"body"\s*:\s*"((?:[^"\\]|\\.)*)"', text, re.DOTALL)
    if body_match:
        out["body"] = _unescape_json_string(body_match.group(1))
    else:
        # Body string was opened but never closed (truncated mid-string)
        body_open = re.search(r'"body"\s*:\s*"', text)
        if body_open:
            tail = text[body_open.end():]
            # take everything up to last sentence-ending punctuation we can see
            tail = _unescape_json_string(tail)
            for marker in ['."', '!"', '?"']:
                idx = tail.rfind(marker)
                if idx > 0:
                    tail = tail[: idx + 1]
                    break
            out["body"] = tail

    hashtag_match = re.search(r'"hashtags"\s*:\s*\[([^\]]*)\]', text)
    if hashtag_match:
        tags = re.findall(r'"((?:[^"\\]|\\.)*)"', hashtag_match.group(1))
        out["hashtags"] = [_unescape_json_string(t) for t in tags]
    return out


def _unescape_json_string(s: str) -> str:
    """Unescape JSON string content (\\n, \\", \\\\, etc.) without re-parsing."""
    try:
        return json.loads(f'"{s}"')
    except json.JSONDecodeError:
        return s.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")


def _ensure_clean_ending(body: str) -> str:
    """If body ends mid-sentence, snap to last sentence boundary."""
    body = body.rstrip()
    if not body:
        return body
    if body[-1] in ".!?…\"'»":
        return body
    # find last sentence-ending punctuation
    for marker in [".", "!", "?", "…"]:
        idx = body.rfind(marker)
        if idx > len(body) * 0.5:
            return body[: idx + 1]
    # fall back — add ellipsis so it doesn't look chopped mid-word
    return body + "…"


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
