"""Session-state helpers: dataset registry, active dataset, column mapping."""
from __future__ import annotations
import pandas as pd
import streamlit as st

from .config import ROLES
from .mapping import auto_map


def init():
    ss = st.session_state
    ss.setdefault("datasets", {})       # name -> DataFrame
    ss.setdefault("active", None)       # active dataset name
    ss.setdefault("mapping", {})        # name -> {role: column}
    ss.setdefault("clean_log", {})      # name -> list[str]
    ss.setdefault("messages", [])       # chat history
    ss.setdefault("ai_cache", {})       # insight cache
    ss.setdefault("theme", "Dark")


def register(name: str, df: pd.DataFrame, make_active: bool = True):
    init()
    base, i = name, 2
    while name in st.session_state["datasets"] and not st.session_state.get("_overwrite"):
        name = f"{base} ({i})"
        i += 1
    st.session_state["datasets"][name] = df
    st.session_state["mapping"][name] = auto_map(df)
    st.session_state["clean_log"].setdefault(name, [])
    if make_active:
        st.session_state["active"] = name
    return name


def update(name: str, df: pd.DataFrame, note: str = ""):
    st.session_state["datasets"][name] = df
    if note:
        st.session_state["clean_log"].setdefault(name, []).append(note)


def names() -> list[str]:
    init()
    return list(st.session_state["datasets"].keys())


def active_name() -> str | None:
    init()
    return st.session_state.get("active")


def active_df() -> pd.DataFrame | None:
    n = active_name()
    return st.session_state["datasets"].get(n) if n else None


def mapping() -> dict:
    n = active_name()
    m = st.session_state.get("mapping", {}).get(n, {}) if n else {}
    return {k: v for k, v in m.items() if v}


def set_mapping(role_map: dict):
    n = active_name()
    if n:
        st.session_state["mapping"][n] = {r: role_map.get(r) for r in ROLES}


def col(role: str):
    """Return the dataframe column bound to a semantic role (or None)."""
    return mapping().get(role)


def require_data() -> bool:
    """Render a friendly stop-block when nothing is loaded. Returns True if data exists."""
    if active_df() is not None:
        return True
    st.info("No dataset loaded yet. Head to **Upload Center** to add a file or load the demo dataset.")
    if st.button("⚡ Load demo dataset", type="primary"):
        from .loaders import load_sample
        name, df = load_sample()
        register(name, df)
        st.rerun()
    return False


def dataset_picker(label="Active dataset", label_visibility="visible"):
    ds = names()
    if not ds:
        return None
    cur = active_name()
    idx = ds.index(cur) if cur in ds else 0
    choice = st.selectbox(label or "Active dataset", ds, index=idx, key="_ds_picker",
                          label_visibility=label_visibility)
    if choice != cur:
        st.session_state["active"] = choice
        st.rerun()
    return choice
