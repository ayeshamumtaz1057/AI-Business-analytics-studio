import pandas as pd
import streamlit as st

from core import auth, db, loaders, state
from core.config import ROLES, ROLE_LABELS, SAMPLE_DIR
from core.theme import page_header

page_header("Upload Center", "CSV · Excel · JSON · ZIP · SQL — with encoding and delimiter auto-detection.", "📤")

tab_file, tab_sql, tab_sample = st.tabs(["📁 Files", "🗄️ SQL database", "🎁 Sample data"])

with tab_file:
    files = st.file_uploader(
        "Drop one or more files",
        type=["csv", "txt", "xlsx", "xls", "xlsm", "json", "zip", "db", "sqlite", "sqlite3"],
        accept_multiple_files=True)

    if files:
        prog = st.progress(0.0, text="Reading files…")
        for i, f in enumerate(files, start=1):
            prog.progress(i / len(files), text=f"Processing {f.name}…")
            try:
                frames, meta = loaders.load_any(f.name, f.getvalue())
            except Exception as e:
                st.error(f"**{f.name}** — {e}")
                continue

            st.markdown(f"#### {f.name}")
            if meta:
                st.caption(" · ".join(f"{k}: {v}" for k, v in meta.items())[:300])

            for name, d in frames.items():
                key = f"{name}"
                with st.expander(f"`{key}` — {len(d):,} rows × {d.shape[1]} cols", expanded=True):
                    for level, msg in loaders.validate(d):
                        {"ok": st.success, "warn": st.warning, "error": st.error}[level](msg, icon=None)
                    st.dataframe(d.head(8), use_container_width=True, hide_index=True)
                    if st.button(f"➕ Load '{key}' into workspace", key=f"add_{f.name}_{key}"):
                        reg = state.register(key, d)
                        db.add_dataset(auth.current_user(), reg, f.name,
                                       f.name.split(".")[-1], len(d), d.shape[1])
                        db.log(auth.current_user(), "upload", reg)
                        st.success(f"'{reg}' is now the active dataset.")
                        st.rerun()
        prog.empty()

with tab_sql:
    st.caption("Connect to SQLite, PostgreSQL, MySQL or any SQLAlchemy-supported database.")
    uri = st.text_input("Connection URI",
                        placeholder="postgresql+psycopg2://user:pass@host:5432/dbname "
                                    "or sqlite:///data/app.db")
    c1, c2 = st.columns(2)
    if c1.button("🔌 Connect and list tables", type="primary") and uri:
        try:
            st.session_state["_sql_tables"] = loaders.sql_tables(uri, limit=5000)
            st.success(f"Connected — {len(st.session_state['_sql_tables'])} table(s) found.")
        except Exception as e:
            st.error(f"Connection failed: {e}")

    for tname, d in (st.session_state.get("_sql_tables") or {}).items():
        with st.expander(f"`{tname}` — {len(d):,} rows"):
            st.dataframe(d.head(6), use_container_width=True, hide_index=True)
            if st.button(f"➕ Load '{tname}'", key=f"sql_{tname}"):
                reg = state.register(tname, d)
                db.add_dataset(auth.current_user(), reg, uri, "sql", len(d), d.shape[1])
                st.rerun()

    st.divider()
    custom = st.text_area("Or run a custom query", "SELECT * FROM table_name LIMIT 1000", height=90)
    if st.button("▶ Run query") and uri:
        try:
            d = loaders.sql_query(uri, custom)
            st.dataframe(d.head(20), use_container_width=True)
            reg = state.register("sql_query_result", d)
            st.success(f"Loaded {len(d):,} rows as '{reg}'.")
        except Exception as e:
            st.error(e)

with tab_sample:
    st.caption("A realistic 2024 e-commerce dataset — 9,000 orders, 24 products, 11 markets, "
               "with deliberate duplicates, nulls and anomalies so every module has something to do.")
    if st.button("⚡ Load Sales_2024.csv", type="primary"):
        name, d = loaders.load_sample()
        reg = state.register(name, d)
        db.add_dataset(auth.current_user(), reg, "sample", "sample", len(d), d.shape[1])
        st.success(f"Loaded '{reg}'.")
        st.rerun()
    p = SAMPLE_DIR / "sales_2024.csv"
    if p.exists():
        st.download_button("⬇ Download the sample CSV", p.read_bytes(), "sales_2024.csv", "text/csv")

# ---- column mapping -------------------------------------------------------
if state.active_df() is not None:
    st.divider()
    st.subheader("Column mapping")
    st.caption("Every analytics module reads these semantic roles. Auto-detected values are "
               "pre-filled — adjust anything that looks wrong.")
    df = state.active_df()
    current = st.session_state["mapping"].get(state.active_name(), {})
    options = ["— none —"] + [str(c) for c in df.columns]
    picked, cols = {}, st.columns(5)
    for i, role in enumerate(ROLES):
        cur = current.get(role)
        idx = options.index(str(cur)) if cur is not None and str(cur) in options else 0
        with cols[i % 5]:
            v = st.selectbox(ROLE_LABELS[role], options, index=idx, key=f"map_{role}")
        picked[role] = None if v == "— none —" else v
    if st.button("💾 Save mapping", type="primary"):
        state.set_mapping(picked)
        st.success("Mapping saved.")
