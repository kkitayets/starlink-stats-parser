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

def generate_index_html(rows):
    headers = rows[0] if rows else []
    wanted = ['Starlink Gen1', 'Starlink Gen2', 'Starlink Gen3D', 'Starlink Gen3', 'Total']
    filtered = [row for row in rows[1:] if row and row[0] in wanted]

    # Строим HTML таблицу статически
    html = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <title>Starlink Stats</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 1.5rem; }
    .table-wrapper { overflow-x: auto; }
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
  </style>
</head>
<body>
  <h1>Starlink: итоговые показатели</h1>
  <div class="table-wrapper">
    <table>
      <caption>Сводка по поколениям и общий итог</caption>
      <thead>
        <tr>
"""
    # Заголовки
    for h in headers:
        html += f"          <th>{h}</th>\n"
    html += """        </tr>
      </thead>
      <tbody>
"""
    # Строки
    for row in filtered:
        html += "        <tr>\n"
        for i, cell in enumerate(row):
            # Если ячейка пустая, ставим пробел или пустую строку
            val = cell if cell else ""
            html += f"          <td>{val}</td>\n"
        html += "        </tr>\n"
    html += """      </tbody>
    </table>
  </div>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    rows = parse_stats()
    generate_index_html(rows)
    # Для отладки сохраняем data.json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"all_rows": rows}, f, ensure_ascii=False, indent=2)
    print("Готово.")
