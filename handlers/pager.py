from telebot import types
from keyboards import step_keyboard, main_menu_keyboard




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

    @bot.callback_query_handler(func=lambda call: (call.data or "").startswith("nav:"))
    def nav(call):
        chat_id = call.message.chat.id
        data = call.data

        # если нет состояния — просто уберём "loading"
        if chat_id not in user_data or "pager" not in user_data[chat_id]:
            bot.answer_callback_query(call.id)
            return

        pager = user_data[chat_id]["pager"]
        steps = pager.get("steps", [])
        if not steps:
            bot.answer_callback_query(call.id)
            return

        idx = pager.get("index", 0)

        if data == "nav:none":
            bot.answer_callback_query(call.id)
            return

        if data == "nav:prev":
            idx = max(0, idx - 1)

        elif data == "nav:next":
            idx = min(len(steps) - 1, idx + 1)

        elif data == "nav:done":
            bot.answer_callback_query(call.id, "Готово ✅")

            # ❗ Полный выход из всех состояний
            user_data[chat_id].pop("pager", None)
            user_data[chat_id].pop("state", None)

            bot.send_message(
                chat_id,
                "✅ Подбор завершён. Что делаем дальше?",
                reply_markup=main_menu_keyboard()
            )
            return

        elif data == "nav:menu":
            bot.answer_callback_query(call.id, "Главное меню")
            user_data[chat_id].pop("pager", None)
            user_data[chat_id].pop("state", None)

            bot.send_message(
                chat_id,
                "🏠 Главное меню",
                reply_markup=main_menu_keyboard()
            )
            return

        elif data == "nav:restart":
            bot.answer_callback_query(call.id, "Ок, начнём заново")
            user_data[chat_id].pop("pager", None)

            # можно сразу отправить выбор типа кожи, а можно меню
            bot.send_message(
                chat_id,
                "Ок 🙂 Выбери действие:",
                reply_markup=main_menu_keyboard()
            )
            return

        pager["index"] = idx

        step_name, items = steps[idx]
        text = _build_step_text(step_name, items, idx, len(steps))
        kb = step_keyboard(items, idx, len(steps))

        # редактируем одно и то же сообщение
        try:
            bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=call.message.message_id,
                parse_mode="Markdown",
                reply_markup=kb
            )
        except Exception:
            # если редактирование не удалось (редко), просто отправим новое
            bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)

        bot.answer_callback_query(call.id)
