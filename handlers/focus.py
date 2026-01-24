from telebot import types

from services.recommender import pick_by_steps
from storage.db import upsert_profile
from keyboards import step_keyboard, main_menu_keyboard

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

    def in_need_focus(message) -> bool:
        chat_id = message.chat.id
        return (
            chat_id in user_data
            and isinstance(user_data[chat_id], dict)
            and user_data[chat_id].get("state") == "need_focus"
        )

    @bot.message_handler(func=in_need_focus)
    def handle_focus(message):
        chat_id = message.chat.id
        text = (message.text or "").lower()

        user_data.setdefault(chat_id, {})
        problems = user_data[chat_id].setdefault("problems", set())

        matched = False

        if "акне" in text or "высып" in text:
            problems.add("Акне/высыпания")
            matched = True

        if "чувств" in text or "покрас" in text:
            problems.add("Чувствительность")
            problems.add("Покраснение")
            matched = True

        if "сух" in text or "шелуш" in text:
            problems.add("Шелушение/сухость")
            matched = True

        if not matched:
            bot.send_message(
                chat_id,
                "Напиши одним словом, что важнее:\n"
                "• *акне*\n"
                "• *чувствительность*\n"
                "• *сухость*",
                parse_mode="Markdown"
            )
            return

        # сохраняем изменения
        upsert_profile(chat_id, problems=problems)

        # убираем state
        user_data[chat_id].pop("state", None)

        # запускаем подбор заново
        is_pro = bool(user_data[chat_id].get("is_pro"))
        per_step = 5 if is_pro else 2

        steps_dict = pick_by_steps(user_data[chat_id], per_step=per_step)
        steps = [(name, steps_dict.get(name, [])) for name in STEPS_ORDER if steps_dict.get(name)]

        if not steps:
            bot.send_message(
                chat_id,
                "Я расширил подбор, но вариантов всё ещё мало 😕\n"
                "Попробуй уточнить по-другому или начать заново.",
                reply_markup=main_menu_keyboard()
            )
            return

        user_data[chat_id]["pager"] = {
            "steps": steps,
            "index": 0,
            "message_id": None,
        }

        step_name, items = steps[0]
        sent = bot.send_message(
            chat_id,
            _build_step_text(step_name, items, 0, len(steps)),
            parse_mode="Markdown",
            reply_markup=step_keyboard(items, 0, len(steps))
        )
        user_data[chat_id]["pager"]["message_id"] = sent.message_id
