import pandas as pd
import streamlit as st

from core import state
from core.theme import page_header, kpi_card, insight_card
from core.kpis import compute, format_kpi, timeseries, breakdown, prepare, money
from core import charts, insights

page_header("Dashboard", "Live business overview built from your active dataset.", "📊")

if not state.require_data():
    st.stop()

raw = state.active_df()
mapping = state.mapping()
df = prepare(raw, mapping)

# ---- filters --------------------------------------------------------------
f1, f2, f3 = st.columns([1.4, 1, 1])
date_c = mapping.get("date")
if date_c and df[date_c].notna().any():
    lo, hi = df[date_c].min().date(), df[date_c].max().date()
    rng = f1.date_input("Date range", (lo, hi), min_value=lo, max_value=hi)
    if isinstance(rng, tuple) and len(rng) == 2:
        df = df[(df[date_c].dt.date >= rng[0]) & (df[date_c].dt.date <= rng[1])]
freq_label = f2.selectbox("Granularity", ["Daily", "Weekly", "Monthly"], index=0)
freq = {"Daily": "D", "Weekly": "W", "Monthly": "ME"}[freq_label]
cat_c = mapping.get("category")
if cat_c:
    opts = sorted(df[cat_c].dropna().astype(str).unique())
    chosen = f3.multiselect("Category", opts, default=[])
    if chosen:
        df = df[df[cat_c].astype(str).isin(chosen)]

if df.empty:
    st.warning("No rows match the current filters.")
    st.stop()

# ---- KPI row --------------------------------------------------------------
k = compute(df, mapping)
order = ["Total Revenue", "Total Profit", "Total Orders", "Total Customers",
         "Avg. Order Value", "Profit Margin"]
icons = ["💰", "📈", "🧾", "👥", "🛒", "🎯"]
cols = st.columns(6)
for c, name, ic in zip(cols, order, icons):
    with c:
        kpi_card(name, format_kpi(name, k[name]["value"]), k[name]["delta"], ic)
st.write("")

tgt = k["Target Achievement"]["value"]
if tgt == tgt:
    st.progress(min(float(tgt) / 100, 1.0),
                text=f"Sales target achievement — {tgt:.1f}% of the configured annual target")
st.write("")

# ---- charts ---------------------------------------------------------------
c1, c2, c3 = st.columns([1.35, 1, 1])

with c1:
    st.markdown("##### Revenue Trend")
    ts = timeseries(df, mapping, freq)
    if ts.empty:
        st.info("Map a date and revenue column in Settings to see the trend.")
    else:
        st.plotly_chart(charts.revenue_trend(ts), use_container_width=True)

with c2:
    st.markdown("##### Sales by Category")
    b = breakdown(df, mapping, "category", "revenue", top=8)
    if b.empty:
        st.info("No category column mapped.")
    else:
        st.plotly_chart(charts.donut(b["label"].astype(str), b["value"],
                                     "Total", money(b["value"].sum())),
                        use_container_width=True)

with c3:
    st.markdown("##### AI Insights")
    for title, body, kind in insights.quick_cards(df, mapping):
        insight_card(title, body, kind)
    if st.button("View full insights", use_container_width=True, type="primary"):
        st.switch_page("views/insights.py")

st.write("")
d1, d2, d3 = st.columns([1.1, 1, 1])

with d1:
    st.markdown("##### Top 10 Products by Revenue")
    p = breakdown(df, mapping, "product", "revenue", top=10)
    if p.empty:
        st.info("No product column mapped.")
    else:
        st.plotly_chart(charts.hbar(p["label"].astype(str), p["value"]),
                        use_container_width=True)

with d2:
    st.markdown("##### Sales by Region")
    r = breakdown(df, mapping, "region", "revenue", top=40)
    if r.empty:
        st.info("No region column mapped.")
    else:
        try:
            st.plotly_chart(charts.choropleth(r.rename(columns={"label": "loc", "value": "val"}),
                                              "loc", "val"), use_container_width=True)
        except Exception:
            st.plotly_chart(charts.hbar(r["label"].astype(str).head(10), r["value"].head(10)),
                            use_container_width=True)

with d3:
    st.markdown("##### Revenue Forecast")
    ts = timeseries(df, mapping, "D")
    if len(ts) < 12:
        st.info("Not enough history to forecast.")
    else:
        from core.forecasting import forecast
        try:
            fc, met = forecast(ts, horizon=90)
            st.plotly_chart(charts.forecast_chart(ts, fc), use_container_width=True)
            g = met.get("Expected growth %")
            st.caption(f"Next 90 days ≈ **{money(met['Forecast total'])}**"
                       + (f" ({g:+.1f}% vs prior 90 days)" if g == g else ""))
        except Exception as e:
            st.info(f"Forecast unavailable: {e}")
