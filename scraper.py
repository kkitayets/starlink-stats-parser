import requests
from bs4 import BeautifulSoup
import json
import os
import re

URL = "https://planet4589.org/space/con/star/stats.html"

# Соответствие полных названий поколений → короткие имена файлов
GEN_NAMES = {
    'Starlink Gen1': 'Gen1',
    'Starlink Gen2': 'Gen2',
    'Starlink Gen3D': 'Gen3D',
    'Starlink Gen3': 'Gen3',
    'Total': 'Total'
}

# Интересующие нас метрики (названия столбцов в таблице)
METRICS = [
    'Total Sats Launched',
    'Total Down',
    'Total Working'
]

def parse_stats():
    """Загружает таблицу и возвращает список строк."""
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

def get_column_index(headers, name):
    """Возвращает индекс столбца по его названию."""
    for i, h in enumerate(headers):
        if h.strip() == name:
            return i
    raise ValueError(f"Столбец '{name}' не найден")

def generate_number_pages(rows):
    """
    Создаёт папки и HTML-файлы для каждого числа.
    Число отображается в левом верхнем углу без отступов.
    """
    if not rows:
        return

    headers = rows[0]
    # Находим индексы нужных метрик
    metric_indices = {}
    for metric in METRICS:
        metric_indices[metric] = get_column_index(headers, metric)

    # Отбираем только итоговые строки
    wanted_full_names = list(GEN_NAMES.keys())
    filtered = []
    for row in rows[1:]:
        if row and row[0] in wanted_full_names:
            filtered.append(row)

    base_dir = "Starlink"
    for metric in METRICS:
        metric_dir = os.path.join(base_dir, metric)
        os.makedirs(metric_dir, exist_ok=True)

        col_index = metric_indices[metric]
        for row in filtered:
            full_name = row[0]
            short_name = GEN_NAMES[full_name]
            value = row[col_index] if col_index < len(row) else '0'

            # HTML с числом в левом верхнем углу
            html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{short_name} {metric}</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      font-size: 10rem;
      font-family: system-ui, sans-serif;
      background: white;
      line-height: 1;
    }}
    /* Убираем любые возможные отступы */
    html, body {{
      width: 100%;
      height: 100%;
    }}
    .number {{
      display: inline-block;
      padding: 10px;
    }}
  </style>
</head>
<body>
  <div class="number">{value}</div>
</body>
</html>"""

            file_path = os.path.join(metric_dir, f"{short_name}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)

    print(f"✅ Созданы страницы для {len(METRICS)} метрик в папке '{base_dir}'")

def generate_static_html(rows):
    """(Опционально) создаёт index.html с общей таблицей для обзора."""
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
    table { border-collapse: collapse; width: 100%; max-width: 1200px; font-size: 14px; }
    th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: right; white-space: nowrap; }
    th:first-child, td:first-child { text-align: left; font-weight: 500; }
    caption { text-align: left; font-weight: bold; margin-bottom: 0.5rem; font-size: 1.2rem; }
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
        for i, h in enumerate(headers):
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
    """(Опционально) сохраняет data.json в формате массива объектов."""
    if not rows:
        return
    headers = rows[0]
    wanted = ['Starlink Gen1', 'Starlink Gen2', 'Starlink Gen3D', 'Starlink Gen3', 'Total']
    filtered = [row for row in rows[1:] if row and row[0] in wanted]

    objects = []
    for row in filtered:
        obj = {}
        for i, header in enumerate(headers):
            value = row[i] if i < len(row) else ''
            obj[header] = value
        objects.append(obj)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(objects, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    rows = parse_stats()
    generate_number_pages(rows)      # ← новые отдельные страницы с числами
    generate_static_html(rows)       # (оставляем для удобства)
    generate_json_for_restful(rows)  # (оставляем на всякий случай)

    print("✅ Все страницы обновлены.")
