import re
import urllib.parse
from config import PARTNER_BASE_URL


def _wrap_with_advcake(target_url: str) -> str:
    """
    Надёжно добавляет dl= в партнёрскую ссылку:
    - если dl уже был в PARTNER_BASE_URL -> удаляем/перезаписываем
    - гарантируем ровно один dl
    """
    base = PARTNER_BASE_URL.strip()

    parts = urllib.parse.urlsplit(base)
    qs = urllib.parse.parse_qs(parts.query, keep_blank_values=True)

    # Удаляем существующий dl, если он уже был (частая причина редиректа на главную)
    qs.pop("dl", None)

    # Вставляем правильный dl (один!)
    qs["dl"] = [target_url]

    new_query = urllib.parse.urlencode(qs, doseq=True)
    rebuilt = urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
    return rebuilt


def goldapple_card_url(ga_id: str, slug: str | None = None) -> str:
    ga_id = str(ga_id).strip()
    if slug:
        slug = slug.strip().strip("/")
        return f"https://goldapple.ru/{ga_id}-{slug}"
    return f"https://goldapple.ru/{ga_id}"


def _clean_query(name: str) -> str:
    s = re.sub(r"\([^)]*\)", "", name).strip()
    s = re.sub(r"\s{2,}", " ", s)
    return s


def goldapple_target_for_product(p: dict) -> str:
    ga_id = p.get("ga_id")
    if ga_id:
        return _wrap_with_advcake(goldapple_card_url(ga_id, p.get("slug")))

    q = p.get("query") or _clean_query(p["name"])
    target = f"https://goldapple.ru/web?q={urllib.parse.quote_plus(q)}&m=1"
    return _wrap_with_advcake(target)


def goldapple_search_url(query: str) -> str:
    q = urllib.parse.quote_plus(query)
    target = f"https://goldapple.ru/web?q={q}&m=1"
    return _wrap_with_advcake(target)


def product_query(p: dict) -> str:
    return p.get("query") or _clean_query(p["name"])
