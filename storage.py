import hashlib
import json
import os
import re
from config import POSTED_FILE


def load_posted() -> set:
    if not os.path.exists(POSTED_FILE):
        return set()
    try:
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_posted(posted_ids: set) -> None:
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(posted_ids), f, ensure_ascii=False, indent=2)


def mark_posted(*ids: str) -> None:
    posted = load_posted()
    for i in ids:
        if i:
            posted.add(i)
    save_posted(posted)


def title_fingerprint(title: str) -> str:
    norm = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
    return "title:" + hashlib.md5(norm.encode("utf-8")).hexdigest()[:16]


STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "at", "for", "with", "by", "from", "as",
    "and", "or", "but", "not", "no", "this", "that", "these", "those",
    "it", "its", "has", "have", "had", "will", "would", "can", "could",
    "new", "now", "just", "more", "most", "some", "what", "how", "why",
    "about", "over", "out", "up", "down", "off", "into", "after", "before",
}


def title_tokens(title: str) -> frozenset:
    norm = re.sub(r"[^a-z0-9]+", " ", title.lower())
    tokens = [t for t in norm.split() if len(t) >= 3 and t not in STOPWORDS]
    return frozenset(tokens)


def is_similar_to_posted(title: str, posted_titles: list, threshold: float = 0.6) -> bool:
    new_tokens = title_tokens(title)
    if len(new_tokens) < 3:
        return False
    for past in posted_titles:
        past_tokens = title_tokens(past)
        if not past_tokens:
            continue
        overlap = len(new_tokens & past_tokens) / min(len(new_tokens), len(past_tokens))
        if overlap >= threshold:
            return True
    return False


def load_posted_titles() -> list:
    if not os.path.exists("posted_titles.json"):
        return []
    try:
        with open("posted_titles.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_posted_title(title: str, keep_last: int = 200) -> None:
    titles = load_posted_titles()
    titles.append(title)
    titles = titles[-keep_last:]
    with open("posted_titles.json", "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
