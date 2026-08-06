"""Natural-language querying over the active dataframe.

Strategy: ask Gemini for a single safe pandas expression; if AI is unavailable
(or the expression is rejected) fall back to intent matching so chat still works.
"""
from __future__ import annotations
import re

import numpy as np
import pandas as pd

from . import ai
from .kpis import compute, money, format_kpi, timeseries, breakdown
from .products import performance

FORBIDDEN = re.compile(
    r"(import|__|open\s*\(|exec|eval|os\.|sys\.|subprocess|to_csv|to_pickle|read_|"
    r"delete|drop\s*\(\s*columns|globals|locals|getattr|setattr|compile)", re.I)

CODE_SYSTEM = (
    "You translate business questions into ONE line of pandas code. "
    "The dataframe is named `df`. Return ONLY the expression — no imports, no prints, "
    "no markdown fences, no assignment. It must evaluate to a DataFrame, Series or scalar."
)


def _safe(expr: str) -> bool:
    return bool(expr) and not FORBIDDEN.search(expr) and "\n" not in expr.strip()


def ai_answer(question: str, df: pd.DataFrame, mapping: dict) -> tuple[str, object | None]:
    """Return (markdown_answer, optional_result_frame)."""
    schema = "\n".join(f"- {c} ({df[c].dtype})" for c in df.columns)
    roles = ", ".join(f"{k}={v}" for k, v in mapping.items() if v)
    head = df.head(3).to_csv(index=False)

    expr = ai.generate(
        f"Columns:\n{schema}\n\nSemantic roles: {roles}\n\nFirst rows:\n{head}\n\n"
        f"Question: {question}\n\nPandas expression:",
        system=CODE_SYSTEM, temperature=0.1, max_tokens=300)

    result = None
    if expr:
        expr = expr.strip().strip("`").replace("python", "", 1).strip()
        expr = expr.splitlines()[0].strip() if expr else expr
        if _safe(expr):
            try:
                result = eval(expr, {"__builtins__": {}}, {"df": df, "pd": pd, "np": np})
            except Exception:
                result = None

    frame = None
    if isinstance(result, pd.DataFrame):
        frame = result.head(50)
    elif isinstance(result, pd.Series):
        frame = result.head(50).reset_index()

    facts = ""
    if frame is not None:
        facts = frame.head(20).to_csv(index=False)
    elif result is not None:
        facts = str(result)

    narrative = ai.generate(
        f"Question: {question}\n\nComputed result:\n{facts or 'no direct result'}\n\n"
        f"Overall KPIs: { {k: format_kpi(k, v['value']) for k, v in compute(df, mapping).items()} }\n\n"
        "Answer the question in 2-4 sentences using these numbers. Be specific and business-focused.",
        system=ai.ANALYST_SYSTEM, temperature=0.3, max_tokens=600)

    if narrative:
        return narrative, frame
    if frame is not None:
        return "Here is what the data shows:", frame
    return fallback_answer(question, df, mapping)


# ---- Offline intent engine -------------------------------------------------
def fallback_answer(q: str, df: pd.DataFrame, mapping: dict) -> tuple[str, object | None]:
    ql = q.lower()
    k = compute(df, mapping)

    def top_table(role, n=10, asc=False):
        b = breakdown(df, mapping, role, "revenue", top=200)
        if b.empty:
            return None
        b = b.sort_values("value", ascending=asc).head(n).reset_index(drop=True)
        b.columns = [role.replace("_", " ").title(), "Revenue"]
        return b

    if re.search(r"(top|best|highest).*(customer)", ql):
        t = top_table("customer_id")
        if t is not None:
            return f"Your highest-value customers by total revenue (top {len(t)}):", t
    if re.search(r"(top|best|highest|selling).*(product|item|sku)", ql):
        t = top_table("product")
        if t is not None:
            return (f"**{t.iloc[0,0]}** is your best seller at "
                    f"{money(t.iloc[0,1])}. Full ranking:"), t
    if re.search(r"(worst|slow|lowest|underperform)", ql):
        t = top_table("product", asc=True)
        if t is not None:
            return "These products generate the least revenue and are candidates for review:", t
    if re.search(r"(profitab|margin).*(categ)|categ.*(profitab|margin)", ql):
        from .products import category_performance
        c = category_performance(df, mapping)
        if not c.empty and "Margin %" in c:
            best = c.sort_values("Margin %", ascending=False).iloc[0]
            return (f"**{best['Category']}** is the most profitable category at a "
                    f"{best['Margin %']:.1f}% margin on {money(best['Revenue'])} revenue."), c
    if re.search(r"(region|country|market)", ql):
        t = top_table("region")
        if t is not None:
            return "Revenue by region:", t
    if re.search(r"(why|drop|decline|fell|down)", ql):
        ts = timeseries(df, mapping, "ME")
        if not ts.empty and len(ts) > 2:
            ts["chg"] = ts["value"].pct_change() * 100
            worst = ts.loc[ts["chg"].idxmin()]
            best_c = breakdown(df, mapping, "category", "revenue", top=1)
            hint = f" The largest category is {best_c.iloc[0]['label']}." if not best_c.empty else ""
            return (f"The sharpest decline was in {pd.to_datetime(worst['date']).strftime('%B %Y')}, "
                    f"down {abs(worst['chg']):.1f}% to {money(worst['value'])}. "
                    f"Check Anomaly Detection for the exact days driving it.{hint}"), ts.round(2)
    if re.search(r"(summar|overview|performance|how.*doing|q[1-4])", ql):
        lines = [f"- **{name}**: {format_kpi(name, v['value'])}"
                 + (f" ({v['delta']:+.1f}%)" if v["delta"] is not None else "")
                 for name, v in k.items() if v["value"] is not None]
        return "Here is the headline performance summary:\n" + "\n".join(lines), None
    if re.search(r"(forecast|predict|next month|future)", ql):
        return ("Open the **Forecasting** page to project revenue 30 / 90 / 365 days ahead "
                "with confidence bands — I can run several models there."), None
    if re.search(r"(trend|over time|monthly|growth)", ql):
        ts = timeseries(df, mapping, "ME")
        if not ts.empty:
            first, last = ts["value"].iloc[0], ts["value"].iloc[-1]
            g = (last - first) / first * 100 if first else 0
            return (f"Revenue moved {g:+.1f}% from the first to the last month in range "
                    f"({money(first)} → {money(last)})."), ts.round(2)

    lines = [f"- **{n}**: {format_kpi(n, v['value'])}" for n, v in k.items()
             if v["value"] is not None][:5]
    return ("I could not match that to a specific analysis. Here is the current snapshot — "
            "try asking about top products, customers, regions, margins or trends.\n"
            + "\n".join(lines)), None


def answer(question: str, df: pd.DataFrame, mapping: dict):
    if ai.available():
        return ai_answer(question, df, mapping)
    return fallback_answer(question, df, mapping)


SUGGESTIONS = [
    "Summarize overall business performance",
    "Which category is most profitable?",
    "Show me the top 10 customers",
    "Why did sales drop?",
    "What are my slowest moving products?",
    "How does revenue trend over time?",
]
