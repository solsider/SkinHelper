import os
from dotenv import load_dotenv

load_dotenv()

print("DEBUG BOT_TOKEN =", repr(os.getenv("BOT_TOKEN")))
print("DEBUG ENV has BOT_TOKEN =", "BOT_TOKEN" in os.environ)

TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN. Добавь его в .env")
