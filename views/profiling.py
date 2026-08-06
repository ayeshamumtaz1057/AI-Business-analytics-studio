import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from core import profiling, state
from core.theme import page_header, kpi_card, plotly_layout

page_header("Data Profiling", "Automatic quality assessment of the active dataset.", "🔍")
if not state.require_data():
    st.stop()

df = state.active_df()
o = profiling.overview(df)
score = profiling.quality_score(df)

cols = st.columns(6)
cards = [("Rows", f"{o['rows']:,}", "📋"), ("Columns", f"{o['columns']}", "🧱"),
         ("Duplicate rows", f"{o['duplicate_rows']:,}", "👯"),
         ("Missing cells", f"{o['missing_pct']:.2f}%", "🕳️"),
         ("Memory", f"{o['memory_mb']:.2f} MB", "💾"),
         ("Quality score", f"{score}/100", "🏅")]
for c, (l, v, i) in zip(cols, cards):
    with c:
        kpi_card(l, v, None, i, help_text="")
st.write("")

t1, t2, t3, t4, t5 = st.tabs(["Columns", "Missing values", "Numeric statistics",
                              "Correlations", "Distributions"])

with t1:
    prof = profiling.column_profile(df)
    st.dataframe(prof, use_container_width=True, hide_index=True)
    st.download_button("⬇ Download profile (CSV)", prof.to_csv(index=False),
                       "column_profile.csv", "text/csv")

with t2:
    miss = profiling.missing_summary(df)
    if miss.empty:
        st.success("No missing values anywhere in this dataset.")
    else:
        c1, c2 = st.columns([1, 1.2])
        c1.dataframe(miss, use_container_width=True, hide_index=True)
        fig = px.bar(miss.head(20), x="Missing %", y="Column", orientation="h")
        c2.plotly_chart(plotly_layout(fig, 420, legend=False), use_container_width=True)

with t3:
    stats = profiling.numeric_stats(df)
    if stats.empty:
        st.info("No numeric columns found.")
    else:
        st.dataframe(stats, use_container_width=True)

with t4:
    corr, strong = profiling.correlations(df, threshold=0.4)
    if corr.empty:
        st.info("Need at least two numeric columns for a correlation analysis.")
    else:
        c1, c2 = st.columns([1.3, 1])
        fig = px.imshow(corr, text_auto=True, aspect="auto", zmin=-1, zmax=1,
                        color_continuous_scale="RdBu_r")
        c1.plotly_chart(plotly_layout(fig, 460, legend=False), use_container_width=True)
        c2.markdown("**Strongest relationships**")
        c2.dataframe(strong.head(15), use_container_width=True, hide_index=True)

with t5:
    num = df.select_dtypes(include=np.number).columns.tolist()
    cat = [c for c in df.columns if c not in num]
    c1, c2 = st.columns(2)
    if num:
        col = c1.selectbox("Numeric column", num)
        fig = px.histogram(df, x=col, nbins=45, marginal="box", opacity=.85)
        c1.plotly_chart(plotly_layout(fig, 380, legend=False), use_container_width=True)
    if cat:
        col2 = c2.selectbox("Categorical column", cat)
        vc = df[col2].astype(str).value_counts().head(15).reset_index()
        vc.columns = [col2, "count"]
        fig2 = px.bar(vc, x="count", y=col2, orientation="h")
        c2.plotly_chart(plotly_layout(fig2, 380, legend=False), use_container_width=True)
