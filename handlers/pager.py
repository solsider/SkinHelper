from telebot import types
from keyboards import step_keyboard, main_menu_keyboard

MAX_LEN = 3800  # запас до лимита Telegram 4096


def _build_step_text(step_name: str, items: list[dict], step_index: int, total_steps: int) -> str:
    lines = [
        f"🧴 *Умный Уход* — шаг {step_index + 1}/{total_steps}",
        f"— *{step_name}* —",
        "",
    ]
    for i, p in enumerate(items, start=1):
        name = p.get("name", "—")
        lines.append(f"{i}) {name}")

        why = (p.get("why") or "").strip()
        if why:
            # коротко, чтобы не улететь за лимит
            if len(why) > 180:
                why = why[:177] + "…"
            lines.append(f"_{why}_")
        lines.append("")

    text = "\n".join(lines).strip()
    if len(text) > MAX_LEN:
        text = text[:MAX_LEN - 1] + "…"
    return text


def register(bot, user_data: dict):

    @bot.callback_query_handler(func=lambda call: (call.data or "").startswith("nav:"))
    def nav(call):
        chat_id = call.message.chat.id
        data = call.data or ""

        # быстро убираем "часики"
        bot.answer_callback_query(call.id)

        # нет состояния — нечего листать
        if chat_id not in user_data or "pager" not in user_data[chat_id]:
            return

        pager = user_data[chat_id]["pager"]
        steps = pager.get("steps") or []
        if not steps:
            return

        idx = int(pager.get("index", 0))

        if data == "nav:none":
            return

        if data == "nav:prev":
            idx = max(0, idx - 1)

        elif data == "nav:next":
            idx = min(len(steps) - 1, idx + 1)

        elif data == "nav:done":
            user_data[chat_id].pop("pager", None)
            bot.send_message(
                chat_id,
                "✅ Подбор завершён. Что делаем дальше?",
                reply_markup=main_menu_keyboard()
            )
            return

        elif data == "nav:menu":
            user_data[chat_id].pop("pager", None)
            bot.send_message(
                chat_id,
                "🏠 Главное меню",
                reply_markup=main_menu_keyboard()
            )
            return

        elif data == "nav:restart":
            user_data[chat_id].pop("pager", None)
            bot.send_message(
                chat_id,
                "Давай заново 🙂 Нажми «🧴 Подобрать уход»",
                reply_markup=main_menu_keyboard()
            )
            return

        pager["index"] = idx

        step_name, items = steps[idx]
        text = _build_step_text(step_name, items, idx, len(steps))
        kb = step_keyboard(items, idx, len(steps))

        # ВАЖНО: редактируем именно то сообщение, где нажали кнопку
        msg_id = call.message.message_id

        try:
            bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=msg_id,
                parse_mode="Markdown",
                reply_markup=kb
            )
            pager["message_id"] = msg_id

        except Exception:
            # если редактировать нельзя — отправляем новое сообщение
            sent = bot.send_message(
                chat_id,
                text,
                parse_mode="Markdown",
                reply_markup=kb
            )
            pager["message_id"] = sent.message_id

            # и отключаем кнопки у старого, чтобы не кликали "мертвое"
            try:
                bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id, reply_markup=None)
            except Exception:
                pass
