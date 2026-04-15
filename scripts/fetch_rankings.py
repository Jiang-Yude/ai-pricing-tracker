"""
fetch_rankings.py
從 artificialanalysis.ai 爬取 omniscienceIndex 熱度指數
不需要 API key，爬取公開頁面
"""
import json
import re
import urllib.request
from pathlib import Path

URL = "https://artificialanalysis.ai/models"


def fetch():
    req = urllib.request.Request(URL, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode('utf-8', errors='ignore')


def parse(html):
    # 嘗試多種 pattern
    patterns = [
        r'"modelName"\s*:\s*"([^"]+)"\s*,\s*"omniscienceIndex"\s*:\s*([\d.]+)',
        r'"name"\s*:\s*"([^"]+)"\s*[^}]*?"omniscienceIndex"\s*:\s*([\d.]+)',
    ]
    results = {}
    for pat in patterns:
        matches = re.findall(pat, html)
        for name, score in matches:
            results[name] = float(score)
        if results:
            break
    return results


def main():
    print("Fetching rankings from artificialanalysis.ai...")

    # 載入既有 models
    raw_path = Path('data/raw_models.json')
    if not raw_path.exists():
        print("  [ERROR] data/raw_models.json not found, run fetch_models.py first")
        return

    raw = json.loads(raw_path.read_text())

    try:
        html = fetch()
        rankings = parse(html)
        print(f"  Found {len(rankings)} rankings")
    except Exception as e:
        print(f"  [WARN] Failed to fetch rankings: {e}")
        print("  Using placeholder values")
        rankings = {}

    # 名稱對應表（OpenRouter name → artificialanalysis name 可能不同）
    NAME_MAP = {
        'claude': 'Claude',
        'gpt': 'GPT',
        'gemini': 'Gemini',
        'grok': 'Grok',
        'deepseek': 'DeepSeek',
        'qwen': 'Qwen',
        'llama': 'Llama',
        'mistral': 'Mistral',
    }

    def find_omni(model_id, model_name):
        # 先用 id 片段找
        for rank_name, score in rankings.items():
            if any(kw in model_id.lower() for kw in rank_name.lower().split()):
                return score
        # 再用 name 找
        for rank_name, score in rankings.items():
            if rank_name.lower() in model_name.lower():
                return score
        # fallback: 根據廠商給預設值
        prefix = model_id.split('/')[0]
        defaults = {
            'anthropic': 3.5, 'openai': 3.0, 'google': 3.2,
            'deepseek': 4.0, 'x-ai': 2.5, 'qwen': 2.2,
            'meta-llama': 2.8, 'mistralai': 1.8, 'minimax': 1.2,
            'nvidia': 1.5, 'arcee-ai': 0.8, 'stepfun': 0.6,
        }
        return defaults.get(prefix, 1.0)

    # 注入 omni 到 vendors
    for v in raw['vendors']:
        for m in v['models']:
            m['omniscience_index'] = find_omni(m['id'], m['name'])

    # 注入 omni 到 free_models
    for m in raw['free_models']:
        m['omniscience_index'] = find_omni(m['id'], m['name']) * 0.8

    raw_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2))
    print("Saved omniscience_index to raw_models.json")


if __name__ == '__main__':
    main()
