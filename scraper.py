import requests
from bs4 import BeautifulSoup
import json

URL = "https://planet4589.org/space/con/star/stats.html"

def parse_stats():
    resp = requests.get(URL, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table")
    if not table:
        raise RuntimeError("Table not found")

    rows = []
    for tr in table.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if not cells:
            continue
        rows.append(cells)

    # Ищем строки, где первый столбец содержит Total или Subtotal
    result = {}
    for row in rows:
        if not row:
            continue
        first = row[0]
        if "Total" in first or "Subtotal" in first:
            result[first] = row

    return result

if __name__ == "__main__":
    data = parse_stats()
    # Сохраняем в JSON
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Parsed rows:", list(data.keys()))
