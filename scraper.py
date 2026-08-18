import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://planet4589.org/space/con/star/stats.html"

def parse_stats():
    resp = requests.get(URL, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Поиск нужной таблицы (как раньше)
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

    return rows  # возвращаем все строки

def generate_index_html(rows):
    # Заголовки – первая строка
    headers = rows[0] if rows else []

    # Список названий итоговых строк, которые показываем
    wanted = ['Starlink Gen1', 'Starlink Gen2', 'Starlink Gen3D', 'Starlink Gen3', 'Total']
    filtered = [row for row in rows[1:] if row and row[0] in wanted]

    # Подготавливаем данные для вставки в JS
    data_json = json.dumps({
        "headers": headers,
        "rows": filtered
    }, ensure_ascii=False)

    # Шаблон HTML
    html_template = """<!DOCTYPE html>
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
  <div id="stats"></div>

  <script>
    // Данные встроены прямо в скрипт (без fetch)
    const data = DATA_PLACEHOLDER;

    const container = document.getElementById('stats');
    if (!data || !data.rows || data.rows.length === 0) {
      container.textContent = 'Нет данных';
    } else {
      let html = '<div class="table-wrapper"><table>';
      html += '<caption>Сводка по поколениям и общий итог</caption>';
      html += '<thead><tr>';
      for (let h of data.headers) {
        html += '<th>' + (h || '') + '</th>';
      }
      html += '</tr></thead><tbody>';

      for (let row of data.rows) {
        html += '<tr>';
        for (let i = 0; i < data.headers.length; i++) {
          const val = (row[i] !== undefined && row[i] !== '') ? row[i] : '';
          html += '<td>' + val + '</td>';
        }
        html += '</tr>';
      }
      html += '</tbody></table></div>';
      container.innerHTML = html;
    }
  </script>
</body>
</html>"""

    # Заменяем плейсхолдер на реальные данные
    final_html = html_template.replace('DATA_PLACEHOLDER', data_json)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    rows = parse_stats()
    generate_index_html(rows)

    # (Опционально) сохраняем сырые данные в data.json для отладки
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"all_rows": rows}, f, ensure_ascii=False, indent=2)

    print("Готово. index.html обновлён.")
