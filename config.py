import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_POSTS_PER_RUN = int(os.getenv("MAX_POSTS_PER_RUN", "1"))

# Сэтгэл сэргээх / spiritual / motivational RSS эх сурвалжууд
RSS_FEEDS = [
    {"name": "Tiny Buddha",      "url": "https://tinybuddha.com/feed/"},
    {"name": "Positivity Blog",  "url": "https://www.positivityblog.com/feed/"},
    {"name": "Marc and Angel",   "url": "https://www.marcandangel.com/feed/"},
    {"name": "Mindful",          "url": "https://www.mindful.org/feed/"},
    {"name": "Purpose Fairy",    "url": "https://www.purposefairy.com/feed/"},
    {"name": "Lifehack",         "url": "https://www.lifehack.org/feed"},
]

# Түлхүүр үг — title/summary-д эдгээрийн аль нэг байвал л постлоно
AI_KEYWORDS = [
    # meditation / mindfulness
    "meditation", "mindful", "mindfulness", "zen", "presence",
    "awareness", "consciousness",
    # spiritual / soul
    "spiritual", "soul", "spirit", "divine", "sacred", "inner",
    "purpose", "meaning",
    # emotion / healing
    "healing", "heal", "peace", "calm", "gratitude", "grateful",
    "compassion", "kindness", "forgiveness", "love",
    # growth / motivation
    "self-love", "self love", "growth", "motivation", "inspire",
    "inspiration", "inspired", "journey", "wisdom",
    "happiness", "happy", "joy", "hope", "faith",
    # habits / wellbeing
    "habit", "mindset", "positive", "affirmation", "letting go",
    "let go", "wellbeing", "well-being", "wellness",
    "life lesson", "life lessons", "quote", "truth",
]

POSTED_FILE = "posted.json"
