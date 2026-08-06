"""Customer analytics: RFM, CLV, churn risk, repeat behaviour, segmentation."""
from __future__ import annotations
import numpy as np
import pandas as pd


SEGMENTS = {
    (4, 4): "Champions", (4, 3): "Loyal Customers", (3, 4): "Loyal Customers",
    (3, 3): "Potential Loyalist", (4, 2): "Recent Buyers", (4, 1): "New Customers",
    (3, 1): "Promising", (2, 4): "At Risk", (1, 4): "Can't Lose Them",
    (2, 3): "Needs Attention", (1, 3): "At Risk", (2, 2): "About to Sleep",
    (2, 1): "Hibernating", (1, 2): "Hibernating", (1, 1): "Lost",
    (3, 2): "Needs Attention",
}


def rfm(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    cust, date, rev = mapping.get("customer_id"), mapping.get("date"), mapping.get("revenue")
    order = mapping.get("order_id")
    if not (cust and date and rev):
        return pd.DataFrame()

    d = df[[c for c in {cust, date, rev, order} if c]].copy()
    d[date] = pd.to_datetime(d[date], errors="coerce", format="mixed")
    d[rev] = pd.to_numeric(d[rev], errors="coerce")
    d = d.dropna(subset=[cust, date, rev])
    if d.empty:
        return pd.DataFrame()

    snapshot = d[date].max() + pd.Timedelta(days=1)
    agg = {date: lambda s: (snapshot - s.max()).days, rev: "sum"}
    g = d.groupby(cust).agg(
        Recency=(date, lambda s: (snapshot - s.max()).days),
        Frequency=(order, "nunique") if order else (date, "count"),
        Monetary=(rev, "sum"),
        FirstPurchase=(date, "min"),
        LastPurchase=(date, "max"),
    ).reset_index().rename(columns={cust: "Customer"})

    def score(series, reverse=False):
        try:
            q = pd.qcut(series.rank(method="first"), 4, labels=[1, 2, 3, 4])
        except Exception:
            q = pd.Series(2, index=series.index)
        q = q.astype(int)
        return 5 - q if reverse else q

    g["R"] = score(g["Recency"], reverse=True)
    g["F"] = score(g["Frequency"])
    g["M"] = score(g["Monetary"])
    g["RFM Score"] = g["R"].astype(str) + g["F"].astype(str) + g["M"].astype(str)
    g["Segment"] = [SEGMENTS.get((r, max(f, m)), "Others") for r, f, m in zip(g.R, g.F, g.M)]

    tenure = (g["LastPurchase"] - g["FirstPurchase"]).dt.days.clip(lower=1)
    g["Avg Order Value"] = g["Monetary"] / g["Frequency"].clip(lower=1)
    g["Purchase Rate/mo"] = g["Frequency"] / (tenure / 30.0)
    g["CLV (12mo est.)"] = g["Avg Order Value"] * g["Purchase Rate/mo"].clip(upper=30) * 12
    g["Churn Risk %"] = (g["Recency"] / max(g["Recency"].max(), 1) * 100).round(1)
    g["Risk Band"] = pd.cut(g["Churn Risk %"], [-0.1, 33, 66, 100],
                            labels=["Low", "Medium", "High"]).astype(str)
    return g.sort_values("Monetary", ascending=False).reset_index(drop=True)


def cohort_retention(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    cust, date = mapping.get("customer_id"), mapping.get("date")
    if not (cust and date):
        return pd.DataFrame()
    d = df[[cust, date]].copy()
    d[date] = pd.to_datetime(d[date], errors="coerce", format="mixed")
    d = d.dropna()
    if d.empty:
        return pd.DataFrame()
    d["period"] = d[date].dt.to_period("M")
    first = d.groupby(cust)["period"].min().rename("cohort")
    d = d.join(first, on=cust)
    d["offset"] = (d["period"] - d["cohort"]).apply(lambda x: x.n)
    tab = d.groupby(["cohort", "offset"])[cust].nunique().unstack(fill_value=0)
    if tab.empty:
        return tab
    retention = tab.divide(tab.iloc[:, 0], axis=0) * 100
    retention.index = retention.index.astype(str)
    return retention.round(1)


def summary(rfm_df: pd.DataFrame) -> dict:
    if rfm_df.empty:
        return {}
    total = len(rfm_df)
    repeat = int((rfm_df["Frequency"] > 1).sum())
    return {
        "Customers": total,
        "Repeat customers": repeat,
        "Repeat rate %": repeat / total * 100,
        "Avg CLV": float(rfm_df["CLV (12mo est.)"].mean()),
        "High churn risk": int((rfm_df["Risk Band"] == "High").sum()),
        "Top 10% revenue share %": float(
            rfm_df.nlargest(max(total // 10, 1), "Monetary")["Monetary"].sum()
            / max(rfm_df["Monetary"].sum(), 1e-9) * 100),
    }
