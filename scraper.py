import requests
from bs4 import BeautifulSoup
import json

URL = "https://planet4589.org/space/con/star/stats.html"

def parse_stats():
    resp = requests.get(URL, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    tables = soup.find_all("table")
    target_table = None
    for table in tables:
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if cells and "Total" in cells[0]:
                target_table = table
                break
        if target_table:
            break

    if not target_table:
        target_table = tables[0] if tables else None

    if not target_table:
        raise RuntimeError("No table found")

    rows = []
    for tr in target_table.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if cells:
            rows.append(cells)
    return rows

def generate_static_html(rows):
    headers = rows[0] if rows else []
    wanted = ['Starlink Gen1', 'Starlink Gen2', 'Starlink Gen3D', 'Starlink Gen3', 'Total']
    filtered = [row for row in rows[1:] if row and row[0] in wanted]

    html = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Starlink Stats</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 1.5rem; }
    table {
      border-collapse: collapse;
      width: 100%;
      max-width: 1200px;
      font-size: 14px;
    }
    th, td {
      border: 1px solid #ccc;
      padding: 6px 10px;
      text-align: right;
      white-space: nowrap;
    }
    th:first-child, td:first-child {
      text-align: left;
      font-weight: 500;
    }
    caption {
      text-align: left;
      font-weight: bold;
      margin-bottom: 0.5rem;
      font-size: 1.2rem;
    }
    .table-wrapper { overflow-x: auto; }
  </style>
</head>
<body>
  <h1>Starlink: итоговые показатели</h1>
  <div class="table-wrapper">
    <table>
      <caption>Сводка по поколениям и общий итог</caption>
      <thead><tr>"""
    for h in headers:
        html += f"<th>{h}</th>"
    html += "</tr></thead><tbody>"
    for row in filtered:
        html += "<tr>"
        for i in range(len(headers)):
            val = row[i] if i < len(row) else ''
            html += f"<td>{val}</td>"
        html += "</tr>"
    html += """</tbody></table>
  </div>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

def generate_json_for_restful(rows):
    # rows[0] - заголовки
    headers = rows[0] if rows else []
    # Какие строки нас интересуют
    wanted = ['Starlink Gen1', 'Starlink Gen2', 'Starlink Gen3D', 'Starlink Gen3', 'Total']
    filtered = [row for row in rows[1:] if row and row[0] in wanted]

    # Преобразуем в список объектов
    result = []
    for row in filtered:
        obj = {}
        for i, header in enumerate(headers):
            if i < len(row):
                obj[header] = row[i]
            else:
                obj[header] = ""
        result.append(obj)

    # Сохраняем как массив объектов
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    rows = parse_stats()
    generate_static_html(rows)   # Для iframe или отдельной страницы
    generate_json_for_restful(rows)  # Для Restful Table

    print("Обновлены index.html и data.json (в формате массива объектов)")
