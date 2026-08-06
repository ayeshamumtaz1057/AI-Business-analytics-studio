# 📊 AI CSV Analytics Pro
**A focused data analytics workspace — automated cleaning, visualization, predictive modeling, and reporting, all in one dashboard**

Built by Ayesha Mumtaz

AI CSV Analytics Pro is a Streamlit dashboard built around a single, complete pipeline — **upload → clean → profile → visualize → model → export** — for any CSV or Excel file, running entirely locally with no external API dependency.

[Overview](#overview) · [Demo](#demo) · [Screenshots](#screenshots) · [Features](#features) · [Architecture](#architecture) · [Tech Stack](#tech-stack) · [Data Pipeline](#data-pipeline) · [Getting Started](#getting-started) · [Deployment](#deployment) · [Troubleshooting](#troubleshooting)

## Quick Start

```bash
git clone https://github.com/ayeshamumtaz1057/AI_CSV_Analytics_Pro.git
cd AI_CSV_Analytics_Pro
pip install -r requirements.txt
streamlit run app.py
```

Open the app at **http://localhost:8501**. No API key or `.env` file required — every feature runs on local computation.

---

## Overview

AI CSV Analytics Pro turns a raw spreadsheet into a finished analysis in one pass. Upload a file, choose how duplicates and missing values should be handled, and the app profiles the dataset, surfaces statistical insights, renders interactive charts, trains a regression model, and exports everything as a PDF or Excel report — all from a single dashboard.

### The Problem

Getting from "raw spreadsheet" to "shareable analysis" usually means bouncing between a notebook for cleaning, a separate charting tool, and a third tool for the writeup — each with its own setup and no shared state between them. A cleaning decision made early (say, how to fill missing values) rarely carries through consistently to the charts or the final report.

### The Solution

AI CSV Analytics Pro unifies the pipeline behind one dashboard, so every step follows the same flow:

- **Upload** — drop in a CSV, XLSX, or XLS file
- **Clean** — choose duplicate handling and a missing-value strategy from the sidebar
- **Analyze** — get a data health score, profiling metrics, and rule-based insights
- **Visualize** — pick from 9 interactive chart types
- **Model** — train a Linear Regression model on any numeric columns
- **Export** — download a PDF summary or Excel workbook

Everything runs on your machine. Nothing is uploaded anywhere — the app has no network dependency for its core features.

---

## Demo

Add your demo video link here.

**Live app:** *add your Streamlit Cloud URL here*

---

## Screenshots

### Dashboard
Sidebar cleaning controls, hero banner, and dark enterprise theme. The gradient header, graphite cards, and metric styling are hand-written CSS injected over Streamlit's defaults.

*(add screenshot)*

### Executive Overview
Row/column counts, missing-cell percentage, and duplicate count, computed live from the cleaned dataset.

*(add screenshot)*

### Visual Analytics
Chart-type picker with live Plotly rendering — bar, line, scatter, histogram, box, pie, correlation heatmap, treemap, and sunburst.

*(add screenshot)*

### Predictive Modeling
Target/feature selection with R², RMSE, and MAE displayed after training.

*(add screenshot)*

---

## Features

### 1. AI Data Analyst — main feature

| Capability | Detail |
|---|---|
| Upload | CSV, XLSX, and XLS files, with automatic encoding fallback (UTF-8 → Latin-1 → CP1252) |
| Profiling | Row/column counts, missing values, duplicates, full statistics |
| Cleaning | Drop duplicates; fill nulls via Mean/Mode, Drop Rows, or leave as None |
| Visualization | 9 Plotly chart types — bar, line, scatter, histogram, box, pie, correlation heatmap, treemap, sunburst |
| Insights | Rule-based analysis: skewness, correlation strength, dominant categories, data health scoring |
| Export | Download the cleaned result as a PDF summary or Excel workbook |

### 2. Predictive Modeling

| Capability | Detail |
|---|---|
| Model | Automated Linear Regression via scikit-learn |
| Preprocessing | Feature scaling with StandardScaler, 80/20 train/test split |
| Evaluation | R², RMSE, MAE displayed after training |
| Interpretability | Per-feature coefficients and intercept returned alongside metrics |

### 3. Report Generation

| Capability | Detail |
|---|---|
| PDF report | Formatted executive summary of metadata and insights, built with fpdf2 |
| Excel workbook | Cleaned dataset plus summary statistics, multi-sheet, built with openpyxl |

### Cross-cutting

| | |
|---|---|
| 🎨 Custom theme | Dark graphite palette, gradient header, hover-lift cards — hand-written CSS |
| 📊 Data Health Score | Single 0–100 metric combining completeness and duplication penalty |
| 🛡️ Fully offline | No API key, no external service — every feature computes locally |
| 📤 Export everywhere | PDF and Excel output |

---

## Architecture

```
              User (Browser)
        Streamlit UI + custom CSS
                    │
                    ▼
        ┌───────────────────────┐
        │        app.py         │
        │  upload · sidebar ·   │
        │  page flow · session  │
        └───────────┬───────────┘
                     │
   ┌─────────┬───────┼───────┬─────────────┐
   ▼         ▼       ▼       ▼             ▼
┌────────┐┌────────┐┌──────────┐┌──────────┐┌─────────────────┐
│data_   ││data_   ││analytics ││visualizer││ml_engine /       │
│loader  ││cleaner ││          ││          ││report_generator  │
└────────┘└────────┘└──────────┘└──────────┘└─────────────────┘
```

**Flow:** `app.py` handles file upload and sidebar controls, then dispatches sequentially into each module: `data_loader` → `data_cleaner` → `analytics` → `visualizer` / `ml_engine` → `report_generator`. Each module only depends on `pandas`/`numpy`/its own third-party library — no module imports another module.

**Why it's structured this way:** every stage of the pipeline is an independently testable pure function. Adding a new chart type or a new cleaning strategy touches exactly one file.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit ≥1.32, custom CSS injection |
| UI Style | Dark graphite theme, gradient header, hover-lift metric cards |
| Data | Pandas ≥2.2, NumPy ≥1.26 |
| Charts | Plotly Express — bar, line, scatter, histogram, box, pie, heatmap, treemap, sunburst |
| Machine Learning | scikit-learn (LinearRegression, train_test_split, StandardScaler) |
| PDF | fpdf2 |
| Excel | openpyxl |
| Deployment | Streamlit Community Cloud |

### Why these choices

| Decision | Reasoning |
|---|---|
| Streamlit over a custom frontend | File uploads, charts, and download buttons ship in days rather than weeks; the re-run-on-interaction trade-off is handled with `st.session_state`. |
| Rule-based insights over an LLM call | Skew, correlation, and category-dominance detection are deterministic statistics — no API key, no latency, no quota, and the app works fully offline. |
| Plotly over Matplotlib | Interactive by default (hover, zoom, pan) and themes cleanly against the dark background. |
| fpdf2 over a heavier PDF library | Lightweight, dependency-free PDF generation sufficient for a structured executive summary. |
| scikit-learn's plain LinearRegression | Fast to train, fully interpretable coefficients, and a strong baseline before reaching for heavier models. |

---

## Data Pipeline

The AI Data Analyst is the core feature, and it runs a small pipeline end to end.

```
Upload (CSV / XLSX)
    │
    ▼
Load with Pandas  →  encoding auto-fallback
    │
    ▼
Clean  →  drop duplicates · fill nulls (Mean/Mode / Drop Rows / None)
    │
    ▼
Profile  →  rows, columns, missing values, duplicates, Data Health Score
    │
    ▼
Insights  →  skew, correlation, dominant category → recommendations
    │
    ▼
Visualize  →  9 Plotly chart types, cleaned data flows through automatically
    │
    ▼
Model  →  Linear Regression, R² / RMSE / MAE
    │
    ▼
Export  →  PDF summary / Excel workbook
```

### Cleaning flows into everything downstream

The cleaned DataFrame is held in `st.session_state`, so a decision made in the sidebar (say, filling missing values with the median) is the exact data used by the charts, the insights, the model, and the exported files. There's no re-uploading and no stale copies.

---

## Project Structure

```
AI_CSV_Analytics_Pro/
├── app.py                       Shell: upload, sidebar, page flow
├── styles.css                   Dark enterprise theme
│
├── modules/                     One file per pipeline stage
│   ├── __init__.py
│   ├── data_loader.py           CSV/Excel ingestion, encoding fallback
│   ├── data_cleaner.py          Deduplication, missing-value handling, date parsing
│   ├── analytics.py             Metadata, summary stats, rule-based insights
│   ├── visualizer.py            Plotly chart rendering (9 chart types)
│   ├── ml_engine.py             Automated Linear Regression
│   └── report_generator.py      PDF and Excel export
│
├── assets/                      Screenshots
├── requirements.txt             Python dependencies
└── README.md
```

---

## Getting Started

### Prerequisites

| Requirement | Version | Required? |
|---|---|---|
| Python | 3.9+ | Yes |
| pip | Latest | Yes |

### Manual setup

**1. Clone and enter the project**
```bash
git clone https://github.com/ayeshamumtaz1057/AI_CSV_Analytics_Pro.git
cd AI_CSV_Analytics_Pro
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv

.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run**
```bash
streamlit run app.py
```

No environment variables or API keys are needed — every feature computes locally.

---

## Deployment

### Streamlit Community Cloud (free)

1. Push this repository to GitHub as public.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **Create app**.
3. Repository `ayeshamumtaz1057/AI_CSV_Analytics_Pro`, branch `main`, main file `app.py`.
4. Deploy.

No secrets need to be configured — this app has no external service dependency.

---

## Troubleshooting

### Setup

| Error | Fix |
|---|---|
| `'python' is not recognized` | Reinstall Python and tick **Add Python to PATH**, or use `py` on Windows |
| `ModuleNotFoundError: No module named 'streamlit'` | Virtual environment isn't active — activate it, then reinstall requirements |
| `ModuleNotFoundError: No module named 'sklearn'` | `scikit-learn` missing from `requirements.txt` — reinstall dependencies |

### Runtime

| Error | Fix |
|---|---|
| `FPDFException: Not enough horizontal space to render a single character` | `multi_cell()` wasn't passed `new_x="LMARGIN", new_y="NEXT"` — the cursor isn't reset between lines |
| `TypeError: ... got an unexpected keyword argument` | A module's function signature doesn't match how `app.py` calls it |
| `AttributeError: 'tuple' object has no attribute 'copy'` | `load_file()`/`clean_dataset()` return tuples — unpack them (`df, error = load_file(...)`) instead of assigning directly |
| Chart fails with `ValueError: ... requires an 'x' column` | Different chart types need different column selections — check the required fields for that chart type |
| `could not convert string to float` in regression | A non-numeric column was selected as a target or feature |

### Git & GitHub

| Error | Fix |
|---|---|
| `fatal: pathspec 'add' did not match any files` | Command typed twice — it's just `git add .` |
| `! [rejected] main -> main (fetch first)` | Remote has commits you don't — `git pull origin main --rebase` then `git push` |
| `Support for password authentication was removed` | Use a Personal Access Token: Settings → Developer settings → Tokens (classic) → scope `repo` |

### Deployment

| Error | Fix |
|---|---|
| `Main file does not exist` | `app.py` is nested one folder deep — re-upload the folder's contents |
| App shows old code after pushing | Confirm the push landed on GitHub (check the file in the browser), then **Manage app → Reboot app**, then hard-refresh the browser |

---

## FAQ

**Do I need to pay for anything?**
No. Streamlit Cloud hosting is free, and every library used is open source.

**Is my data sent anywhere?**
No. Files are processed entirely in memory on the machine running the app; nothing is uploaded to any external service.

**Can I add an LLM-backed insights layer later?**
Yes — the current `generate_ai_insights()` function in `analytics.py` is rule-based and fully self-contained. Swapping in an API call would mean editing that one function without touching any other module.

**What happens with a very large file?**
Everything runs in memory via Pandas, so very large files are bounded by available RAM rather than by the app itself.

**How many people can use it at once?**
Streamlit Cloud's free tier handles a handful of concurrent users comfortably; heavier concurrent use would call for a dedicated deployment.

---

## What I Learned

**Streamlit's execution model.** The entire script re-runs on every interaction. Knowing when to hold state in `st.session_state` was the difference between an app that reprocessed the same file on every widget click and one that felt instant.

**Return-type contracts matter more than they seem to.** Several real bugs in this project came from a module returning a tuple while the caller expected a single value (or vice versa). Testing each module's actual signature directly — rather than assuming it matched the call site — caught issues that were invisible from reading the code alone.

**Design your failure modes.** `load_file()` and `run_linear_regression()` both return structured `{"success": False, "error": "..."}`-style results instead of raising, so the UI can show a clear message instead of crashing.

**A clean module boundary pays off.** Because every stage of the pipeline only imports `pandas`/`numpy`/its own library — never another module — adding the Visual Analytics and Predictive Modeling sections to `app.py` was a local, low-risk change that didn't touch cleaning, loading, or export logic at all.

---

## Roadmap

- [ ] Additional regression algorithms (Random Forest, Gradient Boosting)
- [ ] Classification support alongside regression
- [ ] Persistent history via SQLite
- [ ] Docker containerization
- [ ] Optional LLM-backed narrative insights as an upgrade over the rule-based engine
- [ ] Unit tests and CI pipeline

---

## Contributing

Contributions are welcome.

```bash
git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature
```

Please keep the one-module-per-pipeline-stage contract — each module in `modules/` should only depend on `pandas`/`numpy`/its own third-party library, never on another module.

### Adding a new chart type

```python
# in modules/visualizer.py, inside render_chart()
elif chart_type == "Your Chart Type":
    if not x:
        raise ValueError("Your Chart Type requires an 'x' column.")
    fig = px.your_chart_function(df, x=x, y=y, title=title, template=DARK_TEMPLATE)
```

Then add `"Your Chart Type"` to the `CHART_TYPES` list — it appears in the chart-type dropdown automatically.

---

## License

Distributed under the MIT License. See `LICENSE` for details.

---

## Acknowledgements

- **Streamlit** — the framework the app is built on
- **scikit-learn** — the modeling engine
- **Plotly** — interactive visualization

---

## Author

**Ayesha Mumtaz**

⭐ Star this repo if you found it useful
