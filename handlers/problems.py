from telebot import types

from keyboards import PROBLEMS, problems_keyboard, budget_keyboard
from storage.db import upsert_profile


def register(bot, user_data: dict):

    def in_choose_problems(message) -> bool:
        chat_id = message.chat.id
        return (
            chat_id in user_data
            and isinstance(user_data[chat_id], dict)
            and user_data[chat_id].get("state") == "choose_problems"
        )

    @bot.message_handler(func=in_choose_problems)
    def router(message):
        chat_id = message.chat.id
        text = (message.text or "").strip()

        # Сброс
        if text == "Сбросить ↩️":
            user_data[chat_id]["problems"] = set()

            # ✅ сохраняем в БД только по сбросу
            upsert_profile(chat_id, problems=set())

            bot.send_message(
                chat_id,
                "Ок, сбросил. Выбирай заново 👇",
                reply_markup=problems_keyboard(user_data[chat_id]["problems"])
            )
            return

        # Готово -> бюджет
        if text == "Готово ✅":
            if not user_data[chat_id]["problems"]:
                bot.send_message(
                    chat_id,
                    "Выбери хотя бы одну проблему 🙂",
                    reply_markup=problems_keyboard(user_data[chat_id]["problems"])
                )
                return

            # ✅ сохраняем в БД только по готово
            upsert_profile(chat_id, problems=user_data[chat_id]["problems"])

            user_data[chat_id]["state"] = "choose_budget"

            bot.send_message(chat_id, "✅ Принято! Теперь выберем бюджет 👇", reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(chat_id, "Какой бюджет рассматриваем?", reply_markup=budget_keyboard())
            return

        # toggle проблемы (БЕЗ сохранения в БД и БЕЗ лишних сообщений)
        normalized = text.replace("✅ ", "")
        if normalized in PROBLEMS:
            s = user_data[chat_id]["problems"]

            if normalized in s:
                s.remove(normalized)
            else:
                s.add(normalized)

            # ✅ просто обновляем клавиатуру в одном сообщении
            bot.send_message(
                chat_id,
                "Выбери проблемы:",
                reply_markup=problems_keyboard(s)
            )
            return

        return
