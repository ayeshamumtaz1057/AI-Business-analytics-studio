import pandas as pd
import plotly.express as px
import streamlit as st

from core import customers, state
from core.kpis import money, prepare
from core.theme import page_header, kpi_card, plotly_layout

page_header("Customer Analytics", "RFM segmentation, lifetime value and churn risk.", "👥")
if not state.require_data():
    st.stop()

mapping = state.mapping()
df = prepare(state.active_df(), mapping)

rfm = customers.rfm(df, mapping)
if rfm.empty:
    st.warning("Customer analytics needs **customer ID**, **date** and **revenue** columns mapped. "
               "Set them in the Upload Center.")
    st.stop()

s = customers.summary(rfm)
cols = st.columns(5)
cards = [("Customers", f"{s['Customers']:,}", "👥"),
         ("Repeat rate", f"{s['Repeat rate %']:.1f}%", "🔁"),
         ("Avg. CLV (12mo)", money(s["Avg CLV"]), "💎"),
         ("High churn risk", f"{s['High churn risk']:,}", "⚠️"),
         ("Top 10% rev. share", f"{s['Top 10% revenue share %']:.1f}%", "🏆")]
for c, (l, v, i) in zip(cols, cards):
    with c:
        kpi_card(l, v, None, i)
st.write("")

t1, t2, t3, t4 = st.tabs(["Segments", "RFM table", "Churn risk", "Cohort retention"])

with t1:
    seg = rfm.groupby("Segment").agg(Customers=("Customer", "count"),
                                     Revenue=("Monetary", "sum"),
                                     AvgCLV=("CLV (12mo est.)", "mean")).reset_index()
    seg = seg.sort_values("Revenue", ascending=False)
    c1, c2 = st.columns([1, 1])
    fig = px.treemap(seg, path=["Segment"], values="Revenue", color="Customers",
                     color_continuous_scale="Blues")
    c1.plotly_chart(plotly_layout(fig, 400, legend=False), use_container_width=True)
    fig2 = px.scatter(rfm, x="Recency", y="Frequency", size="Monetary", color="Segment",
                      hover_name="Customer", size_max=40, opacity=.75)
    c2.plotly_chart(plotly_layout(fig2, 400), use_container_width=True)
    st.dataframe(seg.round(2), use_container_width=True, hide_index=True)

with t2:
    st.dataframe(rfm.drop(columns=["FirstPurchase", "LastPurchase"]).round(2).head(500),
                 use_container_width=True, hide_index=True)
    st.download_button("⬇ Download RFM (CSV)", rfm.to_csv(index=False), "rfm.csv", "text/csv")

with t3:
    risk = rfm[rfm["Risk Band"] == "High"].nlargest(50, "Monetary")
    st.caption(f"{len(rfm[rfm['Risk Band']=='High']):,} customers are at high churn risk. "
               f"The {len(risk)} shown below are the most valuable — target them first.")
    st.dataframe(risk[["Customer", "Recency", "Frequency", "Monetary",
                       "CLV (12mo est.)", "Churn Risk %"]].round(2),
                 use_container_width=True, hide_index=True)
    band = rfm.groupby("Risk Band")["Monetary"].agg(["count", "sum"]).reset_index()
    band.columns = ["Risk Band", "Customers", "Revenue at stake"]
    fig = px.bar(band, x="Risk Band", y="Revenue at stake", color="Risk Band",
                 text_auto=".3s", category_orders={"Risk Band": ["Low", "Medium", "High"]})
    st.plotly_chart(plotly_layout(fig, 340, legend=False), use_container_width=True)

with t4:
    ret = customers.cohort_retention(df, mapping)
    if ret.empty:
        st.info("Not enough history for a cohort analysis.")
    else:
        fig = px.imshow(ret.iloc[:, :13], text_auto=".0f", aspect="auto",
                        color_continuous_scale="Blues",
                        labels=dict(x="Months since first purchase", y="Cohort", color="% retained"))
        st.plotly_chart(plotly_layout(fig, 430, legend=False), use_container_width=True)
