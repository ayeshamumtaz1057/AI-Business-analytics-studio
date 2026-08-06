"""Business KPI computation with period-over-period comparison."""
from __future__ import annotations
import numpy as np
import pandas as pd

from .config import CURRENCY, TARGET_REVENUE
from .mapping import coerce_types


def money(v, cur=CURRENCY):
    try:
        v = float(v)
    except Exception:
        return "—"
    sign = "-" if v < 0 else ""
    v = abs(v)
    if v >= 1_000_000_000:
        return f"{sign}{cur}{v/1_000_000_000:.2f}B"
    if v >= 1_000_000:
        return f"{sign}{cur}{v/1_000_000:.2f}M"
    if v >= 10_000:
        return f"{sign}{cur}{v/1_000:.1f}K"
    return f"{sign}{cur}{v:,.2f}"


def number(v):
    try:
        return f"{float(v):,.0f}"
    except Exception:
        return "—"


def prepare(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    out = coerce_types(df, mapping)
    d = mapping.get("date")
    if d and d in out.columns:
        out = out.dropna(subset=[d]).sort_values(d)
    return out


def _pct_change(cur, prev):
    if prev in (0, None) or (isinstance(prev, float) and (np.isnan(prev) or prev == 0)):
        return None
    return (cur - prev) / abs(prev) * 100


def compute(df: pd.DataFrame, mapping: dict, compare: bool = True) -> dict:
    """Return {kpi_name: {'value':x, 'delta':y}} for the frame supplied."""
    m = mapping
    rev_c, prof_c = m.get("revenue"), m.get("profit")
    cost_c, qty_c = m.get("cost"), m.get("quantity")
    ord_c, cust_c, date_c = m.get("order_id"), m.get("customer_id"), m.get("date")

    def agg(frame):
        rev = float(pd.to_numeric(frame[rev_c], errors="coerce").sum()) if rev_c else 0.0
        if prof_c:
            prof = float(pd.to_numeric(frame[prof_c], errors="coerce").sum())
        elif cost_c and rev_c:
            prof = rev - float(pd.to_numeric(frame[cost_c], errors="coerce").sum())
        else:
            prof = np.nan
        orders = int(frame[ord_c].nunique()) if ord_c else len(frame)
        customers = int(frame[cust_c].nunique()) if cust_c else np.nan
        units = float(pd.to_numeric(frame[qty_c], errors="coerce").sum()) if qty_c else np.nan
        return {
            "Total Revenue": rev,
            "Total Profit": prof,
            "Total Orders": orders,
            "Total Customers": customers,
            "Units Sold": units,
            "Avg. Order Value": rev / orders if orders else np.nan,
            "Profit Margin": (prof / rev * 100) if rev and not np.isnan(prof) else np.nan,
            "Revenue / Customer": rev / customers if customers and not np.isnan(customers) else np.nan,
        }

    full = agg(df)

    # Period-over-period: split the mapped date range in half and compare.
    recent = previous = None
    if compare and date_c and date_c in df.columns and df[date_c].notna().any():
        dates = pd.to_datetime(df[date_c], errors="coerce", format="mixed")
        span = dates.max() - dates.min()
        if pd.notna(span) and span.days > 0:
            mid = dates.max() - span / 2
            first, second = df[dates <= mid], df[dates > mid]
            if len(first) > 3 and len(second) > 3:
                recent, previous = agg(second), agg(first)

    out = {}
    for k, v in full.items():
        delta = None
        if recent and previous and previous.get(k) is not None:
            delta = _pct_change(recent[k], previous[k])
            if delta is not None and (np.isnan(delta) or np.isinf(delta)):
                delta = None
        out[k] = {"value": v, "delta": delta}

    out["Target Achievement"] = {
        "value": full["Total Revenue"] / TARGET_REVENUE * 100 if TARGET_REVENUE else np.nan,
        "delta": None,
    }
    return out


def format_kpi(name: str, value) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "—"
    if name in ("Total Revenue", "Total Profit", "Avg. Order Value", "Revenue / Customer"):
        return money(value)
    if name in ("Profit Margin", "Target Achievement"):
        return f"{value:.1f}%"
    return number(value)


def timeseries(df, mapping, freq="D", value_role="revenue"):
    d, v = mapping.get("date"), mapping.get(value_role)
    if not d or not v:
        return pd.DataFrame()
    tmp = df[[d, v]].copy()
    tmp[d] = pd.to_datetime(tmp[d], errors="coerce", format="mixed")
    tmp[v] = pd.to_numeric(tmp[v], errors="coerce")
    tmp = tmp.dropna()
    if tmp.empty:
        return pd.DataFrame()
    out = tmp.set_index(d).resample(freq)[v].sum().reset_index()
    out.columns = ["date", "value"]
    return out


def breakdown(df, mapping, dim_role="category", value_role="revenue", top=10):
    dim, val = mapping.get(dim_role), mapping.get(value_role)
    if not dim:
        return pd.DataFrame()
    if val:
        out = df.groupby(dim, dropna=False)[val].sum().sort_values(ascending=False)
    else:
        out = df[dim].value_counts()
    out = out.head(top).reset_index()
    out.columns = ["label", "value"]
    return out
