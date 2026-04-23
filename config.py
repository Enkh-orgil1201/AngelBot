import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_POSTS_PER_RUN = int(os.getenv("MAX_POSTS_PER_RUN", "3"))

RSS_FEEDS = [
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/"},
    {"name": "Ars Technica AI", "url": "https://arstechnica.com/ai/feed/"},
    {"name": "MIT Tech Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed"},
]

AI_KEYWORDS = [
    "ai", "a.i.", "artificial intelligence", "machine learning", "ml ",
    "llm", "chatgpt", "gpt", "claude", "gemini", "openai", "anthropic",
    "deepmind", "meta ai", "mistral", "llama", "generative",
    "neural network", "deep learning", "transformer", "diffusion",
    "copilot", "agent", "autonomous",
]

POSTED_FILE = "posted.json"
