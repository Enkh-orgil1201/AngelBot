# NewsAutoBot

RSS мэдээг Claude-аар монгол руу орчуулаад Facebook Page дээр автомат пост оруулдаг бот.

## Тохиргоо

### 1. Dependencies суулгах

```bash
cd C:\Hustle\NewsAutoBot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. `.env` файл үүсгэх

```bash
copy .env.example .env
```

Дараа нь `.env` файлыг нээж дараах утгуудыг бөглөнө:

- **ANTHROPIC_API_KEY** — https://console.anthropic.com/ -ээс авна
- **FB_PAGE_ID** — Facebook хуудасны ID (Page → About → Page ID)
- **FB_PAGE_ACCESS_TOKEN** — Long-lived Page Access Token

### 3. Facebook Page Access Token авах

1. https://developers.facebook.com/ дээр App үүсгэнэ (Type: Business)
2. Graph API Explorer ашиглаад **Page Access Token** авна
3. `pages_manage_posts`, `pages_read_engagement` эрхүүдийг сонгоно
4. Short-lived token-ыг Long-lived (60 өдөр) болгож хөрвүүлнэ:
   ```
   https://graph.facebook.com/v21.0/oauth/access_token?
     grant_type=fb_exchange_token&
     client_id={APP_ID}&
     client_secret={APP_SECRET}&
     fb_exchange_token={SHORT_TOKEN}
   ```

## Ашиглах

### Dry-run (пост оруулахгүй, зөвхөн харуулна)

```bash
python main.py --dry-run
```

### Бодит постлох

```bash
python main.py
```

### Автоматжуулалт (Windows Task Scheduler)

1. Task Scheduler нээнэ
2. Шинэ Task үүсгэнэ — "NewsAutoBot"
3. Trigger: Daily, 3 удаа (жишээ: 09:00, 13:00, 19:00)
4. Action: `python C:\Hustle\NewsAutoBot\main.py`

### Linux VPS дээр cron

```bash
0 9,13,19 * * * cd /path/to/NewsAutoBot && /path/to/venv/bin/python main.py >> bot.log 2>&1
```

## Файлууд

- `main.py` — Гол ажиллагаа (RSS → Translate → Post)
- `config.py` — Тохиргоо, RSS эх сурвалжуудын жагсаалт
- `rss_fetcher.py` — RSS татах, бүрэн текст татах
- `translator.py` — Claude API-аар орчуулах
- `facebook_poster.py` — FB Graph API
- `storage.py` — Давхар пост оруулахгүйн тулд ID хадгалах
- `posted.json` — Өмнө постолсон мэдээний ID-ууд

## RSS эх сурвалж өөрчлөх

`config.py` дотор `RSS_FEEDS` жагсаалт руу нэмж/хасна.

## Үнэ

- Claude Haiku: ~$1 / сая input токен, $5 / сая output токен
- Нэг пост ≈ 2000 токен → ~$0.002 (0.005₮)
- Өдөрт 10 пост = сард ~$0.6
- VPS: Hetzner CX11 €4/сар (эсвэл өөрийн PC дээр)

## Анхаарах

- Facebook-ийн copyright дүрмээр эх сурвалжийг **заавал** дурдах ёстой (код аль хэдийн хийдэг)
- Нэг өдөрт хэтэрхий олон пост оруулбал спам гэж тооцох эрсдэлтэй (өдөрт 3-5 хангалттай)
- `posted.json` файлыг устгавал тухайн мэдээг дахин постлох магадлалтай
