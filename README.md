# 📊 AI CSV Analytics Pro

**An automated data-cleaning, visualization, and predictive-modeling workspace for any CSV or Excel file — running locally, no data ever leaves your machine.**

[Overview](#overview) · [Features](#features) · [Architecture](#architecture) · [Tech Stack](#tech-stack) · [Cleaning & Insights Pipeline](#cleaning--insights-pipeline) · [Getting Started](#getting-started) · [Deployment](#deployment) · [Troubleshooting](#troubleshooting)

---

## Overview

AI CSV Analytics Pro turns a raw spreadsheet into a finished analysis in one pass. Upload a CSV or Excel file, choose how missing data and duplicates should be handled, and the app profiles the dataset, surfaces rule-based insights, renders interactive charts, trains a regression model, and exports everything as a polished PDF or Excel report — all in a single dashboard.

### The Problem

Getting from "raw spreadsheet" to "shareable analysis" usually means bouncing between a notebook for cleaning, a separate tool for charts, and a third for the writeup — each with its own setup, and no shared state between them.

### The Solution

AI CSV Analytics Pro collapses that workflow into four steps, all in one Streamlit app:

1. **Upload** — drop in a `.csv`, `.xlsx`, or `.xls` file
2. **Clean** — choose duplicate handling and a missing-value strategy from the sidebar
3. **Explore** — view metadata, a data health score, rule-based insights, and interactive charts
4. **Export** — download a PDF executive summary or a full Excel workbook

Everything runs locally in your Python environment. No file ever leaves your machine unless you explicitly export it.

---

## Features

| Capability | Detail |
|---|---|
| **Multi-format ingestion** | CSV, XLSX, XLS, with automatic encoding fallback (UTF-8 → Latin-1 → CP1252) |
| **Automated cleaning** | Drop duplicates, and handle missing values via **Mean/Mode imputation**, **row dropping**, or leave as-is |
| **Data profiling** | Row/column counts, missing-cell percentage, duplicate count, and a computed **Data Health Score (0–100)** |
| **Rule-based AI insights** | Skew detection, correlation discovery between numeric columns, dominant-category flags, and plain-language recommendations — no API key required |
| **Interactive visualization** | 9 Plotly chart types: Bar, Line, Scatter, Histogram, Box Plot, Pie, Correlation Heatmap, Treemap, Sunburst |
| **Predictive modeling** | Automated Linear Regression via scikit-learn, with train/test split, feature scaling, and R² / RMSE / MAE evaluation |
| **Export hub** | Download a formatted **PDF report** or a **multi-sheet Excel workbook** (cleaned data + summary statistics) |
| **Dark enterprise theme** | Hand-written CSS over Streamlit's defaults — graphite cards, gradient accents, hover states |

---

## Architecture

```
              User (Browser)
        Streamlit UI + custom CSS
                    │
                    ▼
        ┌───────────────────────┐
        │        app.py         │
        │  sidebar · page flow  │
        └───────────┬───────────┘
                     │
   ┌─────────┬───────┼───────┬─────────────┐
   ▼         ▼       ▼       ▼             ▼
┌────────┐┌────────┐┌──────────┐┌──────────┐┌─────────────────┐
│data_   ││data_   ││analytics ││visualizer││ml_engine /       │
│loader  ││cleaner ││          ││          ││report_generator  │
└────────┘└────────┘└──────────┘└──────────┘└─────────────────┘
```

**Flow:** `app.py` handles file upload, then hands the raw DataFrame to `data_cleaner`, the cleaned result to `analytics` for profiling and insights, `visualizer` for charts, `ml_engine` for regression, and `report_generator` for PDF/Excel export. Each module is self-contained and only depends on `pandas`/`numpy`/its own third-party library — no module reaches into another.

**Why it's structured this way:** every stage of the pipeline (load → clean → analyze → visualize → model → export) is a separate, independently testable function. Swapping the cleaning strategy or adding a chart type touches exactly one file.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit ≥1.32, custom CSS injection |
| Data | Pandas ≥2.2, NumPy ≥1.26 |
| Charts | Plotly Express (9 chart types) |
| Machine Learning | scikit-learn (Linear Regression, train/test split, StandardScaler) |
| PDF Generation | fpdf2 |
| Excel Generation | openpyxl |

### Why these choices

| Decision | Reasoning |
|---|---|
| **Streamlit over a custom frontend** | File uploads, interactive charts, and download buttons ship in a fraction of the time versus hand-rolling a React app. |
| **Rule-based insights, not an LLM call** | Skew, correlation, and dominant-category detection are deterministic statistics — no API key, no latency, no quota limits, and the app works fully offline. |
| **Plotly over Matplotlib** | Interactive by default (hover, zoom, pan) and themes cleanly against the app's dark background. |
| **fpdf2 over a heavier PDF library** | Lightweight, dependency-free PDF generation that's more than sufficient for a structured executive summary. |

---

## Cleaning & Insights Pipeline

```
Upload (CSV / XLSX / XLS)
        │
        ▼
Load with Pandas — encoding auto-fallback
        │
        ▼
Clean — drop duplicates · impute (median/mode) · drop rows · or leave as-is
        │
        ▼
Profile — rows, columns, missing %, duplicates, Data Health Score
        │
        ▼
Insights — skew, correlation, dominant category, recommendations
        │
        ▼
Visualize — 9 chart types, rendered from the cleaned data
        │
        ▼
Model — Linear Regression, train/test split, R² / RMSE / MAE
        │
        ▼
Export — PDF summary or Excel workbook
```

**Cleaning flows into everything downstream.** The cleaned DataFrame is held in `st.session_state`, so a decision made in the sidebar (say, filling missing values with the median) is the exact data used by the charts, the insights, and the exported files — no re-uploading, no stale copies.

---

## Project Structure

```
ai-csv-analytics-pro/
├── app.py                       Main Streamlit app: upload, sidebar, page flow
├── styles.css                   Dark enterprise theme
├── requirements.txt             Python dependencies
│
├── modules/
│   ├── __init__.py
│   ├── data_loader.py           CSV/Excel ingestion with encoding fallback
│   ├── data_cleaner.py          Deduplication, missing-value handling, date parsing
│   ├── analytics.py             Metadata, summary stats, rule-based insights
│   ├── visualizer.py            Plotly chart rendering (9 chart types)
│   ├── ml_engine.py             Automated Linear Regression
│   └── report_generator.py      PDF and Excel export
│
└── README.md
```

---

## Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.9+ |
| pip | Latest |

### Installation

```bash
git clone https://github.com/your-username/ai-csv-analytics-pro.git
cd ai-csv-analytics-pro
pip install -r requirements.txt
streamlit run app.py
```

Open the app at **http://localhost:8501**.

---

## Deployment

### Streamlit Community Cloud (free)

1. Push this repository to GitHub as public.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **Create app**.
3. Select your repository, branch `main`, main file `app.py`.
4. Deploy.

No secrets or API keys are required — every feature runs on local computation.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'sklearn'` | `scikit-learn` missing from `requirements.txt` or not installed — run `pip install -r requirements.txt` again |
| `FPDFException: Not enough horizontal space to render a single character` | Occurs if `multi_cell()` isn't passed `new_x="LMARGIN", new_y="NEXT"` — the cursor isn't reset between lines |
| `TypeError: ... got an unexpected keyword argument` | A module's function signature doesn't match how `app.py` calls it — check `clean_dataset()` and `generate_excel_report()` argument names |
| `AttributeError: 'tuple' object has no attribute 'copy'` | `load_file()` and `clean_dataset()` both return tuples — make sure their results are unpacked (`df, error = load_file(...)`) rather than assigned directly |
| Charts fail with `ValueError: ... requires an 'x' column` | Some chart types need specific column selections — Bar/Histogram/Pie need `x`, Line/Scatter/Box need both `x` and `y` |
| `could not convert string to float` in regression | A non-numeric column was selected as a feature or target — `run_linear_regression` only accepts numeric columns |

---

## Roadmap

- [ ] Multiple regression algorithms (Random Forest, XGBoost)
- [ ] Classification support alongside regression
- [ ] Scheduled/batch processing for multiple files
- [ ] User-configurable chart color themes
- [ ] Unit test suite and CI pipeline

---

## Contributing

Contributions are welcome.

```bash
git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature
```

Please keep the one-function-per-responsibility contract in `modules/` — each module should stay independently testable.

---

## License

Distributed under the MIT License. See `LICENSE` for details.
