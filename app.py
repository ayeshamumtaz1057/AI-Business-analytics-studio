"""AI Business Analytics Studio — application entry point.

Run with:  streamlit run app.py
"""
import streamlit as st

from core.config import APP_NAME, APP_ICON, VERSION
from core import auth, db, state, theme

st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON,
                   layout="wide", initial_sidebar_state="expanded")

db.engine()
auth.ensure_demo_user()
state.init()
theme.inject()


def _login_screen():
    st.markdown(f"<h1 style='text-align:center;margin-top:4rem'>{APP_ICON} {APP_NAME}</h1>"
                "<p style='text-align:center;color:#93a2c4'>Upload your business data. "
                "Get dashboards, AI insights, forecasts and reports in minutes.</p>",
                unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        tab_login, tab_reg, tab_reset = st.tabs(["Sign in", "Create account", "Reset password"])

        with tab_login:
            u = st.text_input("Username", key="li_u", placeholder="demo")
            p = st.text_input("Password", type="password", key="li_p", placeholder="demo123")
            c1, c2 = st.columns(2)
            if c1.button("Sign in", type="primary", use_container_width=True):
                if auth.verify(u, p):
                    auth.login(u.strip().lower())
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            if c2.button("Continue as guest", use_container_width=True):
                auth.login("guest")
                st.rerun()
            st.caption("Demo account — username `demo`, password `demo123`")

        with tab_reg:
            nu = st.text_input("Choose a username", key="rg_u")
            ne = st.text_input("Email (optional)", key="rg_e")
            np_ = st.text_input("Password", type="password", key="rg_p")
            np2 = st.text_input("Confirm password", type="password", key="rg_p2")
            if st.button("Create account", type="primary", use_container_width=True):
                if np_ != np2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = auth.create_user(nu, np_, ne)
                    (st.success if ok else st.error)(msg)
                    if ok:
                        auth.login(nu.strip().lower())
                        st.rerun()

        with tab_reset:
            st.caption("Local demo reset — in production this would email a signed token.")
            ru = st.text_input("Username", key="rs_u")
            rp = st.text_input("New password", type="password", key="rs_p")
            if st.button("Reset password", use_container_width=True):
                import pandas as pd  # noqa
                exists = not db.query_df("SELECT id FROM users WHERE username=:u",
                                         {"u": ru.strip().lower()}).empty
                if exists and len(rp) >= 6:
                    auth.set_password(ru.strip().lower(), rp)
                    st.success("Password updated. You can sign in now.")
                else:
                    st.error("Unknown user, or password shorter than 6 characters.")


if not auth.current_user():
    _login_screen()
    st.stop()

# --------------------------------------------------------------------------
PAGES = {
    "Overview": [
        st.Page("views/home.py", title="Home", icon=":material/home:", default=True),
        st.Page("views/dashboard.py", title="Dashboard", icon=":material/dashboard:"),
    ],
    "Data": [
        st.Page("views/upload.py", title="Upload Center", icon=":material/upload:"),
        st.Page("views/profiling.py", title="Data Profiling", icon=":material/find_in_page:"),
        st.Page("views/cleaning.py", title="Data Cleaning", icon=":material/cleaning_services:"),
        st.Page("views/transform.py", title="Transformation", icon=":material/transform:"),
    ],
    "Analytics": [
        st.Page("views/visualizations.py", title="Visualizations", icon=":material/bar_chart:"),
        st.Page("views/insights.py", title="AI Insights", icon=":material/auto_awesome:"),
        st.Page("views/chat.py", title="Chat with Data", icon=":material/forum:"),
        st.Page("views/forecasting.py", title="Forecasting", icon=":material/trending_up:"),
        st.Page("views/anomalies.py", title="Anomaly Detection", icon=":material/warning:"),
        st.Page("views/customers.py", title="Customer Analytics", icon=":material/group:"),
        st.Page("views/products.py", title="Product Analytics", icon=":material/inventory_2:"),
    ],
    "Tools": [
        st.Page("views/sql.py", title="SQL Workspace", icon=":material/terminal:"),
        st.Page("views/reports.py", title="Report Generator", icon=":material/description:"),
        st.Page("views/exports.py", title="Export Data", icon=":material/download:"),
    ],
    "System": [
        st.Page("views/history.py", title="Project History", icon=":material/history:"),
        st.Page("views/settings.py", title="Settings", icon=":material/settings:"),
        st.Page("views/admin.py", title="Admin Panel", icon=":material/shield:"),
        st.Page("views/docs.py", title="Documentation", icon=":material/menu_book:"),
    ],
}

with st.sidebar:
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:10px;padding:2px 0 10px'>"
        f"<div style='font-size:26px'>{APP_ICON}</div>"
        f"<div><div style='font-weight:700;line-height:1.15'>AI Business</div>"
        f"<div style='font-weight:700;line-height:1.15'>Analytics Studio</div></div></div>",
        unsafe_allow_html=True)

nav = st.navigation(PAGES, position="sidebar")

with st.sidebar:
    st.divider()
    ds = state.names()
    st.caption("ACTIVE DATASET")
    if ds:
        state.dataset_picker(label="", label_visibility="collapsed")
        df = state.active_df()
        st.caption(f"{len(df):,} rows × {df.shape[1]} cols")
    else:
        st.caption("None loaded")
        if st.button("⚡ Load demo data", use_container_width=True):
            from core.loaders import load_sample
            name, sdf = load_sample()
            state.register(name, sdf)
            db.log(auth.current_user(), "load_demo", name)
            st.rerun()
    st.divider()
    from core import ai
    st.caption(("🟢 Gemini connected" if ai.available() else "⚪ Offline analyst mode"))
    st.caption(f"Signed in as **{auth.current_user()}** · v{VERSION}")
    if st.button("Log out", use_container_width=True):
        auth.logout()
        st.rerun()

nav.run()
