from telebot import types
from services.partner_links import goldapple_target_for_product


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
    kb.row("ℹ️ FAQ")
    return kb


def home_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🏠 Главное меню")
    return kb


# ======================
# GOLD APPLE + ADVCAKE
# ======================

def _goldapple_search_web_url(query: str) -> str:
    """
    Поиск в GoldApple (fallback).
    """
    q = urllib.parse.quote_plus(query)
    return f"https://goldapple.ru/web?q={q}&m=1"


def _wrap_with_advcake(target_url: str) -> str:
    """
    Оборачиваем любую целевую ссылку в AdvCake через dl=
    """
    sep = "&" if "?" in PARTNER_BASE_URL else "?"
    return PARTNER_BASE_URL + f"{sep}dl=" + urllib.parse.quote(target_url, safe="")


def goldapple_link(query: str | None = None, target_url: str | None = None) -> str:
    """
    Универсально:
    - если передан target_url (карточка товара) -> открываем ТОЧНО товар
    - иначе делаем поиск по query
    """
    if target_url:
        # если вдруг передали относительный путь — превращаем в абсолютный
        if target_url.startswith("/"):
            target_url = "https://goldapple.ru" + target_url
        return _wrap_with_advcake(target_url)

    if not query:
        raise ValueError("goldapple_link: нужен query или target_url")

    return _wrap_with_advcake(_goldapple_search_web_url(query))


# ======================
# INLINE КЛАВИАТУРЫ
# ======================

def _product_title(name: str, limit: int = 35) -> str:
    if len(name) > limit:
        return name[: limit - 3] + "…"
    return name


def products_keyboard(products: list[dict]):
    kb = types.InlineKeyboardMarkup()

    for p in products:
        final = goldapple_target_for_product(p)
        kb.add(types.InlineKeyboardButton(_product_title(p["name"]), url=final))

    return kb



def step_keyboard(items: list[dict], step_index: int, total_steps: int):
    kb = types.InlineKeyboardMarkup()

    for p in items:
        final = goldapple_target_for_product(p)
        kb.add(types.InlineKeyboardButton(_product_title(p["name"]), url=final))

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



def product_link_button(product: dict):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Открыть в Золотом Яблоке", url=goldapple_target_for_product(product)))
    return kb



def profile_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🧴 Изменить тип кожи", callback_data="profile:skin"))
    kb.add(types.InlineKeyboardButton("🎯 Изменить проблемы", callback_data="profile:problems"))
    kb.add(types.InlineKeyboardButton("💰 Изменить бюджет", callback_data="profile:budget"))
    kb.add(types.InlineKeyboardButton("🗑 Сбросить профиль", callback_data="profile:reset"))
    return kb
