"""Data transformation: group-by, pivot, merge, split, binning, scaling, encoding."""
from __future__ import annotations
import numpy as np
import pandas as pd


def group_by(df, keys, aggs: dict):
    out = df.groupby(list(keys), dropna=False).agg(aggs)
    out.columns = ["_".join(map(str, c)).strip("_") if isinstance(c, tuple) else str(c)
                   for c in out.columns]
    return out.reset_index()


def pivot(df, index, columns, values, aggfunc="sum", fill_value=0):
    out = pd.pivot_table(df, index=index, columns=columns, values=values,
                         aggfunc=aggfunc, fill_value=fill_value)
    if isinstance(out.columns, pd.MultiIndex):
        out.columns = ["_".join(map(str, c)) for c in out.columns]
    return out.reset_index()


def merge(left, right, how="inner", left_on=None, right_on=None,
          suffixes=("_x", "_y"), coerce_keys=True):
    """Join two dataframes, reconciling mismatched key dtypes.

    pandas refuses to merge a text key against a numeric one. Rather than crash, we
    try to make the keys compatible: numeric-looking text is parsed to numbers, and
    anything still mismatched falls back to a string comparison on both sides.
    Returns (dataframe, message) so the caller can tell the user what happened.
    """
    l, r = left.copy(), right.copy()
    note = ""

    if coerce_keys and left_on and right_on:
        lk, rk = l[left_on], r[right_on]
        if lk.dtype != rk.dtype:
            l_num, r_num = pd.to_numeric(lk, errors="coerce"), pd.to_numeric(rk, errors="coerce")
            both_numeric = l_num.notna().mean() > 0.95 and r_num.notna().mean() > 0.95
            if both_numeric:
                l[left_on], r[right_on] = l_num, r_num
                note = (f"Keys had different types ({lk.dtype} vs {rk.dtype}); "
                        f"both were read as numbers before joining.")
            else:
                l[left_on] = lk.astype(str).str.strip()
                r[right_on] = rk.astype(str).str.strip()
                note = (f"Keys had different types ({lk.dtype} vs {rk.dtype}); "
                        f"both were compared as text. Check the result for unmatched rows.")

    out = l.merge(r, how=how, left_on=left_on, right_on=right_on, suffixes=suffixes)

    matched = out[left_on].notna().sum() if left_on in out.columns else len(out)
    if not len(out):
        note = ((note + " ") if note else "") + (
            "No rows matched — the two key columns share no common values.")
    return out, note or f"Joined {len(out):,} rows ({matched:,} matched on the key)."


def split_column(df, column, sep=" ", maxsplit=1, names=None):
    out = df.copy()
    parts = out[column].astype(str).str.split(sep, n=maxsplit, expand=True)
    names = names or [f"{column}_{i+1}" for i in range(parts.shape[1])]
    for i, nm in enumerate(names[: parts.shape[1]]):
        out[nm] = parts[i]
    return out


def date_features(df, column):
    out = df.copy()
    d = pd.to_datetime(out[column], errors="coerce", format="mixed")
    out[f"{column}_year"] = d.dt.year
    out[f"{column}_quarter"] = d.dt.quarter
    out[f"{column}_month"] = d.dt.month
    out[f"{column}_month_name"] = d.dt.month_name()
    out[f"{column}_week"] = d.dt.isocalendar().week.astype("Int64")
    out[f"{column}_day"] = d.dt.day
    out[f"{column}_dayofweek"] = d.dt.day_name()
    out[f"{column}_is_weekend"] = d.dt.dayofweek >= 5
    return out


def formula_feature(df, name, expression):
    """Create a new column from a pandas eval expression, e.g. `revenue - cost`."""
    out = df.copy()
    out[name] = out.eval(expression)
    return out


def ratio_feature(df, name, numerator, denominator, as_pct=False):
    out = df.copy()
    val = pd.to_numeric(out[numerator], errors="coerce") / pd.to_numeric(
        out[denominator], errors="coerce").replace(0, np.nan)
    out[name] = val * 100 if as_pct else val
    return out


def binning(df, column, bins=5, labels=None, method="equal_width"):
    out = df.copy()
    s = pd.to_numeric(out[column], errors="coerce")
    if method == "quantile":
        out[f"{column}_bin"] = pd.qcut(s, q=bins, labels=labels, duplicates="drop")
    else:
        out[f"{column}_bin"] = pd.cut(s, bins=bins, labels=labels)
    out[f"{column}_bin"] = out[f"{column}_bin"].astype(str)
    return out


def scale(df, columns, method="standard"):
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
    scaler = {"standard": StandardScaler, "minmax": MinMaxScaler, "robust": RobustScaler}[method]()
    out = df.copy()
    vals = out[columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    scaled = scaler.fit_transform(vals)
    for i, c in enumerate(columns):
        out[f"{c}_{method}"] = scaled[:, i]
    return out


def encode(df, columns, method="onehot", max_categories=30):
    out = df.copy()
    if method == "onehot":
        keep = [c for c in columns if out[c].nunique() <= max_categories]
        if keep:
            out = pd.get_dummies(out, columns=keep, prefix=keep, dtype=int)
        return out
    if method == "label":
        for c in columns:
            out[f"{c}_code"] = out[c].astype("category").cat.codes
        return out
    if method == "frequency":
        for c in columns:
            freq = out[c].value_counts(normalize=True)
            out[f"{c}_freq"] = out[c].map(freq)
        return out
    return out


def sort_filter(df, sort_by=None, ascending=True, query=None, limit=None):
    out = df.copy()
    if query:
        out = out.query(query)
    if sort_by:
        out = out.sort_values(sort_by, ascending=ascending)
    if limit:
        out = out.head(int(limit))
    return out.reset_index(drop=True)
