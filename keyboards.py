import urllib.parse
from telebot import types

SKIN_TYPES = ["Сухая", "Жирная", "Комбинированная", "Нормальная", "Чувствительная"]

PROBLEMS = [
    "Акне/высыпания",
    "Черные точки",
    "Покраснение",
    "Шелушение/сухость",
    "Чувствительность",
    "Пигментация",
    "Расширенные поры",
    "Тусклый тон",
]

BUDGETS = ["низкий", "средний", "премиум"]


def skin_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(*SKIN_TYPES)
    return kb


def problems_keyboard(selected: set[str]):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    row = []
    for p in PROBLEMS:
        label = f"✅ {p}" if p in selected else p
        row.append(label)
        if len(row) == 2:
            kb.row(*row)
            row = []
    if row:
        kb.row(*row)

    kb.row("Готово ✅", "Сбросить ↩️")
    return kb


def budget_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Бюджет: низкий", "Бюджет: средний")
    kb.row("Бюджет: премиум")
    return kb


def goldapple_search_url(query: str) -> str:
    q = urllib.parse.quote(query)
    return f"https://goldapple.ru/search?text={q}"


def product_link_button(url: str | None = None, query: str | None = None):
    """
    Если есть url — откроем его. Иначе откроем поиск по GoldApple.
    """
    kb = types.InlineKeyboardMarkup()
    link = url if url else goldapple_search_url(query or "")
    kb.add(types.InlineKeyboardButton("Открыть в Золотом Яблоке", url=link))
    return kb


def products_keyboard(products: list[dict]):
    """
    Inline-клавиатура из списка товаров.
    Каждая кнопка ведёт на url или поиск.
    """
    kb = types.InlineKeyboardMarkup()
    for p in products:
        url = p.get("url") or goldapple_search_url(p.get("query") or p["name"])
        title = p["name"]
        if len(title) > 35:
            title = title[:32] + "…"
        kb.add(types.InlineKeyboardButton(title, url=url))
    return kb


def step_keyboard(items: list[dict], step_index: int, total_steps: int):
    """
    Пошаговый режим:
    - кнопки товаров
    - навигация prev/next/done
    - главное меню
    - restart
    """
    kb = types.InlineKeyboardMarkup()

    # Кнопки товаров
    for p in items:
        url = p.get("url") or goldapple_search_url(p.get("query") or p["name"])
        title = p["name"]
        if len(title) > 35:
            title = title[:32] + "…"
        kb.add(types.InlineKeyboardButton(title, url=url))

    prev_btn = types.InlineKeyboardButton("⬅️ Назад", callback_data="nav:prev")
    next_btn = types.InlineKeyboardButton("Дальше ➡️", callback_data="nav:next")
    restart_btn = types.InlineKeyboardButton("🔄 Начать заново", callback_data="nav:restart")

    if step_index <= 0:
        prev_btn = types.InlineKeyboardButton("⬅️", callback_data="nav:none")

    if step_index >= total_steps - 1:
        next_btn = types.InlineKeyboardButton("✅ Готово", callback_data="nav:done")

    kb.row(prev_btn, next_btn)
    kb.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="nav:menu"))
    kb.add(restart_btn)
    return kb


def profile_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🧴 Изменить тип кожи", callback_data="profile:skin"))
    kb.add(types.InlineKeyboardButton("🎯 Изменить проблемы", callback_data="profile:problems"))
    kb.add(types.InlineKeyboardButton("💰 Изменить бюджет", callback_data="profile:budget"))
    kb.add(types.InlineKeyboardButton("🗑 Сбросить профиль", callback_data="profile:reset"))
    return kb


def main_menu_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🧴 Подобрать уход")
    kb.row("👤 Мой профиль", "🔄 Изменить профиль")
    kb.row("💎 PRO")   # ← ОБЯЗАТЕЛЬНО
    kb.row("ℹ️ О боте")
    return kb



def home_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🏠 Главное меню")
    return kb
