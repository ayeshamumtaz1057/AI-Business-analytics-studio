import numpy as np
import pandas as pd
import streamlit as st

from core import state, transform
from core.config import AGGREGATIONS
from core.theme import page_header

page_header("Data Transformation", "Reshape, enrich and engineer features from your data.", "🔀")


def run(fn, *args, **kwargs):
    """Run a transformation, surfacing failures as a message instead of a crash."""
    try:
        out = fn(*args, **kwargs)
    except Exception as exc:
        st.error(f"That transformation could not be applied — {exc}")
        return None
    if isinstance(out, tuple):          # (dataframe, message)
        out, msg = out
        if msg:
            st.info(msg)
    return out
if not state.require_data():
    st.stop()

df = state.active_df()
name = state.active_name()
num = df.select_dtypes(include=np.number).columns.tolist()
cat = [c for c in df.columns if c not in num]

tabs = st.tabs(["Group By", "Pivot", "Merge", "Split column", "Feature engineering",
                "Binning", "Scaling", "Encoding", "Sort & filter"])
result = None

with tabs[0]:
    keys = st.multiselect("Group by", list(df.columns), default=cat[:1])
    vals = st.multiselect("Aggregate columns", num, default=num[:2])
    fn = st.selectbox("Function", AGGREGATIONS)
    if st.button("Run group by", type="primary") and keys and vals:
        result = run(transform.group_by, df, keys, {v: fn for v in vals})

with tabs[1]:
    c1, c2, c3, c4 = st.columns(4)
    idx = c1.selectbox("Rows", cat or list(df.columns), key="p_i")
    colm = c2.selectbox("Columns", [c for c in cat if c != idx] or list(df.columns), key="p_c")
    valc = c3.selectbox("Values", num or list(df.columns), key="p_v")
    fn2 = c4.selectbox("Aggregation", AGGREGATIONS, key="p_f")
    if st.button("Build pivot table", type="primary"):
        result = run(transform.pivot, df, idx, colm, valc, fn2)

with tabs[2]:
    others = [n for n in state.names() if n != name]
    if not others:
        st.info("Load a second dataset in the Upload Center to enable merges.")
    else:
        c1, c2, c3 = st.columns(3)
        right_name = c1.selectbox("Right dataset", others)
        right = st.session_state["datasets"][right_name]
        lk = c2.selectbox("Left key", list(df.columns))
        rk = c3.selectbox("Right key", list(right.columns))
        how = st.radio("Join type", ["inner", "left", "right", "outer"], horizontal=True)
        if lk and rk:
            same = df[lk].dtype == right[rk].dtype
            st.caption(f"Left key `{lk}` is *{df[lk].dtype}* · right key `{rk}` is "
                       f"*{right[rk].dtype}*"
                       + ("" if same else " — types differ, they will be reconciled automatically."))
        if st.button("Merge datasets", type="primary"):
            result = run(transform.merge, df, right, how, lk, rk)

with tabs[3]:
    c1, c2, c3 = st.columns(3)
    scol = c1.selectbox("Column", cat or list(df.columns), key="sp")
    sep = c2.text_input("Separator", " ")
    n = c3.number_input("Max splits", 1, 5, 1)
    if st.button("Split column", type="primary"):
        result = run(transform.split_column, df, scol, sep, int(n))

with tabs[4]:
    st.caption("Create new columns from expressions, ratios or date parts.")
    c1, c2 = st.columns(2)
    with c1:
        newname = st.text_input("New column name", "profit_margin")
        expr = st.text_input("Expression (pandas eval)", "profit / revenue * 100")
        if st.button("Create from expression", type="primary"):
            result = run(transform.formula_feature, df, newname, expr)
    with c2:
        dcol = st.selectbox("Date column for calendar features",
                            [c for c in df.columns], key="dfe")
        if st.button("Generate date features"):
            result = run(transform.date_features, df, dcol)

with tabs[5]:
    c1, c2, c3 = st.columns(3)
    bcol = c1.selectbox("Column", num or list(df.columns), key="bc")
    bins = c2.number_input("Bins", 2, 20, 5)
    method = c3.selectbox("Method", ["equal_width", "quantile"])
    if st.button("Create bins", type="primary") and num:
        result = run(transform.binning, df, bcol, int(bins), None, method)

with tabs[6]:
    scols = st.multiselect("Columns to scale", num, default=num[:2])
    smethod = st.selectbox("Scaler", ["standard", "minmax", "robust"])
    if st.button("Scale", type="primary") and scols:
        result = run(transform.scale, df, scols, smethod)

with tabs[7]:
    ecols = st.multiselect("Categorical columns", cat, default=cat[:1])
    emethod = st.selectbox("Encoding", ["onehot", "label", "frequency"])
    if st.button("Encode", type="primary") and ecols:
        result = run(transform.encode, df, ecols, emethod)

with tabs[8]:
    c1, c2, c3 = st.columns(3)
    sb = c1.selectbox("Sort by", ["— none —"] + list(df.columns))
    asc = c2.radio("Order", ["Ascending", "Descending"], horizontal=True) == "Ascending"
    lim = c3.number_input("Limit rows (0 = all)", 0, 1_000_000, 0)
    q = st.text_input("Filter query (pandas syntax)", placeholder="revenue > 500 and region == 'Germany'")
    if st.button("Apply", type="primary", key="sfb"):
        result = run(transform.sort_filter, df, None if sb == "— none —" else sb, asc,
                     q or None, lim or None)

if result is not None:
    st.session_state["_tf_result"] = result

res = st.session_state.get("_tf_result")
if res is not None:
    st.divider()
    st.subheader(f"Result — {len(res):,} rows × {res.shape[1]} columns")
    st.dataframe(res.head(40), use_container_width=True)
    c1, c2, c3 = st.columns(3)
    new_name = c1.text_input("Save as", f"{name} · transformed")
    if c2.button("💾 Save as new dataset", type="primary"):
        state.register(new_name, res)
        st.success(f"Saved '{new_name}'.")
        st.rerun()
    if c3.button("♻ Replace active dataset"):
        state.update(name, res, "Applied transformation")
        st.session_state.pop("_tf_result")
        st.rerun()
    st.download_button("⬇ Download CSV", res.to_csv(index=False),
                       "transformed.csv", "text/csv")
