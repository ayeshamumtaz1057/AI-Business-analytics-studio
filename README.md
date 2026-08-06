# 📊 AI Business Analytics Studio

> Upload your business data. Get a professional dashboard, AI insights, forecasts, and
> board-ready reports in minutes. **A mini Power BI + ChatGPT for business data.**

Built with Python, Streamlit, Pandas, Plotly, scikit-learn and the Gemini API.
Every module works on *any* tabular dataset thanks to a semantic column-mapping layer —
and the whole app runs **fully offline** when no AI key is configured.

---

## ✨ Overview

A business owner drops in a CSV, Excel workbook, JSON file or SQL connection and immediately gets:

| | |
|---|---|
| 📈 **Professional dashboard** | 8 KPIs with period-over-period deltas, trends, breakdowns, regional map |
| ✨ **AI insights** | Executive summary, trends, opportunities, risks, prioritised recommendations |
| 🔮 **Forecasts** | 7–365 period projections with confidence bands and what-if scenarios |
| 📄 **Reports** | PDF, Excel, CSV bundle, PowerPoint — with charts, KPIs and AI narrative |
| 💬 **Chat with data** | "Why did sales drop?" · "Top 10 customers" · "Which category is most profitable?" |
| 🎯 **Recommendations** | Inventory actions, churn targets, pricing reviews |
| ⬇️ **Exports** | Any dataset, any format, one click |

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        STREAMLIT UI  (app.py + views/)                   │
│  Home · Dashboard · Upload · Profiling · Cleaning · Transform · Charts    │
│  Insights · Chat · Forecast · Anomalies · Customers · Products · SQL      │
│  Reports · Exports · History · Settings · Admin · Docs                   │
└───────────────┬──────────────────────────────────────────────────────────┘
                │  session state (datasets, column mapping, chat, cache)
┌───────────────▼──────────────────────────────────────────────────────────┐
│                             CORE ENGINE  (core/)                         │
│                                                                          │
│  loaders ──► mapping ──► cleaning ──► transform ──► kpis ──► charts       │
│     │           │                                    │          │        │
│     │      auto-detects date / revenue / profit /    │          │        │
│     │      customer / product / category / region    │          │        │
│     │                                                ▼          ▼        │
│  profiling   forecasting   customers   products   anomalies   insights    │
│                  (sklearn)   (RFM/CLV)   (ABC)    (IsoForest)    │        │
│                                                                  ▼       │
│                                          nlq ◄────────────► ai (Gemini)  │
│                                                                  │       │
│                                          reports ◄───────────────┘       │
│                                   (ReportLab · OpenPyXL · python-pptx)   │
└───────────────┬───────────────────────────────┬──────────────────────────┘
                │                               │
       ┌────────▼────────┐            ┌─────────▼──────────┐
       │  SQLite / SQLAlchemy         │  Gemini API        │
       │  users · datasets ·          │  (optional —       │
       │  reports · chat · history    │  offline fallback) │
       └──────────────────────────────┴────────────────────┘
```

**The key design decision:** every analytics module reads *semantic roles*
(`date`, `revenue`, `profit`, `customer_id`, `product`, `category`, `region`, …) rather than
hard-coded column names. `core/mapping.py` scores each column against regex patterns **and**
dtype checks to auto-detect those roles, and the user can override them in one screen.
That is what lets the same dashboard, forecast and RFM engine work on any business dataset.

---

## 🧩 Feature list

<details open>
<summary><b>Data layer</b></summary>

- **Upload Center** — CSV, Excel (multi-sheet), JSON, ZIP (multiple datasets), SQLite files,
  and live SQL databases via SQLAlchemy. Auto-detects encoding (chardet + fallback ladder) and
  delimiter (`csv.Sniffer` + frequency fallback). Upload progress, per-file validation.
- **Data Profiling** — shape, dtypes, null counts and %, duplicates, memory usage, unique
  values, numeric statistics (incl. skew/kurtosis), correlation matrix + strongest pairs, and a
  0–100 data-quality score.
- **Smart Data Cleaning** — remove duplicates, 9 missing-value strategies, date standardisation,
  text case, whitespace trimming, outlier removal/clipping (IQR or z-score), type conversion,
  column renaming and snake_casing. Every action logged, one-click **undo**.
- **Data Transformation** — group-by, pivot tables, dataset merges, column splitting, formula and
  ratio feature engineering, calendar features, binning (equal-width/quantile), scaling
  (standard/minmax/robust), encoding (one-hot/label/frequency), sort & query filter.
</details>

<details open>
<summary><b>Analytics layer</b></summary>

- **Business Dashboard** — Revenue, Profit, Orders, Customers, Units, AOV, Profit Margin,
  Revenue/Customer and Sales Target Achievement, each with period-over-period deltas; revenue
  trend with rolling average, category donut, top-10 products, world map, embedded 90-day forecast.
- **Interactive Visualizations** — 14 chart types (bar, line, area, pie, donut, scatter, bubble,
  histogram, box, heatmap, treemap, sunburst, waterfall, correlation matrix) with filters, zoom,
  PNG and interactive-HTML download.
- **AI Business Insights** — executive summary, key trends, best/worst products, sales
  opportunities, business risks, customer insights and P1–P4 recommendations.
- **Natural Language Chat** — Gemini writes a sandboxed pandas expression, runs it, then narrates
  the result. Falls back to an intent engine offline.
- **Forecasting** — Ridge (trend + Fourier seasonality + calendar features), Random Forest,
  moving average and linear trend; 7/14/30/60/90/180/365 horizons; backtest MAE/MAPE;
  95% confidence band; what-if uplift slider.
- **Customer Analytics** — RFM scoring, 11 named segments, 12-month CLV estimate, churn-risk
  bands, repeat-purchase rate, revenue concentration, cohort retention heatmap.
- **Product Analytics** — best sellers, slow movers, margins, revenue share, ABC classification,
  days-since-last-sale, category performance and heuristic inventory actions.
- **Anomaly Detection** — z-score, IQR, rolling z-score and Isolation Forest over both time series
  (spikes/drops with severity) and individual transactions.
</details>

<details open>
<summary><b>Delivery layer</b></summary>

- **SQL Workspace** — every loaded dataset registered as a queryable table, saved queries,
  CSV/Excel export, save results back as a dataset.
- **Report Generator** — PDF (ReportLab: KPI grid, embedded charts, AI narrative, data tables,
  page footers), Excel (styled, frozen headers, auto-width), CSV bundle (ZIP), PowerPoint deck.
- **Export Data** — CSV, JSON, multi-sheet Excel or ZIP for any combination of datasets.
- **Project History** — datasets, reports (re-downloadable), chat transcripts, full activity log.
- **Authentication** — registration, login, PBKDF2-SHA256 password hashing with per-user salt,
  password reset, guest mode, profile settings.
- **Settings** — theme, language, Gemini key + model selection with a connection test, column
  mapping editor, account management.
- **Admin Panel** — user and role management, dataset/report oversight, daily usage charts and
  AI-call monitoring.
- **Documentation** — built-in guide, module reference, FAQ and downloadable example dataset.
</details>

---

## 📸 Screenshots

| Dashboard | AI Insights | Forecasting |
|---|---|---|
| ![Dashboard](assets/screenshot-dashboard.png) | ![Insights](assets/screenshot-insights.png) | ![Forecast](assets/screenshot-forecast.png) |

> Drop your own captures into `assets/` with these filenames. A short demo GIF
> (`assets/demo.gif`) is the single highest-value addition to this README —
> record upload → dashboard → AI insights → PDF export in about 20 seconds.

---

## 🚀 Installation

### Local

```bash
git clone https://github.com/<you>/ai-business-analytics-studio.git
cd ai-business-analytics-studio

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python scripts/generate_sample_data.py     # creates the demo dataset

streamlit run app.py
```

Open <http://localhost:8501>. Sign in with **`demo` / `demo123`**, or click *Continue as guest*.

### Enable AI (optional)

```bash
cp .env.example .env          # then add your key
export GEMINI_API_KEY="your_key_from_https://aistudio.google.com/apikey"
```

You can also paste the key into **Settings → AI model** at runtime.
**Without a key everything still works** — the app switches to a deterministic offline analyst
for insights and chat.

### Docker

```bash
docker compose up --build
# or
docker build -t analytics-studio . && docker run -p 8501:8501 analytics-studio
```

---

## 🎬 Demo

1. **Load demo data** in the sidebar (9,040 orders, 24 products, 6 categories, 11 markets, 2024).
2. **Data Profiling** → quality score 99/100, 39 duplicates and 107 nulls flagged.
3. **Smart Cleaning** → remove duplicates, trim whitespace (merges the messy product names).
4. **Dashboard** → $7.04M revenue, 25.5% margin, +12.5% period-over-period.
5. **AI Insights** → full executive report.
6. **Chat** → *"Which category is most profitable?"* → **Beauty, 52.0% margin on $323.4K**.
7. **Forecasting** → 90-day projection with confidence band.
8. **Report Generator** → 3-page PDF with KPI grid, charts and the AI narrative.

---

## 🛠 Tech stack

| Layer | Technology |
|---|---|
| UI | Streamlit 1.40+ (`st.navigation` multipage, custom CSS design system) |
| Data | Pandas 2/3, NumPy |
| Charts | Plotly (Express + Graph Objects) |
| ML | scikit-learn — Ridge, RandomForest, IsolationForest, scalers |
| Database | SQLAlchemy + SQLite (PostgreSQL/MySQL ready) |
| AI | Google Gemini (`gemini-2.0-flash` by default) with offline rule engine |
| Reports | ReportLab (PDF), OpenPyXL (Excel), python-pptx (slides), Kaleido (chart images) |
| Packaging | Docker + docker-compose |

---

## 📁 Folder structure

```
ai_analytics_studio/
├── app.py                     # entry point: auth gate + st.navigation sidebar
├── core/                      # all business logic — no Streamlit UI code
│   ├── config.py              # constants, semantic roles, regex patterns, palette
│   ├── theme.py               # CSS design system, KPI/insight cards, plotly theming
│   ├── utils.py               # pandas 2/3 dtype helpers
│   ├── db.py                  # SQLAlchemy schema + query helpers
│   ├── auth.py                # PBKDF2 auth, roles, session
│   ├── state.py               # dataset registry & active-dataset helpers
│   ├── loaders.py             # CSV/Excel/JSON/ZIP/SQL ingestion + validation
│   ├── mapping.py             # semantic role auto-detection (the core abstraction)
│   ├── profiling.py           # profiling & data-quality score
│   ├── cleaning.py            # cleaning operations -> (df, message)
│   ├── transform.py           # reshape & feature engineering
│   ├── kpis.py                # KPI computation, formatting, time series, breakdowns
│   ├── charts.py              # 14 chart types + purpose-built dashboard figures
│   ├── forecasting.py         # 4 models, backtesting, confidence bands, scenarios
│   ├── customers.py           # RFM, CLV, churn, cohorts
│   ├── products.py            # performance, ABC, movers, inventory actions
│   ├── anomalies.py           # 4 detection methods
│   ├── ai.py                  # Gemini client + availability checks
│   ├── insights.py            # data brief -> AI report, offline analyst fallback
│   ├── nlq.py                 # natural language -> sandboxed pandas -> narrative
│   └── reports.py             # PDF / Excel / PPTX builders
├── views/                     # one file per page (20 pages)
├── scripts/generate_sample_data.py
├── data/{samples,uploads,reports}/
├── .streamlit/config.toml
├── Dockerfile · docker-compose.yml · requirements.txt
└── README.md · LICENSE · CONTRIBUTING.md
```

---

## 🗺 Future roadmap

- [ ] Scheduled refreshes and email delivery of reports
- [ ] Multi-tenant workspaces with row-level permissions
- [ ] Prophet / SARIMAX forecasting and automatic model selection
- [ ] Write-back connectors (Google Sheets, Shopify, Stripe, QuickBooks)
- [ ] Vector-store memory so chat remembers earlier findings across sessions
- [ ] Alerting rules — notify on anomalies or KPI thresholds
- [ ] Model-agnostic AI layer (OpenAI, Claude, local Ollama)
- [ ] Full i18n, starting with Urdu and Spanish

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: keep **all business logic in `core/`** and pure
of Streamlit calls, one page per file in `views/`, and add a smoke test for any new module.

---

## ⚠️ Disclaimer

Forecasts, anomaly flags and AI commentary are decision *support*, not decision *guarantees*.
Statistical outliers are not proof of fraud, and forecasts cannot anticipate campaigns, price
changes or market shocks. Always validate against your own domain knowledge before acting.

## 📄 License

MIT — see [LICENSE](LICENSE).
