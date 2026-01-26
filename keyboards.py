import urllib.parse
from telebot import types
from config import PARTNER_BASE_URL

# ======================
# ДАННЫЕ
# ======================

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

# ======================
# REPLY КЛАВИАТУРЫ
# ======================

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


def main_menu_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🧴 Подобрать уход")
    kb.row("👤 Мой профиль", "🔄 Изменить профиль")
    kb.row("💎 PRO", "ℹ️ FAQ")
    return kb


def home_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🏠 Главное меню")
    return kb


# ======================
# GOLD APPLE + ADVCAKE
# ======================

def _goldapple_target_url(query: str) -> str:
    """
    Рабочий вариант GoldApple:
    https://goldapple.ru/web?q=...
    """
    q = urllib.parse.quote_plus(query)
    return f"https://goldapple.ru/web?q={q}&m=1"


def goldapple_search_url(query: str) -> str:
    """
    Оборачиваем GoldApple-ссылку в AdvCake через dl=
    """
    target_url = _goldapple_target_url(query)
    sep = "&" if "?" in PARTNER_BASE_URL else "?"
    return PARTNER_BASE_URL + f"{sep}dl=" + urllib.parse.quote(target_url, safe="")


# ======================
# INLINE КЛАВИАТУРЫ
# ======================

def products_keyboard(products: list[dict]):
    kb = types.InlineKeyboardMarkup()

    for p in products:
        query = p.get("query") or p["name"]
        url = goldapple_search_url(query)

        title = p["name"]
        if len(title) > 35:
            title = title[:32] + "…"

        kb.add(types.InlineKeyboardButton(title, url=url))

    return kb


def step_keyboard(items: list[dict], step_index: int, total_steps: int):
    kb = types.InlineKeyboardMarkup()

    # Товары
    for p in items:
        query = p.get("query") or p["name"]
        url = goldapple_search_url(query)

        title = p["name"]
        if len(title) > 35:
            title = title[:32] + "…"

        kb.add(types.InlineKeyboardButton(title, url=url))

    # Навигация
    prev_btn = types.InlineKeyboardButton("⬅️ Назад", callback_data="nav:prev")
    next_btn = types.InlineKeyboardButton("Дальше ➡️", callback_data="nav:next")

    if step_index <= 0:
        prev_btn = types.InlineKeyboardButton("⬅️", callback_data="nav:none")
    if step_index >= total_steps - 1:
        next_btn = types.InlineKeyboardButton("✅ Готово", callback_data="nav:done")

    kb.row(prev_btn, next_btn)
    kb.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="nav:menu"))
    kb.add(types.InlineKeyboardButton("🔄 Начать заново", callback_data="nav:restart"))

    return kb


def product_link_button(query: str):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            "Открыть в Золотом Яблоке",
            url=goldapple_search_url(query),
        )
    )
    return kb


def profile_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🧴 Изменить тип кожи", callback_data="profile:skin"))
    kb.add(types.InlineKeyboardButton("🎯 Изменить проблемы", callback_data="profile:problems"))
    kb.add(types.InlineKeyboardButton("💰 Изменить бюджет", callback_data="profile:budget"))
    kb.add(types.InlineKeyboardButton("🗑 Сбросить профиль", callback_data="profile:reset"))
    return kb
