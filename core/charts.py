"""Plotly chart factory supporting 14 chart types with a shared dark theme."""
from __future__ import annotations
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .config import PALETTE
from .theme import plotly_layout


def _agg(df, x, y, agg, color=None):
    keys = [k for k in [x, color] if k]
    if not y:
        out = df.groupby(keys, dropna=False).size().reset_index(name="count")
        return out, "count"
    if agg == "count":
        out = df.groupby(keys, dropna=False)[y].count().reset_index()
    elif agg == "nunique":
        out = df.groupby(keys, dropna=False)[y].nunique().reset_index()
    else:
        out = getattr(df.groupby(keys, dropna=False)[y], agg)().reset_index()
    return out, y


def build(df: pd.DataFrame, kind: str, x=None, y=None, color=None, size=None,
          agg="sum", top_n=None, height=420, title=None):
    """Return a themed plotly figure for the requested chart kind."""
    kind = kind.lower()
    d = df.copy()

    if kind in ("bar", "line", "area", "pie", "donut", "treemap", "sunburst", "waterfall"):
        if x is None:
            raise ValueError("This chart needs a category/X column.")
        group_color = color if kind in ("bar", "line", "area", "treemap", "sunburst") else None
        d, ycol = _agg(d, x, y, agg, group_color)
        if top_n and kind not in ("line", "area"):
            d = d.sort_values(ycol, ascending=False).head(int(top_n))

    if kind == "bar":
        fig = px.bar(d, x=x, y=ycol, color=color, barmode="group", text_auto=".2s")
    elif kind == "line":
        fig = px.line(d, x=x, y=ycol, color=color, markers=True)
    elif kind == "area":
        fig = px.area(d, x=x, y=ycol, color=color)
    elif kind in ("pie", "donut"):
        fig = px.pie(d, names=x, values=ycol, hole=0.55 if kind == "donut" else 0)
        fig.update_traces(textposition="inside", textinfo="percent")
    elif kind == "scatter":
        fig = px.scatter(d, x=x, y=y, color=color, trendline=None, opacity=0.75)
    elif kind == "bubble":
        fig = px.scatter(d, x=x, y=y, size=size or y, color=color, size_max=45, opacity=0.7)
    elif kind == "histogram":
        fig = px.histogram(d, x=x, color=color, nbins=40, opacity=0.85)
    elif kind == "box plot":
        fig = px.box(d, x=color or x, y=y or x, color=color, points="outliers")
    elif kind == "heatmap":
        pt = pd.pivot_table(d, index=x, columns=color, values=y, aggfunc=agg, fill_value=0)
        fig = px.imshow(pt, aspect="auto", color_continuous_scale="Blues", text_auto=".2s")
    elif kind == "treemap":
        path = [p for p in [color, x] if p]
        fig = px.treemap(d, path=path, values=ycol, color=ycol, color_continuous_scale="Blues")
    elif kind == "sunburst":
        path = [p for p in [color, x] if p]
        fig = px.sunburst(d, path=path, values=ycol, color=ycol, color_continuous_scale="Blues")
    elif kind == "waterfall":
        vals = d[ycol].tolist()
        fig = go.Figure(go.Waterfall(
            x=d[x].astype(str).tolist(), y=vals,
            measure=["relative"] * len(vals), connector=dict(line=dict(color="#334166")),
            increasing=dict(marker=dict(color="#22C55E")),
            decreasing=dict(marker=dict(color="#EF4444")),
            totals=dict(marker=dict(color="#5B7CFA"))))
    elif kind == "correlation matrix":
        num = d.select_dtypes(include=np.number)
        corr = num.corr(numeric_only=True).round(2)
        fig = px.imshow(corr, text_auto=True, aspect="auto", zmin=-1, zmax=1,
                        color_continuous_scale="RdBu_r")
    else:
        raise ValueError(f"Unsupported chart type: {kind}")

    if title:
        fig.update_layout(title=title)
    return plotly_layout(fig, height=height)


# ---- Purpose-built dashboard charts ---------------------------------------
def revenue_trend(ts: pd.DataFrame, height=340, label="Revenue"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ts["date"], y=ts["value"], mode="lines+markers", name=label,
        line=dict(color="#5B7CFA", width=2.2), marker=dict(size=4),
        fill="tozeroy", fillcolor="rgba(91,124,250,0.16)"))
    if len(ts) >= 7:
        fig.add_trace(go.Scatter(
            x=ts["date"], y=ts["value"].rolling(7, min_periods=1).mean(),
            mode="lines", name="7-period avg",
            line=dict(color="#F59E0B", width=1.6, dash="dot")))
    return plotly_layout(fig, height=height)


def donut(labels, values, center_label="Total", center_value=""):
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.62,
                           marker=dict(colors=PALETTE),
                           textinfo="percent", textposition="inside"))
    fig.add_annotation(text=f"<b>{center_label}</b><br>{center_value}",
                       showarrow=False, font=dict(size=14, color="#e8edf9"))
    return plotly_layout(fig, height=360)


def hbar(labels, values, height=380, color="#5B7CFA"):
    fig = go.Figure(go.Bar(x=values, y=labels, orientation="h",
                           marker=dict(color=color), text=values,
                           texttemplate="%{text:.3s}", textposition="outside"))
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return plotly_layout(fig, height=height, legend=False)


def choropleth(df, loc_col, val_col):
    fig = px.choropleth(df, locations=loc_col, locationmode="country names",
                        color=val_col, color_continuous_scale="Blues")
    fig.update_geos(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=False,
                    landcolor="#131c33", lakecolor="#0b1020")
    return plotly_layout(fig, height=360, legend=False)


def forecast_chart(hist: pd.DataFrame, fc: pd.DataFrame, height=380):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist["date"], y=hist["value"], name="Actual",
                             line=dict(color="#22C55E", width=2)))
    fig.add_trace(go.Scatter(x=fc["date"], y=fc["upper"], name="Upper",
                             line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=fc["date"], y=fc["lower"], name="Confidence band",
                             fill="tonexty", fillcolor="rgba(34,197,94,0.14)",
                             line=dict(width=0)))
    fig.add_trace(go.Scatter(x=fc["date"], y=fc["forecast"], name="Forecast",
                             line=dict(color="#22C55E", width=2, dash="dot")))
    return plotly_layout(fig, height=height)


def anomaly_chart(ts: pd.DataFrame, anomalies: pd.DataFrame, height=380):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ts["date"], y=ts["value"], name="Value",
                             line=dict(color="#5B7CFA", width=2)))
    if not anomalies.empty:
        fig.add_trace(go.Scatter(
            x=anomalies["date"], y=anomalies["value"], mode="markers", name="Anomaly",
            marker=dict(color="#EF4444", size=11, symbol="circle-open", line=dict(width=2.5))))
    return plotly_layout(fig, height=height)
