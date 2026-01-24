from telebot import types

from keyboards import (
    skin_keyboard,
    main_menu_keyboard,
    problems_keyboard,
    budget_keyboard,
)
from handlers.profile import show_profile as show_profile_func
from storage.db import upsert_profile


def register(bot, user_data: dict):

    @bot.message_handler(func=lambda m: m.text == "🧴 Подобрать уход")
    def start_flow(message):
        chat_id = message.chat.id
        bot.send_message(
            chat_id,
            "Давай подберём уход 🙂\n\nВыбери тип кожи:",
            reply_markup=skin_keyboard()
        )

    @bot.message_handler(func=lambda m: m.text == "👤 Мой профиль")
    def show_profile(message):
        show_profile_func(bot, user_data, message.chat.id)

    @bot.message_handler(func=lambda m: m.text == "🔄 Изменить профиль")
    def edit_profile(message):
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row("🧴 Тип кожи", "🎯 Проблемы")
        kb.row("💰 Бюджет")
        kb.row("🏠 Главное меню")
        bot.send_message(message.chat.id, "Что хочешь изменить?", reply_markup=kb)

    # --- Обработчики пунктов "Изменить профиль" ---

    @bot.message_handler(func=lambda m: m.text == "🧴 Тип кожи")
    def edit_skin(message):
        chat_id = message.chat.id
        user_data.setdefault(chat_id, {})
        bot.send_message(chat_id, "Выбери тип кожи:", reply_markup=skin_keyboard())

    @bot.message_handler(func=lambda m: m.text == "🎯 Проблемы")
    def edit_problems(message):
        chat_id = message.chat.id
        user_data.setdefault(chat_id, {})
        user_data[chat_id]["state"] = "choose_problems"

        current = user_data.get(chat_id, {}).get("problems", set())
        bot.send_message(chat_id, "Выбери проблемы:", reply_markup=problems_keyboard(current))

    @bot.message_handler(func=lambda m: m.text == "💰 Бюджет")
    def edit_budget(message):
        chat_id = message.chat.id
        user_data.setdefault(chat_id, {})
        user_data[chat_id]["state"] = "choose_budget"
        bot.send_message(chat_id, "Выбери бюджет:", reply_markup=budget_keyboard())

    # --- PRO ---

    @bot.message_handler(func=lambda m: m.text == "💎 PRO")
    def pro_screen(message):
        chat_id = message.chat.id
        user_data.setdefault(chat_id, {})

        if bool(user_data[chat_id].get("is_pro")):
            bot.send_message(
                chat_id,
                "💎 У тебя уже активен *PRO* ✅",
                parse_mode="Markdown",
                reply_markup=main_menu_keyboard()
            )
            return

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🎁 Включить PRO-тест", callback_data="pro:trial"))

        bot.send_message(
            chat_id,
            "💎 *PRO-режим*\n\n"
            "Что даёт PRO:\n"
            "• больше вариантов на каждом шаге ухода\n"
            "• более точный подбор под твой профиль\n\n"
            "Хочешь включить тест? 👇",
            parse_mode="Markdown",
            reply_markup=kb
        )

    @bot.callback_query_handler(func=lambda c: (c.data or "") == "pro:trial")
    def pro_trial(call):
        chat_id = call.message.chat.id

        user_data.setdefault(chat_id, {})
        user_data[chat_id]["is_pro"] = True
        upsert_profile(chat_id, is_pro=True)

        bot.answer_callback_query(call.id, "PRO включён ✅")
        bot.send_message(
            chat_id,
            "✅ PRO активирован!\n\nТеперь подбор будет давать больше вариантов на шаг 👇",
            reply_markup=main_menu_keyboard()
        )

    # --- О боте ---

    @bot.message_handler(func=lambda m: m.text == "ℹ️ О боте")
    def about(message):
        bot.send_message(
            message.chat.id,
            "ℹ️ *Умный Уход*\n\n"
            "Я помогаю подобрать уходовые средства по типу кожи, проблемам и бюджету.\n\n"
            "⚠️ Я не заменяю консультацию дерматолога.",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
