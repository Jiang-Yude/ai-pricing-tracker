# AI API 定價追蹤器

> 每天早上 06:00（台灣時間）自動更新 · 資料來源：OpenRouter

🔗 **網頁：** https://jiang-yude.github.io/ai-pricing-tracker/

由 [江江教練](https://portaly.cc/Jiang_Yude) 設計製作 ·
Threads [@jiang_yude_coach](https://www.threads.com/@jiang_yude_coach)

---

## 這是什麼？

一個追蹤主流 AI API 定價的靜態網頁，每天自動從 OpenRouter 抓取最新定價，部署在 GitHub Pages 上免費運行。

**適合誰看：** 想比較不同 AI 模型 API 費用的開發者、研究者、或對 AI 工具感興趣的人。

---

## 功能

- **三張比較圖表**
  - 價格直方圖（對數刻度，含所有廠商）
  - 使用熱度排行（omniscienceIndex）
  - 熱度 vs 定價散點圖（右下角 = CP 值最高）

- **三個模型區塊**
  - 主要三大廠商（Anthropic / OpenAI / Google，各取高中低三款）
  - 免費好用模型 TOP 5
  - 其他熱門模型 TOP 10

- **每天 06:00 自動更新**（GitHub Actions，完全免費）
- **奶茶 / 系統 / 深咖** 三種配色，預設跟系統走

---

## 資料來源

| 資料 | 來源 | 費用 |
|---|---|---|
| 模型定價 | [OpenRouter 公開 API](https://openrouter.ai/api/v1/models) | 免費，不需要 key |
| 使用熱度 | [artificialanalysis.ai](https://artificialanalysis.ai/models) | 免費爬取 |
| 模型簡介 | OpenRouter API description 欄位 | 免費 |

> ⚠️ 資料由程式自動抓取，僅供參考，請以各廠商官方網站定價為準。
> 使用熱度（omniscienceIndex）為第三方估算，非官方數據。

---

## 自動更新機制

使用 GitHub Actions，每天台灣時間早上 06:00 自動執行：

```
fetch_models.py   → 從 OpenRouter 抓定價
fetch_rankings.py → 從 artificialanalysis.ai 抓熱度
build_json.py     → 合併輸出 data/models.json
git push          → GitHub Pages 自動更新
```

也可以在 GitHub Actions 頁面手動觸發。

---

## 本地執行

```bash
git clone https://github.com/Jiang-Yude/ai-pricing-tracker.git
cd ai-pricing-tracker

python scripts/fetch_models.py
python scripts/fetch_rankings.py
python scripts/build_json.py

# 用任意 http server 預覽
python -m http.server 8080
```

不需要任何 API key。

---

## 授權

MIT License · 資料版權屬各原始來源所有
