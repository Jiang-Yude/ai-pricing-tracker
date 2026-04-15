"""
fetch_models.py
從 OpenRouter 公開 API 抓取所有模型定價，輸出 raw_models.json
不需要任何 API key
"""
import json
import urllib.request
from pathlib import Path

API_URL = "https://openrouter.ai/api/v1/models"

BIG3 = {'anthropic', 'openai', 'google'}

ALL_VENDORS = [
    {'prefix': 'anthropic',  'name': 'Anthropic',  'color': '#D97706'},
    {'prefix': 'openai',     'name': 'OpenAI',     'color': '#10B981'},
    {'prefix': 'google',     'name': 'Google',     'color': '#3B82F6'},
    {'prefix': 'x-ai',       'name': 'xAI (Grok)', 'color': '#8B5CF6'},
    {'prefix': 'deepseek',   'name': 'DeepSeek',   'color': '#EF4444'},
    {'prefix': 'qwen',       'name': 'Qwen',       'color': '#F59E0B'},
    {'prefix': 'mistralai',  'name': 'Mistral',    'color': '#06B6D4'},
    {'prefix': 'meta-llama', 'name': 'Meta',       'color': '#6366F1'},
    {'prefix': 'minimax',    'name': 'MiniMax',    'color': '#EC4899'},
    {'prefix': 'nvidia',     'name': 'NVIDIA',     'color': '#84CC16'},
    {'prefix': 'arcee-ai',   'name': 'Arcee AI',   'color': '#14B8A6'},
    {'prefix': 'stepfun',    'name': 'StepFun',    'color': '#F97316'},
]

FREE_TARGETS = [
    'meta-llama/llama-3.3-70b-instruct:free',
    'nvidia/nemotron-3-super-120b-a12b:free',
    'google/gemma-3-27b-it:free',
    'qwen/qwen3-coder:free',
    'qwen/qwen3.6-plus:free',
    'nvidia/nemotron-3-nano-30b-a3b:free',
    'openai/gpt-oss-120b:free',
]


def fetch():
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data.get('data', [])


def build_model_entry(m):
    pricing = m.get('pricing', {})
    prompt = float(pricing.get('prompt', 0) or 0)
    completion = float(pricing.get('completion', 0) or 0)
    return {
        'id': m['id'],
        'name': m.get('name', m['id']),
        'input_price': round(prompt * 1_000_000, 4),
        'output_price': round(completion * 1_000_000, 4),
        'context_length': m.get('context_length') or 128000,
        'is_free': ':free' in m['id'] and prompt == 0,
        'openrouter_url': f"https://openrouter.ai/models/{m['id']}",
    }


def main():
    print("Fetching models from OpenRouter...")
    raw = fetch()
    print(f"  Got {len(raw)} models")

    model_map = {m['id']: build_model_entry(m) for m in raw if 'id' in m}

    # 每個廠商取高中低三款（依 output_price 高到低，非零付費模型）
    vendors = []
    for v in ALL_VENDORS:
        prefix = v['prefix']
        candidates = [
            m for mid, m in model_map.items()
            if mid.startswith(prefix + '/') and m['output_price'] > 0 and not m['is_free']
        ]
        candidates.sort(key=lambda x: x['output_price'], reverse=True)
        top3 = candidates[:3]
        if not top3:
            continue
        tiers = ['high', 'mid', 'low']
        for i, m in enumerate(top3):
            m['tier'] = tiers[i]
        vendors.append({
            'vendor': v['name'],
            'prefix': prefix,
            'color': v['color'],
            'models': top3,
        })
        print(f"  {v['name']}: {len(top3)} models")

    # 免費模型
    free_models = []
    for fid in FREE_TARGETS:
        if fid in model_map:
            free_models.append(model_map[fid])
        else:
            print(f"  [WARN] Free model not found: {fid}")

    out = {'vendors': vendors, 'free_models': free_models}
    Path('data').mkdir(exist_ok=True)
    Path('data/raw_models.json').write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"Saved: {len(vendors)} vendors, {len(free_models)} free models")


if __name__ == '__main__':
    main()
