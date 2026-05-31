# Apple Product VOC Dashboard 📱

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://hiyulia-apple-voc-dashboard-oibfoj.streamlit.app/)
[![GitHub Stars](https://img.shields.io/github/stars/HiYulia/apple-voc?style=for-the-badge)](https://github.com/HiYulia/apple-voc/stargazers)

A continuously updated **Voice of Customer (VOC) analytics platform** for Apple products — currently covering iPhone 17, with iPad and Mac planned.

Data is collected from real user discussions on **Xiaohongshu (小红书)** and **Bilibili (B站)**, classified using **Claude claude-haiku-4-5** semantic analysis.

🔗 **Live Dashboard** → [hiyulia-apple-voc-dashboard-oibfoj.streamlit.app](https://hiyulia-apple-voc-dashboard-oibfoj.streamlit.app/)

---

## Features

- **Bilingual UI** — toggle between 中文 / English
- **Semantic classification** via Claude claude-haiku-4-5 (not keyword matching)
- **Multi-source data** — Xiaohongshu notes & comments, Bilibili video comments
- **Time-stamped** — all data tagged with source and date range
- **Extensible** — designed to add iPad, Mac, and other product lines

## Current Data Coverage

| Product | Sources | Date Range | Reviews |
|---------|---------|------------|---------|
| iPhone 17 series | 小红书, B站 | 2025-07-20 → present | 1,100+ |

## Tech Stack

- **Scraping** — [MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) (Playwright-based)
- **Classification** — Claude claude-haiku-4-5 via [OpenRouter](https://openrouter.ai)
- **Dashboard** — Streamlit + Plotly
- **Storage** — CSV (upgradeable to PostgreSQL)

## Project Structure

```
apple-voc/
├── dashboard.py        # Streamlit dashboard (bilingual)
├── analyzer.py         # Claude semantic classifier
├── scraper.py          # JD.com scraper (cookie-based)
├── merge_data.py       # Merge new data into existing dataset
├── i18n.py             # Bilingual string definitions
├── requirements.txt
└── data/               # CSV files (gitignored, see below)
```

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/apple-voc.git
cd apple-voc
pip install -r requirements.txt

# Set your OpenRouter API key
export OPENROUTER_API_KEY="sk-or-..."

# Run dashboard (needs data files — see Data Collection)
streamlit run dashboard.py
```

## Data Collection

Data files are **not committed** to the repo (privacy + size). To collect your own:

**Xiaohongshu & Bilibili** via MediaCrawler:
```bash
git clone https://github.com/NanmiCoder/MediaCrawler.git
cd MediaCrawler
pip install -r requirements.txt
# Edit config/base_config.py: set PLATFORM, KEYWORDS, LOGIN_TYPE
python main.py --platform xhs --lt qrcode --type search
```

Then merge and classify:
```bash
python merge_data.py ~/path/to/downloaded.csv
python analyzer.py
```

## Adding New Products (iPad, Mac, etc.)

1. Scrape with keywords like `"iPad Pro", "M4 iPad"` via MediaCrawler
2. Run `merge_data.py` — it auto-deduplicates
3. Re-run `analyzer.py`
4. Dashboard auto-updates with new product filter options

## Roadmap

- [ ] iPad (iPad Pro, iPad Air)
- [ ] Mac (MacBook Air, MacBook Pro)
- [ ] Scheduled weekly auto-scrape
- [ ] Trend analysis over time
- [ ] Export to Notion / Google Sheets

---

*Built by [Yuyu](https://medium.com/@yulianiu) · Data for learning purposes only*
