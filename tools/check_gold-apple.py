import re
import time
import requests
from bs4 import BeautifulSoup

from skin_bot.data.products import PRODUCTS

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def clean_query(name: str) -> str:
    name = re.sub(r"\([^)]*\)", "", name)
    return re.sub(r"\s{2,}", " ", name).strip()

def find_product(query: str):
    url = "https://goldapple.ru/search?text=" + requests.utils.quote(query)
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        m = re.search(r"/(\d{8,})", href)
        if m:
            return m.group(1)

    return None

def main():
    found = 0
    for p in PRODUCTS:
        if p.get("deeplink_ok"):
            continue

        q = p.get("query") or clean_query(p["name"])
        ga_id = find_product(q)

        if ga_id:
            p["ga_id"] = ga_id
            p["deeplink_ok"] = True
            found += 1
            print("✔ FOUND:", p["name"], ga_id)
        else:
            print("✖ NOT FOUND:", p["name"])

        time.sleep(1.5)  # чтобы не словить бан

    print("Total deeplink_ok:", found)

if __name__ == "__main__":
    main()
