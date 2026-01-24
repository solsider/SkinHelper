from telebot import types

from keyboards import profile_keyboard, skin_keyboard, problems_keyboard, budget_keyboard, main_menu_keyboard
from storage.db import get_profile, clear_profile


def _profile_text(p: dict) -> str:
    skin = p.get("skin_type") or "—"
    problems = p.get("problems") or set()
    budget = p.get("budget") or "—"
    is_pro = bool(p.get("is_pro"))

    problems_text = "—" if not problems else "\n".join(f"• {x}" for x in sorted(problems))
    pro_text = "✅ PRO" if is_pro else "—"

    return (
        "👤 *Твой профиль*\n\n"
        f"*Тип кожи:* {skin}\n\n"
        f"*Проблемы:*\n{problems_text}\n\n"
        f"*Бюджет:* {budget}\n\n"
        f"*Статус:* {pro_text}"
    )


def show_profile(bot, user_data: dict, chat_id: int):
    profile = get_profile(chat_id)
    if not profile:
        bot.send_message(
            chat_id,
            "У тебя пока нет сохранённого профиля.\n"
            "Давай начнём с подбора 🙂",
            reply_markup=main_menu_keyboard()
        )
        return

    # обновим память (включая is_pro)
    user_data[chat_id] = profile

    bot.send_message(
        chat_id,
        _profile_text(profile),
        parse_mode="Markdown",
        reply_markup=profile_keyboard()
    )


def register(bot, user_data: dict):

    @bot.message_handler(commands=["profile"])
    def profile_cmd(message):
        show_profile(bot, user_data, message.chat.id)

    @bot.callback_query_handler(func=lambda c: (c.data or "").startswith("profile:"))
    def profile_actions(call):
        chat_id = call.message.chat.id
        action = call.data

        # подстрахуемся: если в памяти нет профиля — подтянем из БД
        if chat_id not in user_data:
            p = get_profile(chat_id)
            if p:
                user_data[chat_id] = p
            else:
                bot.answer_callback_query(call.id)
                bot.send_message(chat_id, "Профиль не найден. Нажми «🧴 Подобрать уход».", reply_markup=main_menu_keyboard())
                return

        if action == "profile:skin":
            bot.answer_callback_query(call.id, "Изменяем тип кожи")
            user_data[chat_id]["state"] = "choose_skin"
            bot.send_message(chat_id, "Выбери тип кожи:", reply_markup=skin_keyboard())
            return

        if action == "profile:problems":
            bot.answer_callback_query(call.id, "Изменяем проблемы")
            user_data[chat_id]["state"] = "choose_problems"
            current = user_data.get(chat_id, {}).get("problems", set())
            bot.send_message(chat_id, "Выбери проблемы:", reply_markup=problems_keyboard(current))
            return

        if action == "profile:budget":
            bot.answer_callback_query(call.id, "Изменяем бюджет")
            user_data[chat_id]["state"] = "choose_budget"
            bot.send_message(chat_id, "Выбери бюджет:", reply_markup=budget_keyboard())
            return

        if action == "profile:reset":
            clear_profile(chat_id)
            user_data.pop(chat_id, None)
            bot.answer_callback_query(call.id, "Профиль сброшен")

            bot.send_message(
                chat_id,
                "🗑 Профиль удалён.\n\n"
                "Хочешь начать заново? 🙂",
                reply_markup=main_menu_keyboard()
            )
            return

        bot.answer_callback_query(call.id)
