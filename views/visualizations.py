import numpy as np
import streamlit as st

from core import charts, state
from core.config import CHART_TYPES, AGGREGATIONS
from core.theme import page_header
from core.utils import text_columns

page_header("Interactive Visualizations", "14 chart types — zoom, filter, and download any figure.", "📈")
if not state.require_data():
    st.stop()

df = state.active_df()
num = df.select_dtypes(include=np.number).columns.tolist()
allc = list(df.columns)

c1, c2, c3, c4, c5, c6 = st.columns([1.2, 1, 1, 1, 1, .8])
kind = c1.selectbox("Chart type", CHART_TYPES)
needs_xy = kind in ("Scatter", "Bubble", "Box Plot")
x = c2.selectbox("X / Category", allc, index=0)
y = c3.selectbox("Y / Value", ["— count —"] + allc,
                 index=(allc.index(num[0]) + 1) if num else 0)
color = c4.selectbox("Colour / group", ["— none —"] + allc)
agg = c5.selectbox("Aggregation", AGGREGATIONS)
top_n = c6.number_input("Top N", 0, 100, 10 if kind in ("Bar", "Pie", "Donut", "Treemap") else 0)

with st.expander("Filters"):
    fdf = df.copy()
    cols = st.columns(3)
    for i, c in enumerate(text_columns(fdf)[:3]):
        opts = sorted(fdf[c].dropna().astype(str).unique())[:200]
        sel = cols[i].multiselect(str(c), opts, key=f"vf_{c}")
        if sel:
            fdf = fdf[fdf[c].astype(str).isin(sel)]
    if num:
        c = st.selectbox("Numeric range filter", ["— none —"] + num)
        if c != "— none —":
            lo, hi = float(fdf[c].min()), float(fdf[c].max())
            r = st.slider("Range", lo, hi, (lo, hi))
            fdf = fdf[(fdf[c] >= r[0]) & (fdf[c] <= r[1])]
    st.caption(f"{len(fdf):,} rows after filtering")

size = None
if kind == "Bubble":
    size = st.selectbox("Bubble size", num or allc)

try:
    fig = charts.build(fdf, kind, x=x, y=None if y == "— count —" else y,
                       color=None if color == "— none —" else color,
                       size=size, agg=agg, top_n=top_n or None, height=520)
    st.plotly_chart(fig, use_container_width=True)
    html = fig.to_html(include_plotlyjs="cdn")
    st.download_button("⬇ Download chart (interactive HTML)", html,
                       f"{kind.lower().replace(' ', '_')}.html", "text/html")
    st.caption("Use the camera icon in the chart toolbar to save a PNG.")
except Exception as e:
    st.warning(f"Cannot build this chart with the current selections — {e}")

st.divider()
st.subheader("Chart gallery")
st.caption("Quick auto-generated views of your data.")
g1, g2 = st.columns(2)
try:
    if num:
        with g1:
            st.plotly_chart(charts.build(fdf, "Histogram", x=num[0], height=300),
                            use_container_width=True)
        with g2:
            st.plotly_chart(charts.build(fdf, "Correlation Matrix", height=300),
                            use_container_width=True)
except Exception:
    pass
