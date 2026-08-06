"""One-click data cleaning operations. Every function returns (df, message)."""
from __future__ import annotations
import re

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from .utils import is_text, text_columns


def remove_duplicates(df, subset=None, keep="first"):
    before = len(df)
    out = df.drop_duplicates(subset=subset or None, keep=keep)
    return out.reset_index(drop=True), f"Removed {before - len(out):,} duplicate rows."


def handle_missing(df, strategy="drop_rows", columns=None, fill_value=None):
    cols = columns or list(df.columns)
    out = df.copy()
    if strategy == "drop_rows":
        before = len(out)
        out = out.dropna(subset=cols).reset_index(drop=True)
        return out, f"Dropped {before - len(out):,} rows containing nulls."
    if strategy == "drop_columns":
        drop = [c for c in cols if out[c].isna().any()]
        return out.drop(columns=drop), f"Dropped {len(drop)} column(s) with nulls."
    filled = 0
    for c in cols:
        n = int(out[c].isna().sum())
        if not n:
            continue
        if strategy == "mean" and is_numeric_dtype(out[c]):
            out[c] = out[c].fillna(out[c].mean())
        elif strategy == "median" and is_numeric_dtype(out[c]):
            out[c] = out[c].fillna(out[c].median())
        elif strategy == "mode":
            m = out[c].mode()
            if not m.empty:
                out[c] = out[c].fillna(m.iloc[0])
        elif strategy == "zero" and is_numeric_dtype(out[c]):
            out[c] = out[c].fillna(0)
        elif strategy == "ffill":
            out[c] = out[c].ffill()
        elif strategy == "bfill":
            out[c] = out[c].bfill()
        elif strategy == "constant":
            out[c] = out[c].fillna(fill_value)
        else:
            continue
        filled += n
    return out, f"Imputed {filled:,} missing values using '{strategy}'."


def standardize_dates(df, columns, output="datetime", fmt="%Y-%m-%d"):
    out = df.copy()
    done = []
    for c in columns:
        parsed = pd.to_datetime(out[c], errors="coerce", format="mixed")
        out[c] = parsed.dt.strftime(fmt) if output == "string" else parsed
        done.append(str(c))
    return out, f"Standardized date column(s): {', '.join(done)}."


def fix_text_case(df, columns, mode="title"):
    out = df.copy()
    fn = {"lower": str.lower, "upper": str.upper, "title": str.title, "capitalize": str.capitalize}[mode]
    for c in columns:
        out[c] = out[c].astype(str).map(lambda v: fn(v) if v not in ("nan", "None") else np.nan)
    return out, f"Applied '{mode}' case to {len(columns)} column(s)."


def trim_whitespace(df, columns=None):
    out = df.copy()
    cols = columns or text_columns(out)
    for c in cols:
        out[c] = out[c].astype(str).str.strip().replace({"nan": np.nan, "None": np.nan})
        out[c] = out[c].astype(str).str.replace(r"\s+", " ", regex=True).replace({"nan": np.nan})
    return out, f"Trimmed whitespace in {len(cols)} column(s)."


def remove_outliers(df, columns, method="iqr", factor=1.5, action="remove"):
    out = df.copy()
    mask = pd.Series(False, index=out.index)
    for c in columns:
        s = pd.to_numeric(out[c], errors="coerce")
        if method == "iqr":
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            lo, hi = q1 - factor * iqr, q3 + factor * iqr
        else:  # z-score
            lo, hi = s.mean() - factor * s.std(), s.mean() + factor * s.std()
        bad = (s < lo) | (s > hi)
        if action == "clip":
            out[c] = s.clip(lo, hi)
        else:
            mask |= bad.fillna(False)
    if action == "clip":
        return out, f"Clipped outliers in {len(columns)} column(s) ({method})."
    n = int(mask.sum())
    return out[~mask].reset_index(drop=True), f"Removed {n:,} outlier rows ({method}, factor {factor})."


def rename_columns(df, mapping):
    mapping = {k: v for k, v in mapping.items() if v and v != k}
    return df.rename(columns=mapping), f"Renamed {len(mapping)} column(s)."


def clean_column_names(df):
    def norm(c):
        c = re.sub(r"[^0-9a-zA-Z]+", "_", str(c)).strip("_").lower()
        return c or "col"
    return df.rename(columns={c: norm(c) for c in df.columns}), "Normalized all column names to snake_case."


def convert_types(df, column, target):
    out = df.copy()
    if target == "numeric":
        out[column] = pd.to_numeric(out[column], errors="coerce")
    elif target == "integer":
        out[column] = pd.to_numeric(out[column], errors="coerce").astype("Int64")
    elif target == "datetime":
        out[column] = pd.to_datetime(out[column], errors="coerce", format="mixed")
    elif target == "string":
        out[column] = out[column].astype(str)
    elif target == "category":
        out[column] = out[column].astype("category")
    elif target == "boolean":
        out[column] = out[column].astype(str).str.lower().isin(["1", "true", "yes", "y", "t"])
    return out, f"Converted '{column}' to {target}."


def drop_columns(df, columns):
    return df.drop(columns=list(columns)), f"Dropped {len(columns)} column(s)."
