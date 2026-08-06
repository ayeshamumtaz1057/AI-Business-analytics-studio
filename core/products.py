"""Product analytics: best sellers, slow movers, profitability, inventory hints."""
from __future__ import annotations
import numpy as np
import pandas as pd


def performance(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    prod, rev = mapping.get("product"), mapping.get("revenue")
    if not prod:
        return pd.DataFrame()
    prof, qty, order = mapping.get("profit"), mapping.get("quantity"), mapping.get("order_id")
    cost, date = mapping.get("cost"), mapping.get("date")

    d = df.copy()
    for c in [rev, prof, qty, cost]:
        if c:
            d[c] = pd.to_numeric(d[c], errors="coerce")

    agg = {}
    if rev:
        agg["Revenue"] = (rev, "sum")
    if prof:
        agg["Profit"] = (prof, "sum")
    elif rev and cost:
        d["_profit"] = d[rev] - d[cost]
        agg["Profit"] = ("_profit", "sum")
    if qty:
        agg["Units"] = (qty, "sum")
    agg["Orders"] = (order, "nunique") if order else (prod, "count")

    g = d.groupby(prod, dropna=False).agg(**agg).reset_index().rename(columns={prod: "Product"})
    if "Revenue" in g and "Profit" in g:
        g["Margin %"] = (g["Profit"] / g["Revenue"].replace(0, np.nan) * 100).round(2)
    if "Revenue" in g:
        g["Revenue Share %"] = (g["Revenue"] / max(g["Revenue"].sum(), 1e-9) * 100).round(2)
        g = g.sort_values("Revenue", ascending=False)
        g["Cumulative %"] = g["Revenue Share %"].cumsum().round(2)
        g["ABC Class"] = np.where(g["Cumulative %"] <= 80, "A",
                          np.where(g["Cumulative %"] <= 95, "B", "C"))

    if date:
        dd = d[[prod, date]].copy()
        dd[date] = pd.to_datetime(dd[date], errors="coerce", format="mixed")
        last = dd.groupby(prod)[date].max()
        recency = (dd[date].max() - last).dt.days
        g = g.merge(recency.rename("Days Since Last Sale").reset_index()
                    .rename(columns={prod: "Product"}), on="Product", how="left")
    return g.reset_index(drop=True)


def movers(perf: pd.DataFrame, top=10):
    if perf.empty or "Revenue" not in perf:
        return pd.DataFrame(), pd.DataFrame()
    best = perf.nlargest(top, "Revenue")
    slow = perf.nsmallest(top, "Revenue")
    return best, slow


def inventory_suggestions(perf: pd.DataFrame, limit=12) -> pd.DataFrame:
    if perf.empty:
        return pd.DataFrame()
    rows = []
    for _, r in perf.iterrows():
        cls = r.get("ABC Class", "C")
        margin = r.get("Margin %", np.nan)
        stale = r.get("Days Since Last Sale", np.nan)
        if cls == "A" and (pd.isna(margin) or margin > 0):
            action, why = "Increase stock", "Class A revenue driver — protect against stock-outs."
        elif not pd.isna(margin) and margin < 5:
            action, why = "Review pricing", f"Thin margin of {margin:.1f}% — renegotiate cost or raise price."
        elif not pd.isna(stale) and stale > 60:
            action, why = "Discount / clear", f"No sales in {int(stale)} days — capital is tied up."
        elif cls == "C":
            action, why = "Reduce stock", "Long-tail item with minimal revenue contribution."
        else:
            action, why = "Maintain", "Performing in line with expectations."
        rows.append({"Product": r["Product"], "Class": cls,
                     "Revenue": r.get("Revenue", np.nan),
                     "Margin %": margin, "Action": action, "Rationale": why})
    out = pd.DataFrame(rows)
    order = {"Increase stock": 0, "Review pricing": 1, "Discount / clear": 2,
             "Reduce stock": 3, "Maintain": 4}
    return out.sort_values("Action", key=lambda s: s.map(order)).head(limit).reset_index(drop=True)


def category_performance(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    cat, rev = mapping.get("category"), mapping.get("revenue")
    if not (cat and rev):
        return pd.DataFrame()
    prof = mapping.get("profit")
    d = df.copy()
    d[rev] = pd.to_numeric(d[rev], errors="coerce")
    agg = {"Revenue": (rev, "sum")}
    if prof:
        d[prof] = pd.to_numeric(d[prof], errors="coerce")
        agg["Profit"] = (prof, "sum")
    g = d.groupby(cat, dropna=False).agg(**agg).reset_index().rename(columns={cat: "Category"})
    if "Profit" in g:
        g["Margin %"] = (g["Profit"] / g["Revenue"].replace(0, np.nan) * 100).round(2)
    g["Share %"] = (g["Revenue"] / max(g["Revenue"].sum(), 1e-9) * 100).round(2)
    return g.sort_values("Revenue", ascending=False).reset_index(drop=True)
