from keyboards import main_menu_keyboard
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
            "🧴 Умный Уход — персональный подбор ухода за кожей\n\n"
            "Я подбираю косметику по типу кожи, задачам и бюджету — логично и по шагам.\n\n"
            "Что я учитываю:\n"
            "• тип кожи\n"  
            "• проблемы и задачи\n"  
            "• бюджет\n"
            "• этапы ухода: очищение · активы · крем · SPF\n\n"
            "Начнём с типа кожи 👇",
            reply_markup=main_menu_keyboard()
        )


    @bot.message_handler(func=lambda m: m.text == "🏠 Главное меню")
    def back_to_menu(message):
        bot.send_message(
            message.chat.id,
            "🏠 Главное меню",
            reply_markup=main_menu_keyboard()
        )
