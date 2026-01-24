from data.products import PRODUCTS
from data.brands import POPULAR_BRANDS

STEPS_ORDER = ["Очищение", "Актив", "Крем", "SPF"]


def budget_rank(b: str) -> int:
    return {"низкий": 0, "средний": 1, "премиум": 2}.get(b, 1)


def _budget_ok(p: dict, user_budget: str) -> bool:
    return budget_rank(p.get("budget", "средний")) <= budget_rank(user_budget)


def _skin_ok(p: dict, skin: str | None) -> bool:
    skins = p.get("skin", ["Все"])
    if not skin:
        return True
    return ("Все" in skins) or (skin in skins)


def _pro_ok(p: dict, is_pro: bool) -> bool:
    if p.get("pro_only"):
        return is_pro
    return True


def score_product(p: dict, step: str, skin: str | None, problems: set[str], user_budget: str, is_pro: bool,
                  strict_problems: bool) -> int:
    if p.get("step") != step:
        return -10_000
    if not _skin_ok(p, skin):
        return -10_000
    if not _budget_ok(p, user_budget):
        return -10_000
    if not _pro_ok(p, is_pro):
        return -10_000

    score = 1

    # совпадение проблем (если strict_problems=True — требуем хотя бы одно совпадение)
    p_probs = set(p.get("problems", []) or [])
    matches = 0
    for pr in problems:
        if pr in p_probs:
            matches += 1
            score += 3

    if strict_problems and problems and matches == 0:
        return -10_000

    # базовые шаги важнее
    if step in ("Очищение", "Крем", "SPF"):
        score += 2

    # популярные бренды чуть выше
    if p.get("brand") in POPULAR_BRANDS:
        score += 1

    return score


def pick_by_steps(profile: dict, per_step: int = 2) -> dict[str, list[dict]]:
    skin = profile.get("skin_type")
    problems = set(profile.get("problems") or set())
    user_budget = profile.get("budget") or "средний"
    is_pro = bool(profile.get("is_pro"))

    result: dict[str, list[dict]] = {}

    for step in STEPS_ORDER:
        # 1) строгий проход: хотим совпадение по проблемам (если проблемы выбраны)
        strict = []
        for p in PRODUCTS:
            s = score_product(p, step, skin, problems, user_budget, is_pro, strict_problems=True)
            if s > -10_000:
                strict.append((s, p))
        strict.sort(key=lambda x: x[0], reverse=True)

        chosen = [p for _, p in strict[:per_step]]

        # 2) fallback: если мало — добираем по типу кожи/бюджету даже без совпадения проблем
        if len(chosen) < per_step:
            loose = []
            for p in PRODUCTS:
                s = score_product(p, step, skin, problems, user_budget, is_pro, strict_problems=False)
                if s > -10_000:
                    loose.append((s, p))
            loose.sort(key=lambda x: x[0], reverse=True)
            for _, p in loose:
                if p not in chosen:
                    chosen.append(p)
                if len(chosen) >= per_step:
                    break

        result[step] = chosen[:per_step]

    return result
