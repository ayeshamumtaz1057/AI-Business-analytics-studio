import pandas as pd
import streamlit as st

from core import charts, forecasting, state
from core.kpis import timeseries, money, prepare
from core.theme import page_header, kpi_card

page_header("Forecasting", "Project future performance with confidence bands.", "🔮")
if not state.require_data():
    st.stop()

mapping = state.mapping()
df = prepare(state.active_df(), mapping)

if not mapping.get("date"):
    st.warning("Map a date column in the Upload Center to enable forecasting.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
metric = c1.selectbox("Metric", [r for r in ("revenue", "profit", "quantity") if mapping.get(r)])
gran = c2.selectbox("Granularity", ["Daily", "Weekly", "Monthly"])
freq = {"Daily": "D", "Weekly": "W", "Monthly": "ME"}[gran]
horizon = c3.select_slider("Forecast horizon (periods)",
                           options=[7, 14, 30, 60, 90, 180, 365], value=90)
model = c4.selectbox("Model", forecasting.MODELS)

ts = timeseries(df, mapping, freq, metric)
if len(ts) < 10:
    st.warning("Not enough history — at least 10 periods are needed.")
    st.stop()

try:
    fc, met = forecasting.forecast(ts, int(horizon), model, freq)
except Exception as e:
    st.error(f"Forecast failed: {e}")
    st.stop()

uplift = st.slider("What-if scenario — adjust forecast by %", -50, 100, 0, 5)
if uplift:
    fc = forecasting.scenario(fc, uplift)

k = st.columns(4)
with k[0]:
    kpi_card(f"Forecast total ({horizon} periods)", money(fc["forecast"].sum()), None, "🔮")
with k[1]:
    g = met.get("Expected growth %")
    kpi_card("Expected growth", f"{g:+.1f}%" if g == g else "—",
             None, "📈")
with k[2]:
    kpi_card("Avg. per period", money(fc["forecast"].mean()), None, "📅")
with k[3]:
    mape = met.get("MAPE %")
    kpi_card("Backtest MAPE", f"{mape:.1f}%" if mape else "—", None, "🎯",
             help_text="lower is better")

st.write("")
st.plotly_chart(charts.forecast_chart(ts, fc, height=440), use_container_width=True)

c1, c2 = st.columns([1.3, 1])
with c1:
    st.subheader("Forecast table")
    show = fc.copy()
    show["date"] = show["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(show.round(2), use_container_width=True, hide_index=True, height=320)
    st.download_button("⬇ Download forecast (CSV)", fc.to_csv(index=False),
                       f"forecast_{metric}_{horizon}.csv", "text/csv")
with c2:
    st.subheader("Model diagnostics")
    for kk, vv in met.items():
        st.write(f"**{kk}** — {vv:,.2f}" if isinstance(vv, float) else f"**{kk}** — {vv}")
    st.caption("The shaded band is a 95% confidence interval that widens with horizon. "
               "Forecasts assume the historical pattern continues; they cannot anticipate "
               "price changes, campaigns or market shocks.")
