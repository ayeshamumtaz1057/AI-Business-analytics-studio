import numpy as np
import pandas as pd
import streamlit as st

from core import cleaning, state, db, auth
from core.theme import page_header
from core.utils import text_columns

page_header("Smart Data Cleaning", "One-click fixes. Every action is logged and reversible.", "🧹")
if not state.require_data():
    st.stop()

name = state.active_name()
df = state.active_df()
st.session_state.setdefault("_undo", {})

if st.session_state.pop("_flash", None):
    st.success(st.session_state.get("clean_log", {}).get(name, ["Done"])[-1])

c1, c2, c3 = st.columns([1, 1, 2])
c1.metric("Rows", f"{len(df):,}")
c2.metric("Columns", df.shape[1])
c3.metric("Nulls", f"{int(df.isna().sum().sum()):,}")


def apply(new_df, msg):
    st.session_state["_undo"][name] = df.copy()
    state.update(name, new_df, msg)
    db.log(auth.current_user(), "clean", f"{name}: {msg}")
    st.session_state["_flash"] = msg
    st.rerun()


tabs = st.tabs(["Duplicates", "Missing values", "Text & whitespace", "Dates",
                "Outliers", "Types", "Columns"])

with tabs[0]:
    subset = st.multiselect("Consider only these columns (blank = all)", list(df.columns))
    keep = st.radio("Keep", ["first", "last"], horizontal=True)
    st.caption(f"{int(df.duplicated(subset=subset or None).sum()):,} duplicate rows detected.")
    if st.button("Remove duplicates", type="primary"):
        apply(*cleaning.remove_duplicates(df, subset or None, keep))

with tabs[1]:
    strategy = st.selectbox("Strategy", ["drop_rows", "drop_columns", "mean", "median",
                                         "mode", "zero", "ffill", "bfill", "constant"])
    cols = st.multiselect("Columns (blank = all)", list(df.columns))
    fill = st.text_input("Constant value", "Unknown") if strategy == "constant" else None
    if st.button("Apply", type="primary", key="mv"):
        apply(*cleaning.handle_missing(df, strategy, cols or None, fill))

with tabs[2]:
    txt = text_columns(df)
    c1, c2 = st.columns(2)
    with c1:
        tc = st.multiselect("Text columns for case fix", txt)
        mode = st.selectbox("Case", ["title", "lower", "upper", "capitalize"])
        if st.button("Fix text case", key="case") and tc:
            apply(*cleaning.fix_text_case(df, tc, mode))
    with c2:
        wc = st.multiselect("Columns to trim (blank = all text)", txt, key="trim")
        if st.button("Trim whitespace", key="trimb"):
            apply(*cleaning.trim_whitespace(df, wc or None))

with tabs[3]:
    dc = st.multiselect("Date columns", list(df.columns))
    out = st.radio("Output", ["datetime", "string"], horizontal=True)
    fmt = st.text_input("String format", "%Y-%m-%d") if out == "string" else "%Y-%m-%d"
    if st.button("Standardize dates", type="primary") and dc:
        apply(*cleaning.standardize_dates(df, dc, out, fmt))

with tabs[4]:
    num = df.select_dtypes(include=np.number).columns.tolist()
    oc = st.multiselect("Numeric columns", num)
    method = st.selectbox("Method", ["iqr", "zscore"])
    factor = st.slider("Sensitivity factor", 1.0, 5.0, 1.5, 0.1)
    action = st.radio("Action", ["remove", "clip"], horizontal=True)
    if st.button("Handle outliers", type="primary") and oc:
        apply(*cleaning.remove_outliers(df, oc, method, factor, action))

with tabs[5]:
    c1, c2 = st.columns(2)
    col = c1.selectbox("Column", list(df.columns), key="tcol")
    target = c2.selectbox("Convert to", ["numeric", "integer", "datetime", "string",
                                         "category", "boolean"])
    if st.button("Convert type", type="primary"):
        apply(*cleaning.convert_types(df, col, target))

with tabs[6]:
    st.caption("Rename columns")
    renames = {}
    grid = st.columns(3)
    for i, c in enumerate(df.columns):
        with grid[i % 3]:
            renames[c] = st.text_input(str(c), str(c), key=f"rn_{i}")
    b1, b2, b3 = st.columns(3)
    if b1.button("Apply renames", type="primary"):
        apply(*cleaning.rename_columns(df, renames))
    if b2.button("snake_case all names"):
        apply(*cleaning.clean_column_names(df))
    drop = st.multiselect("Drop columns", list(df.columns))
    if b3.button("Drop selected") and drop:
        apply(*cleaning.drop_columns(df, drop))

st.divider()
c1, c2 = st.columns([1, 3])
if c1.button("↩ Undo last action") and st.session_state["_undo"].get(name) is not None:
    state.update(name, st.session_state["_undo"].pop(name), "Undo")
    st.rerun()
log = st.session_state["clean_log"].get(name, [])
with c2.expander(f"Cleaning log ({len(log)} actions)", expanded=bool(log)):
    for i, m in enumerate(log, 1):
        st.write(f"{i}. {m}")

st.subheader("Preview")
st.dataframe(state.active_df().head(30), use_container_width=True)
