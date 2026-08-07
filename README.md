<div align="center">

# 📊 AI Business Analytics Studio

**Upload your business data. Get a dashboard, AI insights, forecasts and board-ready reports in minutes.**

A mini Power BI + ChatGPT for business data — built entirely in Python

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Charts-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Gemini](https://img.shields.io/badge/Gemini-API-4285F4?logo=googlegemini&logoColor=white)](https://aistudio.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Live demo](https://share.streamlit.io/) · [Report a bug](../../issues) · [Request a feature](../../issues)

</div>

---

## Overview

Most small businesses sit on months of sales data in a spreadsheet and never get an answer out of it.
Power BI is expensive and takes training; a data analyst costs more than the insight is worth.

**AI Business Analytics Studio closes that gap.** Drop in a CSV, Excel workbook, JSON file or SQL
connection and the app profiles it, cleans it, builds a KPI dashboard, writes an executive report,
forecasts the next quarter, flags anomalies, segments customers, and exports the whole thing as a PDF
— in about two minutes, with no configuration.

The design decision that makes this work on *anyone's* data: no column name is ever hard-coded.
`core/mapping.py` scores every column against regex patterns **and** dtype checks to auto-detect
semantic roles — `date`, `revenue`, `profit`, `customer_id`, `product`, `category`, `region` — and the
user can override any of them in one screen. The same dashboard, RFM engine and forecaster then run
on a Shopify export, a QuickBooks dump or a hand-typed sheet.

**It also runs completely offline.** Without a Gemini API key, a deterministic rule engine writes the
insights and answers chat questions, so no feature is ever a dead end.

---

## Features

| Module | What it does |
|---|---|
| 📤 **Upload Center** | CSV, Excel (multi-sheet), JSON, ZIP, SQLite files and live SQL databases. Auto-detects encoding and delimiter, validates every file. |
| 🔍 **Data Profiling** | Shape, dtypes, nulls, duplicates, memory, unique values, numeric statistics, correlation matrix and a 0–100 quality score. |
| 🧹 **Smart Cleaning** | Duplicates, 9 missing-value strategies, date standardisation, text case, whitespace, outliers, type conversion — all logged and undoable. |
| 🔀 **Transformation** | Group-by, pivots, merges, column splitting, feature engineering, binning, scaling, encoding. |
| 📊 **Dashboard** | 9 KPIs with period-over-period deltas, revenue trend, category donut, top products, world map, embedded forecast. |
| 📈 **Visualizations** | 14 chart types with filters, zoom and PNG / interactive-HTML export. |
| ✨ **AI Insights** | Executive summary, trends, best and worst products, opportunities, risks, customer insights, P1–P4 recommendations. |
| 💬 **Chat with Data** | *"Why did sales drop?"* · *"Top 10 customers"* · *"Which category is most profitable?"* |
| 🔮 **Forecasting** | 4 models, 7–365 period horizons, backtest MAE/MAPE, 95% confidence bands, what-if scenarios. |
| 🚨 **Anomaly Detection** | Z-score, IQR, rolling z-score and Isolation Forest over trends *and* individual transactions. |
| 👥 **Customer Analytics** | RFM scoring, 11 segments, 12-month CLV, churn-risk bands, cohort retention heatmap. |
| 📦 **Product Analytics** | Best sellers, slow movers, margins, ABC classification, inventory actions. |
| 🖥️ **SQL Workspace** | Query every loaded dataset with real SQL, save queries, export results. |
| 📄 **Report Generator** | PDF, Excel, CSV bundle and PowerPoint — with KPIs, charts and the AI narrative. |
| 🕘 **History · ⚙️ Settings · 🛡️ Admin · 📚 Docs** | Activity log, theme and AI configuration, user management, built-in user guide. |

---

## Screenshots

| Dashboard | AI Insights | Forecasting |
|---|---|---|
| ![Dashboard](assets/screenshot-dashboard.png) | ![Insights](assets/screenshot-insights.png) | ![Forecast](assets/screenshot-forecast.png) |

> Save your captures to `assets/` with these filenames. A 20-second GIF at `assets/demo.gif`
> — upload → dashboard → insights → PDF — is the single highest-value addition to this README.

---

## Quick start

```bash
git clone https://github.com/ayeshamumtaz1057/ai-business-analytics-studio.git
cd ai-business-analytics-studio

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python scripts/generate_sample_data.py     # builds the demo dataset

streamlit run app.py
```

Open <http://localhost:8501> and sign in with **`demo` / `demo123`**, or click *Continue as guest*.

### Enable AI (optional)

```bash
export GEMINI_API_KEY="your_key_from_https://aistudio.google.com/apikey"
```

Or paste the key into **Settings → AI model** at runtime. Skip this entirely and the app falls back
to its built-in offline analyst — every module still works.

### Docker

```bash
docker compose up --build
```

### Deploy to Streamlit Cloud

1. Push the repo to GitHub.
2. On [share.streamlit.io](https://share.streamlit.io) → **New app**, select the repo and `app.py`.
3. Add `GEMINI_API_KEY = "..."` under **Settings → Secrets**.
4. Deploy. Pushes to `main` redeploy automatically.

> The Cloud filesystem is ephemeral, so `data/app.db` resets on reboot. For persistent accounts and
> history, point `DB_PATH` in `core/config.py` at a hosted Postgres and store the URI in Secrets.

---

## Try it in two minutes

1. **Load demo data** from the sidebar — 9,040 orders, 24 products, 6 categories, 11 markets, 2024.
2. **Data Profiling** → quality score 99/100, with 39 duplicates and 107 nulls flagged.
3. **Smart Cleaning** → remove duplicates, trim whitespace (this merges the messy product names).
4. **Dashboard** → $7.04M revenue, 25.5% margin, +12.5% period-over-period.
5. **Chat** → *"Which category is most profitable?"* → **Beauty, 52.0% margin on $323.4K**.
6. **Report Generator** → a 3-page PDF with the KPI grid, charts and AI narrative.

---

## Tech stack

| Layer | Technology |
|---|---|
| UI | Streamlit (`st.navigation` multipage, custom CSS design system) |
| Data | Pandas, NumPy |
| Charts | Plotly Express + Graph Objects |
| ML | scikit-learn — Ridge, RandomForest, IsolationForest, scalers |
| Database | SQLAlchemy + SQLite (PostgreSQL / MySQL ready) |
| AI | Google Gemini, with a deterministic offline fallback |
| Reports | ReportLab, OpenPyXL, python-pptx, Kaleido |
| Deploy | Docker + docker-compose, Streamlit Cloud |

---

## Project structure

```
ai_analytics_studio/
├── app.py                  # entry point: auth gate + sidebar navigation
├── core/                   # all business logic — no UI code
│   ├── config.py           # constants, semantic roles, regex patterns, palette
│   ├── mapping.py          # role auto-detection (the core abstraction)
│   ├── loaders.py          # CSV / Excel / JSON / ZIP / SQL ingestion
│   ├── profiling.py        # profiling + data-quality score
│   ├── cleaning.py         # cleaning ops, each returning (df, message)
│   ├── transform.py        # reshape & feature engineering
│   ├── kpis.py             # KPI computation, formatting, time series
│   ├── charts.py           # 14 chart types + dashboard figures
│   ├── forecasting.py      # 4 models, backtesting, confidence bands
│   ├── customers.py        # RFM, CLV, churn, cohorts
│   ├── products.py         # performance, ABC, movers, inventory
│   ├── anomalies.py        # 4 detection methods
│   ├── insights.py         # data brief → AI report, offline fallback
│   ├── nlq.py              # natural language → sandboxed pandas → narrative
│   ├── reports.py          # PDF / Excel / PPTX builders
│   └── ai.py · db.py · auth.py · state.py · theme.py · utils.py
├── views/                  # one file per page (20 pages)
├── tests/                  # logic smoke test + headless render test
├── scripts/generate_sample_data.py
└── Dockerfile · docker-compose.yml · requirements.txt
```

---

## Testing

```bash
PYTHONPATH=. python tests/smoke.py        # every analytics function end-to-end
PYTHONPATH=. python tests/test_views.py   # renders all 20 pages headlessly
```

Both must stay green before a merge.

---

## Roadmap

* Prophet and SARIMAX forecasting with automatic model selection
* Scheduled refreshes and email delivery of reports
* Alerting rules — notify when an anomaly or KPI threshold fires
* Live connectors for Shopify, Stripe, Google Sheets and QuickBooks
* Multi-tenant workspaces with row-level permissions
* Vector-store memory so chat remembers findings across sessions
* Model-agnostic AI layer (OpenAI, Claude, local Ollama)
* Urdu interface translation
* CI pipeline running the test suite on every push

---

## Contributing

Contributions are welcome.

```bash
git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature
```

Please keep all logic in `core/` (never in `views/`), route every model call through `ai.py`, never
hard-code a column name — read it via `state.col("revenue")` — and add a test for any new analytic.

### Adding a semantic role

```python
# core/config.py
ROLES.append("channel")
ROLE_LABELS["channel"] = "Sales Channel"
ROLE_PATTERNS["channel"] = r"(channel|source|medium|platform)"
```

It is auto-detected on upload, appears in the mapping editor, and becomes available to every module
through `state.col("channel")` and `kpis.breakdown(df, mapping, "channel")`.

---

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

---

## Acknowledgements

* **Streamlit** — the framework that made a 20-page analytics app feasible in days
* **Plotly** — interactive charts that survive being embedded in a PDF
* **scikit-learn** — Ridge, RandomForest and IsolationForest behind the forecasts and anomaly flags
* **ReportLab** — board-ready PDF generation without a headless browser
* **Google AI Studio** — free Gemini API access

---

## Disclaimer

Forecasts, anomaly flags and AI commentary are decision *support*, not decision *guarantees*.
Statistical outliers are not proof of fraud, and no model can anticipate a campaign, a price change
or a market shock. Validate against your own domain knowledge before acting.

---

## Author

**Ayesha Mumtaz**
BS Information Technology

[GitHub](https://github.com/ayeshamumtaz1057) · [LinkedIn](https://www.linkedin.com/)

<div align="center">

⭐ **Star this repo if you found it useful.**

</div>
