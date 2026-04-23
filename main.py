import sys
import time
import traceback

from config import RSS_FEEDS, MAX_POSTS_PER_RUN, AI_KEYWORDS, FB_PAGE_ID
from rss_fetcher import fetch_feed, fetch_article_text
from translator import translate_article, format_fb_post
from facebook_poster import post_to_page
from storage import (
    load_posted,
    mark_posted,
    title_fingerprint,
    is_similar_to_posted,
    load_posted_titles,
    save_posted_title,
)
from telegram_notifier import send_notification


def is_ai_related(title: str, summary: str) -> bool:
    haystack = f"{title}\n{summary}".lower()
    return any(kw in haystack for kw in AI_KEYWORDS)


def fb_post_url(post_id: str) -> str:
    # post_id format: "PAGE_ID_POST_ID" — extract the post part
    if "_" in post_id:
        _, pid = post_id.split("_", 1)
        return f"https://www.facebook.com/{FB_PAGE_ID}/posts/{pid}"
    return f"https://www.facebook.com/{post_id}"


def run(dry_run: bool = False) -> None:
    posted_ids = load_posted()
    posted_titles = load_posted_titles()
    published_count = 0

    print(f"[start] already posted: {len(posted_ids)} | limit: {MAX_POSTS_PER_RUN}")

    for feed in RSS_FEEDS:
        if published_count >= MAX_POSTS_PER_RUN:
            break

        print(f"\n[feed] {feed['name']}")
        try:
            items = fetch_feed(feed["url"], limit=5)
        except Exception as e:
            print(f"  feed error: {e}")
            continue

        for item in items:
            if published_count >= MAX_POSTS_PER_RUN:
                break

            article_id = item["id"]
            title_id = title_fingerprint(item["title"])

            if not article_id or article_id in posted_ids:
                continue
            if title_id in posted_ids:
                print(f"  -- skip dup title: {item['title'][:60]}")
                continue
            if is_similar_to_posted(item["title"], posted_titles):
                print(f"  -- skip similar: {item['title'][:60]}")
                continue

            if not is_ai_related(item["title"], item["summary"]):
                continue

            print(f"  -> {item['title'][:70]}")

            body = fetch_article_text(item["link"]) or item["summary"]
            if len(body) < 100:
                print("     skipped (too short)")
                continue

            try:
                translated = translate_article(
                    item["title"], body, feed["name"], item["link"]
                )
                post_text = format_fb_post(translated, feed["name"], item["link"])
            except Exception as e:
                print(f"     translate error: {e}")
                continue

            if dry_run:
                print("     [dry-run] would post:")
                print("     " + post_text.replace("\n", "\n     "))
            else:
                try:
                    res = post_to_page(post_text, link=item["link"])
                    fb_id = res.get("id", "")
                    print(f"     posted id={fb_id}")
                except Exception as e:
                    print(f"     fb error: {e}")
                    continue

                mark_posted(article_id, title_id)
                save_posted_title(item["title"])
                posted_ids.add(article_id)
                posted_ids.add(title_id)
                posted_titles.append(item["title"])

                send_notification(
                    title=translated["title"],
                    fb_post_url=fb_post_url(fb_id),
                    source_url=item["link"],
                    source_name=feed["name"],
                )

            published_count += 1
            time.sleep(8)  # Gemini free tier: ~10 RPM = 6s min

    print(f"\n[done] published: {published_count}")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    try:
        run(dry_run=dry)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
