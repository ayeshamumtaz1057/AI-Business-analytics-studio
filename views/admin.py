import pandas as pd
import plotly.express as px
import streamlit as st

from core import auth, db
from core.theme import page_header, kpi_card, plotly_layout

page_header("Admin Panel", "Users, datasets and platform usage.", "🛡️")

if not auth.is_admin():
    st.warning("Admin access required. Sign in with the `demo` account to explore this panel.")
    st.stop()

users = db.query_df("SELECT username,email,role,created_at FROM users ORDER BY id DESC")
datasets = db.recent("datasets", None, 500)
reports = db.recent("reports", None, 500)
hist = db.recent("history", None, 1000)

c = st.columns(4)
with c[0]:
    kpi_card("Users", f"{len(users):,}", None, "👤")
with c[1]:
    kpi_card("Datasets", f"{len(datasets):,}", None, "🗂️")
with c[2]:
    kpi_card("Reports", f"{len(reports):,}", None, "📄")
with c[3]:
    kpi_card("Logged actions", f"{len(hist):,}", None, "⚡")
st.write("")

t1, t2, t3 = st.tabs(["Users", "Datasets & reports", "Usage"])

with t1:
    st.dataframe(users, use_container_width=True, hide_index=True)
    c1, c2, c3 = st.columns(3)
    tgt = c1.selectbox("User", users["username"].tolist() if not users.empty else [])
    role = c2.selectbox("Role", ["user", "admin"])
    if c3.button("Update role") and tgt:
        db.execute("UPDATE users SET role=:r WHERE username=:u", {"r": role, "u": tgt})
        st.rerun()
    if st.button("🗑 Delete selected user") and tgt and tgt != "demo":
        db.execute("DELETE FROM users WHERE username=:u", {"u": tgt})
        st.rerun()

with t2:
    st.markdown("##### Datasets")
    st.dataframe(datasets, use_container_width=True, hide_index=True, height=260)
    st.markdown("##### Reports")
    st.dataframe(reports, use_container_width=True, hide_index=True, height=260)

with t3:
    if hist.empty:
        st.caption("No activity yet.")
    else:
        h = hist.copy()
        h["day"] = pd.to_datetime(h["created_at"]).dt.date
        daily = h.groupby("day").size().reset_index(name="actions")
        st.plotly_chart(plotly_layout(px.bar(daily, x="day", y="actions"), 320, False),
                        use_container_width=True)
        byact = h["action"].value_counts().reset_index()
        byact.columns = ["action", "count"]
        c1, c2 = st.columns(2)
        c1.plotly_chart(plotly_layout(px.pie(byact, names="action", values="count", hole=.55), 340),
                        use_container_width=True)
        c2.dataframe(byact, use_container_width=True, hide_index=True)
        st.caption("AI calls appear as `ai_insights` and chat rows — use this to monitor "
                   "Gemini API consumption per user.")
