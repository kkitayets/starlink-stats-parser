import requests
from bs4 import BeautifulSoup
import os

URL = "https://planet4589.org/space/con/star/stats.html"

GEN_NAMES = {
    'Starlink Gen1': 'Gen1',
    'Starlink Gen2': 'Gen2',
    'Starlink Gen3D': 'Gen3D',
    'Starlink Gen3': 'Gen3',
    'Total': 'Total'
}

METRICS = [
    'Total Sats Launched',
    'Total Down',
    'Total Working'
]

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

def get_column_index(headers, name):
    for i, h in enumerate(headers):
        if h.strip() == name:
            return i
    raise ValueError(f"Столбец '{name}' не найден")

def generate_number_pages(rows):
    if not rows:
        return

    headers = rows[0]
    metric_indices = {}
    for metric in METRICS:
        metric_indices[metric] = get_column_index(headers, metric)

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

if __name__ == "__main__":
    rows = parse_stats()
    generate_number_pages(rows)
    print("✅ Готово.")
