import requests
from bs4 import BeautifulSoup
import json

URL = "https://planet4589.org/space/con/star/stats.html"

def parse_stats():
    resp = requests.get(URL, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Ищем все таблицы
    tables = soup.find_all("table")
    target_table = None

    # Ищем таблицу, где есть строка с "Total" в первой ячейке
    for table in tables:
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if not cells:
                continue
            first = cells[0]
            if "Total" in first:
                target_table = table
                break
        if target_table:
            break

    if not target_table:
        # Если не нашли, берём первую большую таблицу
        target_table = tables[0] if tables else None

    if not target_table:
        raise RuntimeError("No table found")

    rows = []
    for tr in target_table.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if not cells:
            continue
        rows.append(cells)

    # Сохраняем всю таблицу
    return {"all_rows": rows}

if __name__ == "__main__":
    data = parse_stats()
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Rows count:", len(data.get("all_rows", [])))
