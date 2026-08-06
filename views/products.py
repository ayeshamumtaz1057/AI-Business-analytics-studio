import plotly.express as px
import streamlit as st

from core import charts, products, state
from core.kpis import money, prepare
from core.theme import page_header, kpi_card, plotly_layout

page_header("Product Analytics", "Best sellers, slow movers, margins and inventory actions.", "📦")
if not state.require_data():
    st.stop()

mapping = state.mapping()
df = prepare(state.active_df(), mapping)
perf = products.performance(df, mapping)

if perf.empty:
    st.warning("Map a **product** column in the Upload Center to unlock product analytics.")
    st.stop()

c = st.columns(4)
with c[0]:
    kpi_card("Products", f"{len(perf):,}", None, "📦")
with c[1]:
    kpi_card("Class A items", f"{int((perf.get('ABC Class') == 'A').sum())}", None, "🏆",
             help_text="drive 80% of revenue")
with c[2]:
    top = perf.iloc[0]
    kpi_card("Best seller", str(top["Product"])[:22], None, "⭐",
             help_text=money(top.get("Revenue", 0)))
with c[3]:
    if "Margin %" in perf:
        best_m = perf.nlargest(1, "Margin %").iloc[0]
        kpi_card("Highest margin", str(best_m["Product"])[:22], None, "💎",
                 help_text=f"{best_m['Margin %']:.1f}%")
st.write("")

t1, t2, t3, t4 = st.tabs(["Performance", "Best & slow movers", "Categories", "Inventory actions"])

with t1:
    st.dataframe(perf.round(2), use_container_width=True, hide_index=True, height=430)
    st.download_button("⬇ Download product performance", perf.to_csv(index=False),
                       "product_performance.csv", "text/csv")

with t2:
    best, slow = products.movers(perf, 10)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### 🏆 Best sellers")
        st.plotly_chart(charts.hbar(best["Product"].astype(str), best["Revenue"],
                                    color="#22C55E"), use_container_width=True)
    with c2:
        st.markdown("##### 🐌 Slow movers")
        st.plotly_chart(charts.hbar(slow["Product"].astype(str), slow["Revenue"],
                                    color="#EF4444"), use_container_width=True)
    if "Margin %" in perf and "Revenue" in perf:
        st.markdown("##### Revenue vs margin")
        fig = px.scatter(perf, x="Revenue", y="Margin %", size="Revenue",
                         color=perf.get("ABC Class"), hover_name="Product", size_max=45,
                         opacity=.8)
        st.plotly_chart(plotly_layout(fig, 420), use_container_width=True)

with t3:
    cat = products.category_performance(df, mapping)
    if cat.empty:
        st.info("No category column mapped.")
    else:
        c1, c2 = st.columns([1, 1])
        fig = px.bar(cat, x="Category", y="Revenue", text_auto=".3s")
        c1.plotly_chart(plotly_layout(fig, 380, legend=False), use_container_width=True)
        if "Margin %" in cat:
            fig2 = px.bar(cat.sort_values("Margin %"), x="Margin %", y="Category",
                          orientation="h", text_auto=".1f")
            c2.plotly_chart(plotly_layout(fig2, 380, legend=False), use_container_width=True)
        st.dataframe(cat, use_container_width=True, hide_index=True)

with t4:
    sug = products.inventory_suggestions(perf, 20)
    st.caption("Heuristic recommendations based on ABC class, margin and sales recency.")
    st.dataframe(sug.round(2), use_container_width=True, hide_index=True)
