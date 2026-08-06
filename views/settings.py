import streamlit as st

from core import ai, auth, db, state
from core.config import GEMINI_MODELS, ROLES, ROLE_LABELS
from core.theme import page_header

page_header("Settings", "Appearance, AI model, data mapping and account.", "⚙️")

t1, t2, t3, t4 = st.tabs(["Appearance", "AI model", "Data mapping", "Account"])

with t1:
    st.selectbox("Theme", ["Dark (default)", "Light"], key="theme_choice")
    st.caption("Streamlit's own theme lives in `.streamlit/config.toml`. "
               "Switch to light mode there or via the ☰ menu → Settings → Theme.")
    st.selectbox("Language", ["English", "اردو (Urdu)", "Español", "Français", "العربية"],
                 key="lang", help="UI strings are English-only in this release; "
                                  "AI responses follow the selected language.")
    st.number_input("Annual revenue target (for target achievement KPI)",
                    min_value=0.0, value=8_000_000.0, step=100_000.0, key="target_revenue")

with t2:
    key = st.text_input("Gemini API key", type="password",
                        value=st.session_state.get("gemini_key", ""),
                        help="Stored in this session only. For deployments set the "
                             "GEMINI_API_KEY environment variable or a Streamlit secret.")
    model = st.selectbox("Model", GEMINI_MODELS,
                         index=GEMINI_MODELS.index(st.session_state.get("ai_model", GEMINI_MODELS[0])))
    c1, c2 = st.columns(2)
    if c1.button("💾 Save AI settings", type="primary"):
        st.session_state["gemini_key"] = key
        st.session_state["ai_model"] = model
        st.success("Saved.")
    if c2.button("🔌 Test connection"):
        with st.spinner("Calling Gemini…"):
            out = ai.generate("Reply with exactly: connection ok")
        if out:
            st.success(f"Connected — model replied: {out[:80]}")
        else:
            st.error(f"No response. {st.session_state.get('ai_error', 'Check the key and network.')}")
    st.caption("Without a key the app runs in **offline analyst mode** — every module still "
               "works, using a deterministic rule engine instead of an LLM.")

with t3:
    if state.active_df() is None:
        st.info("Load a dataset to edit its column mapping.")
    else:
        df = state.active_df()
        current = st.session_state["mapping"].get(state.active_name(), {})
        options = ["— none —"] + [str(c) for c in df.columns]
        picked, cols = {}, st.columns(2)
        for i, role in enumerate(ROLES):
            cur = current.get(role)
            idx = options.index(str(cur)) if cur is not None and str(cur) in options else 0
            with cols[i % 2]:
                v = st.selectbox(ROLE_LABELS[role], options, index=idx, key=f"set_map_{role}")
            picked[role] = None if v == "— none —" else v
        if st.button("💾 Save mapping", type="primary", key="save_map2"):
            state.set_mapping(picked)
            st.success("Mapping updated.")

with t4:
    user = auth.current_user()
    st.write(f"Signed in as **{user}**")
    info = db.query_df("SELECT username, email, role, created_at FROM users WHERE username=:u",
                       {"u": user})
    if not info.empty:
        st.dataframe(info, use_container_width=True, hide_index=True)
    st.markdown("##### Change password")
    p1 = st.text_input("New password", type="password", key="np1")
    p2 = st.text_input("Confirm", type="password", key="np2")
    if st.button("Update password"):
        if p1 != p2 or len(p1) < 6:
            st.error("Passwords must match and be at least 6 characters.")
        else:
            auth.set_password(user, p1)
            st.success("Password updated.")
    st.divider()
    if st.button("🧹 Clear session datasets"):
        for k in ("datasets", "mapping", "clean_log", "ai_cache"):
            st.session_state[k] = {}
        st.session_state["active"] = None
        st.rerun()
