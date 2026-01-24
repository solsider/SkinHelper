from keyboards import skin_keyboard, main_menu_keyboard
from storage.db import get_profile

def register(bot, user_data: dict):

    @bot.message_handler(commands=["start"])
    def start_cmd(message):
        chat_id = message.chat.id

        profile = get_profile(chat_id)
        if profile:
            user_data[chat_id] = profile

        bot.send_message(
            chat_id,
            "👋 Привет! Я *Умный Уход* 🌿\n\n"
            "Подберу уход под тип кожи, проблемы и бюджет.\n"
            "Выбери действие в меню ниже 👇",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )


    @bot.message_handler(func=lambda m: m.text == "🏠 Главное меню")
    def back_to_menu(message):
        bot.send_message(
            message.chat.id,
            "🏠 Главное меню",
            reply_markup=main_menu_keyboard()
        )



