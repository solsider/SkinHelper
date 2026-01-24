from telebot import types

from services.recommender import pick_by_steps
from keyboards import BUDGETS, step_keyboard, main_menu_keyboard
from storage.db import upsert_profile, get_profile


STEPS_ORDER = ["Очищение", "Актив", "Крем", "SPF"]


def _build_step_text(step_name: str, items: list[dict], step_index: int, total_steps: int) -> str:
    lines = [
        f"🧴 *Умный Уход* — шаг {step_index + 1}/{total_steps}",
        f"— *{step_name}* —",
        "",
    ]
    for i, p in enumerate(items, start=1):
        lines.append(f"{i}) {p['name']}")
        why = p.get("why", "")
        if why:
            lines.append(f"_{why}_")
        lines.append("")
    return "\n".join(lines).strip()


def register(bot, user_data: dict):

    def in_choose_budget(message) -> bool:
        chat_id = message.chat.id
        return (
            chat_id in user_data
            and isinstance(user_data[chat_id], dict)
            and user_data[chat_id].get("state") == "choose_budget"
            and isinstance(message.text, str)
            and message.text.startswith("Бюджет: ")
        )

    @bot.message_handler(func=in_choose_budget)
    def handle_budget(message):
        chat_id = message.chat.id

        profile = get_profile(chat_id)
        if profile:
            user_data[chat_id].update(profile)

        b = message.text.replace("Бюджет: ", "").strip()
        if b not in BUDGETS:
            bot.send_message(chat_id, "Выбери бюджет кнопкой 🙂")
            return

        bot.send_message(
            chat_id,
            "Отлично, подбираю уход 👇",
            reply_markup=types.ReplyKeyboardRemove()
        )


        # сохраняем бюджет
        user_data[chat_id]["budget"] = b
        user_data[chat_id].pop("state", None)
        upsert_profile(chat_id, budget=b)

        # защитная проверка
        if not user_data[chat_id].get("skin_type"):
            bot.send_message(
                chat_id,
                "Сначала выбери тип кожи 🙂\nНажми «🧴 Подобрать уход» или /skin",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return

        is_pro = bool(user_data[chat_id].get("is_pro"))
        per_step = 5 if is_pro else 2

        steps_dict = pick_by_steps(user_data[chat_id], per_step=per_step)

        # Собираем только непустые шаги
        steps = [
            (name, steps_dict.get(name, []))
            for name in STEPS_ORDER
            if steps_dict.get(name)
        ]

        if not steps:
            bot.send_message(
                chat_id,
                "Пока мало подходящих вариантов в базе под твой профиль.\n"
                "Напиши, что важнее: *акне* или *чувствительность/сухость* — и я расширю базу прицельно.",
                parse_mode="Markdown",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return

        # сохраняем pager в state
        user_data[chat_id]["pager"] = {
            "steps": steps,
            "index": 0,
            "message_id": None,
        }

        # отправляем первый шаг
        step_name, items = steps[0]
        text = _build_step_text(step_name, items, 0, len(steps))
        kb = step_keyboard(items, 0, len(steps))

        sent = bot.send_message(
            chat_id,
            text,
            parse_mode="Markdown",
            reply_markup=kb
        )
        user_data[chat_id]["pager"]["message_id"] = sent.message_id
