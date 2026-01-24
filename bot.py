import os
import time
import threading
import telebot

from config import TOKEN
from storage.db import init_db

from handlers import start, skin, problems, budget, pager, profile, menu, faq


# состояние пользователей (в памяти)
user_data: dict = {}

# создаём бота
bot = telebot.TeleBot(TOKEN)

# --- мониторинг / уведомления админу ---
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "").strip()
BOT_NAME = os.getenv("BOT_NAME", "SkinHelper").strip() or "SkinHelper"


def notify(text: str) -> None:
    """
    Пишем админу в Telegram. Не валим бота, если уведомление не отправилось.
    """
    if not ADMIN_CHAT_ID:
        return
    try:
        telebot.TeleBot(TOKEN).send_message(int(ADMIN_CHAT_ID), f"🤖 {BOT_NAME}: {text}")
    except Exception:
        pass


def start_heartbeat() -> None:
    """
    Раз в 6 часов пишет "я жив" (можешь отключить, если не нужно).
    """
    def _run():
        while True:
            notify("💚 Я жив")
            time.sleep(6 * 60 * 60)  # 6 часов

    threading.Thread(target=_run, daemon=True).start()


def register_handlers() -> None:
    # регистрируем хендлеры (один раз!)
    start.register(bot, user_data)
    menu.register(bot, user_data)
    faq.register(bot, user_data)
    skin.register(bot, user_data)
    budget.register(bot, user_data)
    pager.register(bot, user_data)
    profile.register(bot, user_data)
    problems.register(bot, user_data)


def run_bot_forever() -> None:
    """
    Запускаем polling в вечном цикле:
    - при исключении уведомляем
    - ждём и перезапускаемся
    """
    notify("✅ Запустился (Railway)")

    # если хочешь heartbeat — оставь строку, иначе можешь удалить
    start_heartbeat()

    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)
        except Exception as e:
            notify(f"❌ Упал с ошибкой: {type(e).__name__}: {e}\nПерезапуск через 10 секунд…")
            time.sleep(10)


if __name__ == "__main__":
    init_db()
    register_handlers()
    run_bot_forever()
