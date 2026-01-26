import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
PARTNER_BASE_URL = os.getenv("PARTNER_BASE_URL")

if not TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN. Добавь его в .env")

if not PARTNER_BASE_URL:
    raise RuntimeError("Не найден PARTNER_BASE_URL. Добавь его в .env")
