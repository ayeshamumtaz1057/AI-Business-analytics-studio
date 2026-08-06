import streamlit as st

from core import auth, db, state
from core.theme import page_header

page_header("Project History", "Everything you have uploaded, asked and generated.", "🕘")
user = auth.current_user()

t1, t2, t3, t4 = st.tabs(["Datasets", "Reports", "Chat history", "Activity log"])

with t1:
    d = db.recent("datasets", user, 50)
    if d.empty:
        st.caption("No datasets recorded yet.")
    else:
        st.dataframe(d[["name", "source", "rows", "cols", "created_at"]],
                     use_container_width=True, hide_index=True)

with t2:
    r = db.recent("reports", user, 50)
    if r.empty:
        st.caption("No reports generated yet.")
    else:
        st.dataframe(r[["name", "kind", "path", "created_at"]],
                     use_container_width=True, hide_index=True)
        for _, row in r.head(10).iterrows():
            try:
                with open(row["path"], "rb") as f:
                    st.download_button(f"⬇ {row['name']} ({row['kind']})", f.read(),
                                       row["path"].split("/")[-1], key=f"dl_{row['id']}")
            except Exception:
                pass

with t3:
    c = db.recent("chat", user, 100)
    if c.empty:
        st.caption("No conversations yet.")
    else:
        for _, row in c.iterrows():
            who = "🧑" if row["role"] == "user" else "🤖"
            st.markdown(f"{who} **{row['role']}** · <span style='color:#93a2c4'>"
                        f"{row['created_at']}</span><br>{str(row['message'])[:600]}",
                        unsafe_allow_html=True)
            st.divider()

with t4:
    h = db.recent("history", user, 100)
    if h.empty:
        st.caption("No activity recorded.")
    else:
        st.dataframe(h[["action", "detail", "created_at"]],
                     use_container_width=True, hide_index=True)

st.divider()
if st.button("🗑 Clear my history"):
    for t in ("datasets", "reports", "chat", "history", "queries"):
        db.execute(f"DELETE FROM {t} WHERE username=:u", {"u": user})
    st.success("History cleared.")
    st.rerun()
