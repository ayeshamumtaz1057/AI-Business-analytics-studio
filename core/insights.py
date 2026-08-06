"""AI business insights: builds a compact data brief, then asks Gemini (or falls back
to a deterministic rule engine so the app is fully functional offline)."""
from __future__ import annotations
import json

import numpy as np
import pandas as pd

from . import ai
from .kpis import compute, timeseries, breakdown, money, format_kpi
from .products import performance, category_performance


def build_brief(df: pd.DataFrame, mapping: dict) -> dict:
    """Compact, token-cheap summary of the dataset for the LLM."""
    k = compute(df, mapping)
    brief = {
        "rows": len(df),
        "columns": list(map(str, df.columns))[:40],
        "kpis": {name: {"value": round(float(v["value"]), 2)
                        if v["value"] is not None and not (isinstance(v["value"], float) and np.isnan(v["value"]))
                        else None,
                        "change_pct": round(v["delta"], 2) if v["delta"] is not None else None}
                 for name, v in k.items()},
    }
    d = mapping.get("date")
    if d:
        dates = pd.to_datetime(df[d], errors="coerce", format="mixed").dropna()
        if not dates.empty:
            brief["period"] = f"{dates.min().date()} to {dates.max().date()}"
        ts = timeseries(df, mapping, freq="ME")
        if not ts.empty:
            brief["monthly_revenue"] = {str(r.date.date())[:7]: round(float(r.value), 2)
                                        for r in ts.itertuples()}
    for role in ("category", "region", "product"):
        b = breakdown(df, mapping, role, "revenue", top=8)
        if not b.empty:
            brief[f"top_{role}"] = {str(r.label): round(float(r.value), 2) for r in b.itertuples()}
    cat = category_performance(df, mapping)
    if not cat.empty and "Margin %" in cat:
        brief["category_margins"] = dict(zip(cat["Category"].astype(str),
                                             cat["Margin %"].round(2)))
    perf = performance(df, mapping)
    if not perf.empty and "Revenue" in perf:
        worst = perf.nsmallest(5, "Revenue")
        brief["weakest_products"] = dict(zip(worst["Product"].astype(str),
                                             worst["Revenue"].round(2)))
    return brief


SECTIONS = [
    "Executive Summary", "Key Trends", "Best Performing Products",
    "Underperforming Products", "Sales Opportunities", "Business Risks",
    "Customer Insights", "Actionable Recommendations",
]

PROMPT = """Here is an aggregated brief of a company's sales dataset (JSON):

{brief}

Write a business intelligence report with EXACTLY these markdown sections:
{sections}

Rules:
- Use `## Section Name` headings, exactly as listed.
- Under each heading write 2-4 concise bullet points.
- Quote the real numbers from the brief (currency, %, counts).
- "Actionable Recommendations" must be imperative and prioritised (P1, P2, P3...).
- No preamble, no closing remarks, no invented data."""


def generate_report(df: pd.DataFrame, mapping: dict) -> tuple[str, str]:
    """Return (markdown_report, engine_used)."""
    brief = build_brief(df, mapping)
    text = ai.generate(
        PROMPT.format(brief=json.dumps(brief, default=str)[:12000],
                      sections="\n".join(f"## {s}" for s in SECTIONS)),
        system=ai.ANALYST_SYSTEM,
    )
    if text:
        return text, "Gemini"
    return rule_based_report(df, mapping, brief), "Built-in analyst (offline)"


# ---- Deterministic fallback ------------------------------------------------
def rule_based_report(df, mapping, brief=None) -> str:
    brief = brief or build_brief(df, mapping)
    k = brief["kpis"]
    L = []

    def val(name):
        return k.get(name, {}).get("value")

    def chg(name):
        return k.get(name, {}).get("change_pct")

    rev, prof = val("Total Revenue"), val("Total Profit")
    margin, aov = val("Profit Margin"), val("Avg. Order Value")

    L.append("## Executive Summary")
    L.append(f"- The dataset covers **{brief.get('period', 'the full uploaded period')}** "
             f"with **{brief['rows']:,} transactions**.")
    L.append(f"- Total revenue reached **{money(rev)}**"
             + (f" with **{money(prof)}** profit ({margin:.1f}% margin)." if prof and margin else "."))
    if chg("Total Revenue") is not None:
        d = chg("Total Revenue")
        L.append(f"- Revenue is **{'up' if d>=0 else 'down'} {abs(d):.1f}%** versus the "
                 f"previous comparable period.")
    if aov:
        L.append(f"- Average order value sits at **{money(aov)}** across "
                 f"{format_kpi('Total Orders', val('Total Orders'))} orders.")

    L.append("\n## Key Trends")
    mr = brief.get("monthly_revenue", {})
    if len(mr) >= 2:
        items = list(mr.items())
        best_m = max(items, key=lambda x: x[1])
        worst_m = min(items, key=lambda x: x[1])
        first, last = items[0][1], items[-1][1]
        trend = (last - first) / first * 100 if first else 0
        L.append(f"- Monthly revenue moved **{trend:+.1f}%** from {items[0][0]} to {items[-1][0]}.")
        L.append(f"- Peak month was **{best_m[0]}** ({money(best_m[1])}); "
                 f"weakest was **{worst_m[0]}** ({money(worst_m[1])}).")
    if chg("Profit Margin") is not None:
        L.append(f"- Profit margin changed by **{chg('Profit Margin'):+.1f}%**, which "
                 f"{'protects' if chg('Profit Margin')>=0 else 'erodes'} bottom-line growth.")

    tp = brief.get("top_product", {})
    L.append("\n## Best Performing Products")
    for name, v in list(tp.items())[:4]:
        share = v / rev * 100 if rev else 0
        L.append(f"- **{name}** generated {money(v)} ({share:.1f}% of total revenue).")
    if not tp:
        L.append("- No product column is mapped, so product ranking is unavailable.")

    L.append("\n## Underperforming Products")
    wp = brief.get("weakest_products", {})
    for name, v in list(wp.items())[:4]:
        L.append(f"- **{name}** contributed only {money(v)} — review pricing, placement or delisting.")
    if not wp:
        L.append("- Map a product column to surface long-tail underperformers.")

    L.append("\n## Sales Opportunities")
    cm = brief.get("category_margins", {})
    if cm:
        best_cat = max(cm.items(), key=lambda x: x[1])
        L.append(f"- **{best_cat[0]}** carries the strongest margin ({best_cat[1]:.1f}%) — "
                 f"shift marketing spend here for the highest return per dollar.")
    tr = brief.get("top_region", {})
    if len(tr) >= 2:
        items = list(tr.items())
        L.append(f"- **{items[0][0]}** leads regionally ({money(items[0][1])}); "
                 f"replicate its playbook in **{items[-1][0]}**, currently at {money(items[-1][1])}.")
    if aov:
        L.append(f"- A 10% lift in average order value would add roughly "
                 f"**{money((rev or 0) * 0.10)}** in revenue with no new customers.")

    L.append("\n## Business Risks")
    if tp and rev:
        top_share = sum(list(tp.values())[:3]) / rev * 100
        if top_share > 45:
            L.append(f"- Revenue concentration risk: the top 3 products drive "
                     f"**{top_share:.1f}%** of revenue.")
    if margin is not None and margin < 15:
        L.append(f"- Margin of **{margin:.1f}%** is thin; cost inflation would quickly turn "
                 f"profitable orders negative.")
    if chg("Total Customers") is not None and chg("Total Customers") < 0:
        L.append(f"- Active customers fell **{abs(chg('Total Customers')):.1f}%** — acquisition "
                 f"is not replacing churn.")
    if len(L) and not any("Risk" in x for x in L[-3:]):
        L.append("- Monitor demand volatility: several periods deviate materially from trend.")

    L.append("\n## Customer Insights")
    cust = val("Total Customers")
    if cust:
        L.append(f"- **{cust:,.0f} unique customers** generated an average of "
                 f"**{money((rev or 0)/cust)}** each.")
        L.append(f"- Roughly {val('Total Orders')/cust:.1f} orders per customer — "
                 f"raising repeat purchases is the cheapest growth lever available.")
    else:
        L.append("- Map a customer ID column to unlock RFM, CLV and churn analytics.")

    L.append("\n## Actionable Recommendations")
    L.append(f"- **P1 — Double down on winners.** Increase inventory and ad spend on "
             f"{', '.join(list(tp)[:2]) if tp else 'your top SKUs'} before the next peak period.")
    L.append("- **P2 — Fix the margin leak.** Renegotiate cost or reprice every SKU below a "
             "10% margin within the next quarter.")
    L.append("- **P3 — Reactivate dormant customers.** Launch a win-back campaign for buyers "
             "inactive for 90+ days; see Customer Analytics for the target list.")
    L.append("- **P4 — Operationalise this report.** Schedule a weekly refresh so anomalies are "
             "caught within days, not months.")
    return "\n".join(L)


def quick_cards(df, mapping) -> list[tuple[str, str, str]]:
    """Short insight cards for the dashboard: (title, body, kind)."""
    k = compute(df, mapping)
    out = []
    rd = k["Total Revenue"]["delta"]
    if rd is not None:
        out.append((f"Revenue is {'up' if rd>=0 else 'down'} {abs(rd):.1f}% 📈",
                    f"Revenue {'increased' if rd>=0 else 'decreased'} by {abs(rd):.1f}% compared to "
                    f"the previous period.", "good" if rd >= 0 else "bad"))
    cat = breakdown(df, mapping, "category", "revenue", top=3)
    if not cat.empty:
        out.append(("Best performing category",
                    f"{cat.iloc[0]['label']} is the top category with "
                    f"{money(cat.iloc[0]['value'])} in revenue.", "info"))
    md = k["Profit Margin"]["delta"]
    if md is not None:
        out.append((f"Profit margin {'improved' if md>=0 else 'declined'}",
                    f"Profit margin moved {md:+.1f}% versus the previous period.",
                    "good" if md >= 0 else "warn"))
    perf = performance(df, mapping)
    if not perf.empty and "Revenue" in perf and len(perf) > 3:
        worst = perf.nsmallest(1, "Revenue").iloc[0]
        out.append(("Watch out",
                    f"{worst['Product']} is the weakest performer at {money(worst['Revenue'])}.",
                    "warn"))
    return out[:4]
