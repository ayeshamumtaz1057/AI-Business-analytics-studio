import numpy as np
import pandas as pd
import streamlit as st

from core import anomalies, charts, state
from core.kpis import timeseries, prepare, money
from core.theme import page_header

page_header("Anomaly Detection", "Catch unusual spikes, drops and suspicious transactions.", "🚨")
if not state.require_data():
    st.stop()

mapping = state.mapping()
df = prepare(state.active_df(), mapping)

t1, t2 = st.tabs(["Time series anomalies", "Transaction anomalies"])

with t1:
    if not mapping.get("date"):
        st.info("Map a date column to scan trends for anomalies.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        metric = c1.selectbox("Metric", [r for r in ("revenue", "profit", "quantity")
                                         if mapping.get(r)])
        gran = c2.selectbox("Granularity", ["Daily", "Weekly", "Monthly"])
        method = c3.selectbox("Method", anomalies.METHODS, index=2)
        sens = c4.slider("Sensitivity (σ)", 1.5, 5.0, 3.0, 0.1)

        ts = timeseries(df, mapping, {"Daily": "D", "Weekly": "W", "Monthly": "ME"}[gran], metric)
        if ts.empty:
            st.info("No time series available for this metric.")
        else:
            found = anomalies.detect_timeseries(ts, method, sens)
            st.plotly_chart(charts.anomaly_chart(ts, found, height=420), use_container_width=True)
            st.info(anomalies.summarize(found))
            if not found.empty:
                out = found.copy()
                out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")
                out["value"] = out["value"].round(2)
                st.dataframe(out[["date", "value", "score", "Direction", "Severity"]],
                             use_container_width=True, hide_index=True)
                st.download_button("⬇ Download anomalies", out.to_csv(index=False),
                                   "anomalies.csv", "text/csv")

with t2:
    num = df.select_dtypes(include=np.number).columns.tolist()
    if not num:
        st.info("No numeric columns to scan.")
    else:
        c1, c2 = st.columns([2, 1])
        cols = c1.multiselect("Columns to scan", num,
                              default=[c for c in [mapping.get("revenue"),
                                                   mapping.get("quantity")] if c] or num[:2])
        contamination = c2.slider("Expected anomaly rate", 0.005, 0.10, 0.02, 0.005)
        if st.button("🔎 Scan transactions", type="primary") and cols:
            res = anomalies.detect_transactions(df, cols, contamination)
            if res.empty:
                st.success("No suspicious transactions found.")
            else:
                st.warning(f"{len(res):,} unusual transactions flagged "
                           f"({len(res)/len(df)*100:.2f}% of rows). Review before acting — "
                           f"statistical outliers are not proof of fraud.")
                st.dataframe(res.head(200), use_container_width=True)
                st.download_button("⬇ Download flagged rows", res.to_csv(index=False),
                                   "flagged_transactions.csv", "text/csv")
