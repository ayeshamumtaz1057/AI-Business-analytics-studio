import streamlit as st
import pandas as pd

from core import auth, db, state
from core.theme import page_header, kpi_card, insight_card
from core.kpis import compute, format_kpi
from core.config import APP_NAME

user = auth.current_user()
page_header(f"Welcome back, {user.title()} 👋",
            "Here's what's happening with your data today.")

df = state.active_df()
if df is not None:
    k = compute(df, state.mapping())
    cols = st.columns(4)
    for c, name in zip(cols, ["Total Revenue", "Total Profit", "Total Orders", "Total Customers"]):
        with c:
            kpi_card(name, format_kpi(name, k[name]["value"]), k[name]["delta"])
    st.write("")

st.subheader("Quick actions")
qa = st.columns(4)
actions = [
    ("📤 Upload New Data", "Add CSV, Excel, JSON or SQL", "views/upload.py"),
    ("📊 Open Dashboard", "KPIs, trends and breakdowns", "views/dashboard.py"),
    ("✨ Generate AI Insights", "Executive summary and actions", "views/insights.py"),
    ("💬 Chat with your Data", "Ask questions in plain English", "views/chat.py"),
]
for col, (title, sub, target) in zip(qa, actions):
    with col:
        st.markdown(f"<div class='panel'><b>{title}</b><br>"
                    f"<span style='color:#93a2c4;font-size:.85rem'>{sub}</span></div>",
                    unsafe_allow_html=True)
        if st.button("Open", key=f"qa_{target}", use_container_width=True):
            st.switch_page(target)

st.write("")
left, right = st.columns([1.4, 1])

with left:
    st.subheader("Recent uploads")
    ups = db.recent("datasets", user, 8)
    if ups.empty:
        st.caption("No uploads yet — start from the Upload Center.")
    else:
        st.dataframe(ups[["name", "source", "rows", "cols", "created_at"]],
                     use_container_width=True, hide_index=True)

    st.subheader("Recent reports")
    reps = db.recent("reports", user, 6)
    if reps.empty:
        st.caption("No reports generated yet.")
    else:
        st.dataframe(reps[["name", "kind", "created_at"]],
                     use_container_width=True, hide_index=True)

with right:
    st.subheader("Loaded in this session")
    if not state.names():
        st.caption("No datasets in memory.")
        if st.button("⚡ Load demo dataset", type="primary"):
            from core.loaders import load_sample
            n, sdf = load_sample()
            state.register(n, sdf)
            st.rerun()
    for n in state.names():
        d = st.session_state["datasets"][n]
        active = " · active" if n == state.active_name() else ""
        st.markdown(f"<div class='insight i-info'><div class='t'>{n}{active}</div>"
                    f"<div class='b'>{len(d):,} rows × {d.shape[1]} columns</div></div>",
                    unsafe_allow_html=True)

    st.subheader("Activity")
    hist = db.recent("history", user, 8)
    if hist.empty:
        st.caption("Nothing logged yet.")
    else:
        for _, r in hist.iterrows():
            st.markdown(f"<span class='pill'>{r['created_at'][11:16]}</span> "
                        f"{r['action']} <span style='color:#93a2c4'>{str(r['detail'])[:40]}</span>",
                        unsafe_allow_html=True)
