import pandas as pd
import streamlit as st

from core import ai, auth, db, nlq, state
from core.theme import page_header

page_header("Chat with your Data", "Ask questions in plain English — no SQL required.", "💬")
if not state.require_data():
    st.stop()

df, mapping = state.active_df(), state.mapping()

with st.expander("Suggested questions", expanded=not st.session_state["messages"]):
    cols = st.columns(3)
    for i, s in enumerate(nlq.SUGGESTIONS):
        if cols[i % 3].button(s, key=f"sug_{i}", use_container_width=True):
            st.session_state["_pending"] = s
            st.rerun()

for m in st.session_state["messages"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("table") is not None:
            st.dataframe(m["table"], use_container_width=True, hide_index=True)

prompt = st.chat_input("e.g. Which category is most profitable?") or st.session_state.pop("_pending", None)

if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                answer, table = nlq.answer(prompt, df, mapping)
            except Exception as e:
                answer, table = f"I hit an error running that: `{e}`", None
        st.markdown(answer)
        if table is not None and len(table):
            st.dataframe(table, use_container_width=True, hide_index=True)
    st.session_state["messages"].append({"role": "assistant", "content": answer, "table": table})
    u = auth.current_user()
    db.add_chat(u, state.active_name(), "user", prompt)
    db.add_chat(u, state.active_name(), "assistant", answer[:2000])

if st.session_state["messages"]:
    c1, c2 = st.columns([1, 4])
    if c1.button("🗑 Clear chat"):
        st.session_state["messages"] = []
        st.rerun()
    transcript = "\n\n".join(f"**{m['role']}**: {m['content']}" for m in st.session_state["messages"])
    c2.download_button("⬇ Download transcript", transcript, "chat_transcript.md", "text/markdown")

if not ai.available():
    st.caption("⚪ Offline mode: answers come from the built-in intent engine. "
               "Add a Gemini API key in Settings for free-form questions.")
