import requests
from bs4 import BeautifulSoup
import os

# Конфигурация проектов
PROJECTS = {
    'Starlink': {
        'url': 'https://planet4589.org/space/con/star/stats.html',
        'base_dir': 'Starlink',
        'gen_names': {
            'Starlink Gen1': 'Gen1',
            'Starlink Gen2': 'Gen2',
            'Starlink Gen3D': 'Gen3D',
            'Starlink Gen3': 'Gen3',
            'Total': 'Total'
        }
    },
    'Qianfan': {
        'url': 'https://planet4589.org/space/con/qf/stats.html',
        'base_dir': 'Qianfan',
        'gen_names': {
            'Qianfan Xingzuo': 'Xingzuo',
            'Qianfan DTC': 'DTC',
            'Total': 'Total'
        }
    },
    'Guowang': {
        'url': 'https://planet4589.org/space/con/xw/stats.html',
        'base_dir': 'Guowang',
        'gen_names': {
            'Chinese Xingwang Constellation (as launched)': 'Xingwang',
            'Total Xingwang': 'Total'
        }
    },
    'Kuiper': {
        'url': 'https://planet4589.org/space/con/kp/stats.html',
        'base_dir': 'Kuiper',
        'gen_names': {
            'Amazon Leo (Kuiper) Constellation (2024/25 mods)': 'Kuiper',
            'Total KP': 'Total'
        }
    },
    'OneWeb': {
        'url': 'https://planet4589.org/space/con/ow/stats.html',
        'base_dir': 'OneWeb',
        'gen_names': {
            'OneWeb Constellation (2021 revision, Phase 1)': 'OneWeb',
            'Total OneWeb': 'Total'
        }
    }
}

METRICS = [
    'Total Sats Launched',
    'Total Down',
    'Total Working'
]

METRIC_COLORS = {
    'Total Sats Launched': 'blue',
    'Total Down': 'red',
    'Total Working': 'green'
}

def parse_stats(url):
    """Загружает таблицу и возвращает список строк."""
    resp = requests.get(url, timeout=15)
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

def generate_number_pages(project_name, config, rows):
    """Создаёт папки и HTML-файлы для каждого числа."""
    if not rows:
        return

    headers = rows[0]
    metric_indices = {}
    for metric in METRICS:
        try:
            metric_indices[metric] = get_column_index(headers, metric)
        except ValueError as e:
            print(f"⚠️ {project_name}: {e} — пропускаем")
            return

    wanted_full_names = list(config['gen_names'].keys())
    filtered = []
    for row in rows[1:]:
        if row and row[0] in wanted_full_names:
            filtered.append(row)

    if not filtered:
        print(f"⚠️ {project_name}: не найдены строки для {wanted_full_names}")
        return

    base_dir = config['base_dir']
    for metric in METRICS:
        metric_dir = os.path.join(base_dir, metric)
        os.makedirs(metric_dir, exist_ok=True)

        col_index = metric_indices[metric]
        color = METRIC_COLORS.get(metric, 'black')

        for row in filtered:
            full_name = row[0]
            short_name = config['gen_names'][full_name]
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
      font-size: 14px;
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
      font-weight: bold;
      color: {color};
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

    print(f"✅ {project_name}: созданы страницы для {len(METRICS)} метрик в папке '{base_dir}'")

if __name__ == "__main__":
    for project_name, config in PROJECTS.items():
        print(f"🔄 Обработка {project_name}...")
        try:
            rows = parse_stats(config['url'])
            generate_number_pages(project_name, config, rows)
        except Exception as e:
            print(f"❌ Ошибка при обработке {project_name}: {e}")

    print("✅ Все проекты обработаны.")
