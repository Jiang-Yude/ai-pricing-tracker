"""
build_json.py
合併 raw_models.json 輸出最終 data/models.json
同時從 OpenRouter API 抓取模型簡介（description 欄位）
"""
import csv
import json
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

TW = timezone(timedelta(hours=8))


def fetch_descriptions():
    """從 OpenRouter API 取得模型 description"""
    url = "https://openrouter.ai/api/v1/models"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        return {m['id']: m.get('description', '') for m in data.get('data', [])}
    except Exception as e:
        print(f"  [WARN] Could not fetch descriptions: {e}")
        return {}


def main():
    raw_path = Path('data/raw_models.json')
    if not raw_path.exists():
        print("[ERROR] data/raw_models.json not found")
        return

    raw = json.loads(raw_path.read_text())

    print("Fetching model descriptions from OpenRouter...")
    descs = fetch_descriptions()

    now_tw = datetime.now(TW)
    updated_at = now_tw.strftime('%Y-%m-%d %H:%M')

    # 注入 description
    for v in raw['vendors']:
        for m in v['models']:
            m['description'] = descs.get(m['id'], '')

    for m in raw.get('free_models', []):
        m['description'] = descs.get(m['id'], '')

    output = {
        'updated_at': updated_at,
        'vendors': raw['vendors'],
        'free_models': raw.get('free_models', []),
    }

    out_path = Path('data/models.json')
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"Built data/models.json — updated_at: {updated_at}")
    print(f"  {len(raw['vendors'])} vendors, {len(raw.get('free_models', []))} free models")

    # 歷史價格 CSV（每天 append 一次）
    history_path = Path('data/price_history.csv')
    write_header = not history_path.exists()
    today = now_tw.strftime('%Y-%m-%d')
    with open(history_path, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(['date', 'model_id', 'input_price', 'output_price'])
        for v in raw['vendors']:
            for m in v['models']:
                w.writerow([today, m['id'],
                            m.get('input_price', 0), m.get('output_price', 0)])
    print(f"Appended {today} to price_history.csv")


if __name__ == '__main__':
    main()
