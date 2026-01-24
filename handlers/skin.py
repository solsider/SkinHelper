from telebot import types
from keyboards import SKIN_TYPES, problems_keyboard
from storage.db import upsert_profile


def register(bot, user_data: dict):

    @bot.message_handler(commands=["skin"])
    def skin(message):
        from keyboards import skin_keyboard
        bot.send_message(message.chat.id, "Какой у тебя тип кожи?", reply_markup=skin_keyboard())

    @bot.message_handler(func=lambda m: (m.text or "").strip() in SKIN_TYPES)
    def handle_skin(message):
        user_data[message.chat.id] = {
            "skin_type": message.text.strip(),
            "problems": set(),
            "state": "choose_problems"
        }
        upsert_profile(message.chat.id, skin_type=message.text.strip(), problems=set(), budget=None)

        bot.send_message(
            message.chat.id,
            f"✅ Запомнил: *{message.text.strip()} кожа*.\n\n"
            "Теперь выбери проблемы (можно несколько), потом нажми *Готово*.",
            parse_mode="Markdown",
            reply_markup=types.ReplyKeyboardRemove()
        )

        bot.send_message(
            message.chat.id,
            "Выбери проблемы:",
            reply_markup=problems_keyboard(user_data[message.chat.id]["problems"])
        )
