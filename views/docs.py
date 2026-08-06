import streamlit as st

from core.config import APP_NAME, VERSION, SAMPLE_DIR
from core.theme import page_header

page_header("Documentation", f"{APP_NAME} v{VERSION} — user guide.", "📚")

t1, t2, t3, t4 = st.tabs(["Getting started", "Module guide", "FAQ", "Example data"])

with t1:
    st.markdown("""
### 1. Load data
Go to **Upload Center** and drop a CSV, Excel workbook, JSON file, ZIP of datasets, or connect
a SQL database. The app auto-detects encoding and delimiter, validates the file and shows a preview.
No data of your own? Click **Load demo dataset** for a realistic 9,000-row sales file.

### 2. Confirm the column mapping
Every analytics module reads *semantic roles* — date, revenue, profit, customer, product,
category, region — rather than hard-coded column names. Roles are auto-detected from your
headers and dtypes; review them at the bottom of the Upload Center and fix anything wrong.
**This single step is what makes the dashboard, forecasts and RFM work on any dataset.**

### 3. Clean, then explore
Run **Data Profiling** to see quality issues, fix them in **Smart Data Cleaning** (every action
is logged and undoable), then open the **Dashboard**.

### 4. Ask, forecast, report
Use **AI Insights** for an executive summary, **Chat with your Data** for ad-hoc questions,
**Forecasting** to project 30–365 days ahead, and **Report Generator** to export a PDF,
Excel workbook, CSV bundle or PowerPoint deck.
""")

with t2:
    modules = {
        "Upload Center": "CSV, Excel, JSON, ZIP and SQL ingestion with validation, encoding and delimiter detection.",
        "Data Profiling": "Shape, dtypes, nulls, duplicates, memory, numeric statistics, correlations and a 0–100 quality score.",
        "Smart Data Cleaning": "Duplicates, missing values (9 strategies), text case, whitespace, date standardisation, outliers, type conversion, renaming.",
        "Data Transformation": "Group-by, pivot tables, merges, column splitting, feature engineering, binning, scaling and encoding.",
        "Dashboard": "8 KPIs with period-over-period deltas, revenue trend, category donut, top products, regional map and an embedded forecast.",
        "Visualizations": "14 chart types with filters, zoom and HTML/PNG download.",
        "AI Insights": "Executive summary, trends, best and worst products, opportunities, risks, customer insights and prioritised recommendations.",
        "Chat with your Data": "Natural-language questions answered with Gemini-generated pandas, or an offline intent engine.",
        "Forecasting": "Ridge / Random Forest / moving average / linear trend, 7–365 period horizons, confidence bands and what-if scenarios.",
        "Anomaly Detection": "Z-score, IQR, rolling z-score and Isolation Forest over trends and transactions.",
        "Customer Analytics": "RFM scoring, 11 segments, CLV estimate, churn risk bands and cohort retention.",
        "Product Analytics": "Best sellers, slow movers, margins, ABC classification and inventory actions.",
        "SQL Workspace": "Query every loaded dataset with real SQL, save queries, export results.",
        "Report Generator": "PDF, Excel, CSV bundle and PowerPoint with KPIs, charts and AI narrative.",
        "Project History": "Datasets, reports, chat transcripts and a full activity log.",
        "Settings": "Theme, language, Gemini key and model, column mapping, account management.",
        "Admin Panel": "User management, dataset and report oversight, usage analytics.",
    }
    for k, v in modules.items():
        st.markdown(f"**{k}** — {v}")

with t3:
    faqs = [
        ("Do I need a Gemini API key?",
         "No. Without one the app runs in offline analyst mode: a deterministic rule engine "
         "writes the insights and answers chat questions. Add a key in Settings for free-form "
         "narrative AI."),
        ("Is my data uploaded anywhere?",
         "Files stay in the Streamlit session and the local SQLite database. Only small "
         "aggregated summaries — never raw rows — are sent to Gemini, and only when you have "
         "configured a key."),
        ("Why is a KPI showing a dash?",
         "The role it depends on is not mapped. For example Profit Margin needs both a revenue "
         "and a profit (or cost) column. Set them in the Upload Center."),
        ("How are period-over-period deltas calculated?",
         "The mapped date range is split in half and the second half is compared with the first, "
         "so the comparison adapts to whatever range you filter to."),
        ("How accurate are the forecasts?",
         "They extrapolate historical trend and seasonality and report a backtest MAPE. They "
         "cannot know about upcoming campaigns, price changes or market shocks — treat them as "
         "a planning baseline, not a promise."),
        ("Can I use PostgreSQL instead of SQLite?",
         "Yes — any SQLAlchemy URI works in the Upload Center's SQL tab, and the app's own "
         "metadata store can be repointed in `core/config.py`."),
    ]
    for q, a in faqs:
        with st.expander(q):
            st.write(a)

with t4:
    st.markdown("The bundled demo file `sales_2024.csv` contains 9,000+ orders across 24 products, "
                "6 categories and 11 markets for calendar year 2024 — including deliberate "
                "duplicates, nulls and revenue spikes so every module has something to find.")
    p = SAMPLE_DIR / "sales_2024.csv"
    if p.exists():
        st.download_button("⬇ Download sales_2024.csv", p.read_bytes(), "sales_2024.csv", "text/csv")
    st.code("order_id, order_date, customer_id, customer_segment, product, category,\n"
            "region, channel, quantity, unit_price, discount, cost, revenue, profit",
            language="text")
