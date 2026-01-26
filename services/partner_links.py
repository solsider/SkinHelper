import re
import urllib.parse
from config import PARTNER_BASE_URL


def _wrap_with_advcake(target_url: str) -> str:
    sep = "&" if "?" in PARTNER_BASE_URL else "?"
    return PARTNER_BASE_URL + f"{sep}dl=" + urllib.parse.quote(target_url, safe="")


def goldapple_card_url(ga_id: str, slug: str | None = None) -> str:
    ga_id = str(ga_id).strip()
    if slug:
        slug = slug.strip().strip("/")
        return f"https://goldapple.ru/{ga_id}-{slug}"
    return f"https://goldapple.ru/{ga_id}"


def _clean_query(name: str) -> str:
    # убираем "(...)" — это мешает поиску
    s = re.sub(r"\([^)]*\)", "", name).strip()
    s = re.sub(r"\s{2,}", " ", s)
    return s


def goldapple_target_for_product(p: dict) -> str:
    """
    1) Если есть ga_id -> точная карточка товара.
    2) Иначе fallback: поиск по query/name.
    """
    ga_id = p.get("ga_id")
    if ga_id:
        return _wrap_with_advcake(goldapple_card_url(ga_id, p.get("slug")))

    q = p.get("query") or _clean_query(p["name"])
    target = f"https://goldapple.ru/web?q={urllib.parse.quote_plus(q)}&m=1"
    return _wrap_with_advcake(target)
