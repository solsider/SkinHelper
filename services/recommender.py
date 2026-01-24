# services/recommender.py

from data.products import PRODUCTS
from data.brands import POPULAR_BRANDS

STEPS_ORDER = ["Очищение", "Актив", "Крем", "SPF"]


def budget_rank(b: str) -> int:
    return {"низкий": 0, "средний": 1, "премиум": 2}.get(b, 1)


def _product_steps(p: dict) -> list[str]:
    # поддержка и "steps" (список), и "step" (строка)
    if isinstance(p.get("steps"), list):
        return p["steps"]
    if isinstance(p.get("step"), str):
        return [p["step"]]
    return []


def _skin_ok(p: dict, skin: str | None) -> bool:
    if not skin:
        return True
    skins = p.get("skin", [])
    if not isinstance(skins, list) or not skins:
        return True
    return ("Все" in skins) or (skin in skins)


def _budget_ok(p: dict, user_budget: str) -> bool:
    user_r = budget_rank(user_budget)
    pb = p.get("budget")

    # если список бюджетов (как у тебя в products.py)
    if isinstance(pb, list):
        return any(budget_rank(x) <= user_r for x in pb if isinstance(x, str))

    # если строка
    if isinstance(pb, str):
        return budget_rank(pb) <= user_r

    # если бюджета нет — считаем, что подходит
    return True


def score_product(
    p: dict,
    step: str,
    skin: str | None,
    problems: set[str],
    user_budget: str,
    require_problems: bool,
    require_budget: bool,
) -> int:
    # шаг и кожа всегда обязательны
    if step not in _product_steps(p):
        return -10_000
    if not _skin_ok(p, skin):
        return -10_000

    # бюджет — обязателен только в строгом проходе
    if require_budget and not _budget_ok(p, user_budget):
        return -10_000

    score = 1

    # совпадения проблем (если их нужно учитывать)
    if require_problems and problems:
        p_probs = set(p.get("problems", []) or [])
        matched = 0
        for pr in problems:
            if pr in p_probs:
                matched += 1
                score += 3

        # если в строгом проходе ни одной проблемы не совпало — отсекаем
        if matched == 0:
            return -10_000

    # базовые шаги важнее
    if step in ("Очищение", "Крем", "SPF"):
        score += 2

    # популярные бренды чуть выше
    if p.get("brand") in POPULAR_BRANDS:
        score += 1

    # если бюджет НЕ обязателен (мягкий проход), всё равно слегка штрафуем "дороже"
    # чтобы недорогие выходили выше
    if not require_budget:
        pb = p.get("budget")
        # возьмём минимальный бюджет товара
        if isinstance(pb, list) and pb:
            min_rank = min(budget_rank(x) for x in pb if isinstance(x, str))
        elif isinstance(pb, str):
            min_rank = budget_rank(pb)
        else:
            min_rank = budget_rank("средний")

        # чем дороже — тем ниже
        score -= max(0, min_rank - budget_rank(user_budget))

    return score


def pick_by_steps(profile: dict, per_step: int = 2) -> dict[str, list[dict]]:
    skin = profile.get("skin_type")
    problems = set(profile.get("problems") or set())
    user_budget = profile.get("budget") or "средний"

    result: dict[str, list[dict]] = {}

    # 4 прохода: от строгого к мягкому
    passes = [
        (True, True),     # проблемы + бюджет
        (False, True),    # игнорируем проблемы, держим бюджет
        (True, False),    # держим проблемы, игнорируем бюджет
        (False, False),   # игнорируем и проблемы и бюджет
    ]

    for step in STEPS_ORDER:
        chosen: list[dict] = []

        for require_problems, require_budget in passes:
            scored: list[tuple[int, dict]] = []

            for p in PRODUCTS:
                s = score_product(
                    p=p,
                    step=step,
                    skin=skin,
                    problems=problems,
                    user_budget=user_budget,
                    require_problems=require_problems,
                    require_budget=require_budget,
                )
                if s > -10_000:
                    scored.append((s, p))

            scored.sort(key=lambda x: x[0], reverse=True)

            for _, prod in scored:
                if prod not in chosen:
                    chosen.append(prod)
                if len(chosen) >= per_step:
                    break

            if len(chosen) >= per_step:
                break

        result[step] = chosen[:per_step]

    return result
