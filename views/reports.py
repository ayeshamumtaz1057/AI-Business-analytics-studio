from datetime import datetime

import streamlit as st

from core import auth, charts, db, insights, reports, state
from core.kpis import compute, timeseries, breakdown, prepare, money
from core.products import performance, category_performance
from core.customers import rfm
from core.theme import page_header

page_header("Report Generator", "Board-ready PDF, Excel, CSV and PowerPoint deliverables.", "📄")
if not state.require_data():
    st.stop()

mapping = state.mapping()
df = prepare(state.active_df(), mapping)
name = state.active_name()

c1, c2 = st.columns([2, 1])
title = c1.text_input("Report title", f"Business Performance Report — {name}")
fmt = c2.selectbox("Format", ["PDF", "Excel", "CSV bundle", "PowerPoint"])

sections = st.multiselect(
    "Include sections",
    ["KPI summary", "AI insights", "Charts", "Product performance",
     "Category performance", "Top customers", "Raw data sample"],
    default=["KPI summary", "AI insights", "Charts", "Product performance"])

use_ai = st.checkbox("Generate fresh AI insights for this report", value=True)

if st.button("🛠 Build report", type="primary"):
    with st.spinner("Assembling report…"):
        insights_md = ""
        if "AI insights" in sections:
            cached = st.session_state["ai_cache"].get(name)
            if use_ai or not cached:
                insights_md, engine = insights.generate_report(df, mapping)
                st.session_state["ai_cache"][name] = {"text": insights_md, "engine": engine}
            else:
                insights_md = cached["text"]
        insights_md = st.session_state.get("_report_insights", insights_md)

        tables = {}
        if "Product performance" in sections:
            tables["Product Performance"] = performance(df, mapping).head(40)
        if "Category performance" in sections:
            tables["Category Performance"] = category_performance(df, mapping)
        if "Top customers" in sections:
            r = rfm(df, mapping)
            if not r.empty:
                tables["Top Customers"] = r.head(40)[
                    ["Customer", "Recency", "Frequency", "Monetary", "Segment"]]
        if "Raw data sample" in sections:
            tables["Data Sample"] = df.head(40)

        figs = []
        if "Charts" in sections:
            ts = timeseries(df, mapping, "ME")
            if not ts.empty:
                figs.append(charts.revenue_trend(ts))
            b = breakdown(df, mapping, "category", "revenue", 8)
            if not b.empty:
                figs.append(charts.donut(b["label"].astype(str), b["value"],
                                         "Total", money(b["value"].sum())))

        stamp = datetime.now().strftime("%Y%m%d_%H%M")
        user = auth.current_user()

        if fmt == "PDF":
            data = reports.build_pdf(df, mapping, title, insights_md, tables, figs)
            fname, mime = f"report_{stamp}.pdf", "application/pdf"
        elif fmt == "Excel":
            sheets = dict(tables)
            sheets["Full Data"] = df
            data = reports.build_excel(sheets, compute(df, mapping))
            fname = f"report_{stamp}.xlsx"
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif fmt == "PowerPoint":
            data = reports.build_pptx(title, compute(df, mapping), insights_md, figs)
            fname = f"report_{stamp}.pptx"
            mime = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            if data is None:
                st.error("PowerPoint export needs `python-pptx` — run `pip install python-pptx`.")
                st.stop()
        else:
            import io, zipfile
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                z.writestr("data.csv", df.to_csv(index=False))
                for tname, t in tables.items():
                    z.writestr(f"{tname.lower().replace(' ', '_')}.csv", t.to_csv(index=False))
                if insights_md:
                    z.writestr("insights.md", insights_md)
            data, fname, mime = buf.getvalue(), f"report_{stamp}.zip", "application/zip"

        path = reports.save(data, fname)
        db.add_report(user, title, fmt, path)
        db.log(user, "report", f"{fmt}: {title}")
        st.session_state["_last_report"] = (data, fname, mime)
    st.success("Report ready.")

last = st.session_state.get("_last_report")
if last:
    data, fname, mime = last
    st.download_button(f"⬇ Download {fname}", data, fname, mime, type="primary")

st.divider()
st.subheader("Report history")
hist = db.recent("reports", auth.current_user(), 15)
if hist.empty:
    st.caption("No reports yet.")
else:
    st.dataframe(hist[["name", "kind", "created_at"]], use_container_width=True, hide_index=True)
