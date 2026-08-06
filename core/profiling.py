"""Dataset profiling: shape, dtypes, nulls, duplicates, stats, correlations."""
from __future__ import annotations
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from .utils import is_text


def overview(df: pd.DataFrame) -> dict:
    cells = max(df.shape[0] * df.shape[1], 1)
    return {
        "rows": len(df),
        "columns": df.shape[1],
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_cells": int(df.isna().sum().sum()),
        "missing_pct": float(df.isna().sum().sum() / cells * 100),
        "memory_mb": float(df.memory_usage(deep=True).sum() / 1024**2),
        "numeric_cols": int(sum(is_numeric_dtype(df[c]) for c in df.columns)),
        "text_cols": int(sum(is_text(df[c]) for c in df.columns)),
    }


def column_profile(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    n = max(len(df), 1)
    for c in df.columns:
        s = df[c]
        nulls = int(s.isna().sum())
        rec = {
            "Column": str(c),
            "Type": str(s.dtype),
            "Non-Null": int(s.notna().sum()),
            "Nulls": nulls,
            "Null %": round(nulls / n * 100, 2),
            "Unique": int(s.nunique(dropna=True)),
            "Unique %": round(s.nunique(dropna=True) / n * 100, 2),
            "Memory (KB)": round(s.memory_usage(deep=True) / 1024, 1),
        }
        if is_numeric_dtype(s):
            d = pd.to_numeric(s, errors="coerce")
            rec.update({
                "Min": round(float(d.min()), 2) if d.notna().any() else None,
                "Mean": round(float(d.mean()), 2) if d.notna().any() else None,
                "Max": round(float(d.max()), 2) if d.notna().any() else None,
                "Std": round(float(d.std()), 2) if d.notna().any() else None,
            })
            rec["Sample"] = ""
        else:
            top = s.dropna().astype(str).value_counts().head(3)
            rec["Sample"] = ", ".join(top.index.tolist())
        rows.append(rec)
    return pd.DataFrame(rows)


def numeric_stats(df: pd.DataFrame) -> pd.DataFrame:
    num = df.select_dtypes(include=np.number)
    if num.empty:
        return pd.DataFrame()
    desc = num.describe().T
    desc["skew"] = num.skew(numeric_only=True)
    desc["kurtosis"] = num.kurtosis(numeric_only=True)
    desc["zeros"] = (num == 0).sum()
    return desc.round(3)


def correlations(df: pd.DataFrame, threshold: float = 0.5) -> tuple[pd.DataFrame, pd.DataFrame]:
    num = df.select_dtypes(include=np.number)
    if num.shape[1] < 2:
        return pd.DataFrame(), pd.DataFrame()
    corr = num.corr(numeric_only=True).round(3)
    pairs = (
        corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        .stack().reset_index()
    )
    pairs.columns = ["Feature A", "Feature B", "Correlation"]
    pairs["abs"] = pairs["Correlation"].abs()
    strong = (pairs[pairs["abs"] >= threshold]
              .sort_values("abs", ascending=False)
              .drop(columns="abs").reset_index(drop=True))
    return corr, strong


def missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    m = df.isna().sum()
    out = pd.DataFrame({"Column": m.index.astype(str), "Missing": m.values})
    out["Missing %"] = (out["Missing"] / max(len(df), 1) * 100).round(2)
    return out[out["Missing"] > 0].sort_values("Missing", ascending=False).reset_index(drop=True)


def quality_score(df: pd.DataFrame) -> int:
    """0-100 heuristic data-quality score."""
    o = overview(df)
    score = 100.0
    score -= min(o["missing_pct"] * 1.5, 40)
    score -= min(o["duplicate_rows"] / max(len(df), 1) * 100 * 1.2, 25)
    const = sum(df[c].nunique(dropna=False) <= 1 for c in df.columns)
    score -= min(const / max(df.shape[1], 1) * 100 * 0.3, 15)
    return int(max(0, round(score)))
