"""
Visualizer module: renders interactive Plotly charts for the Streamlit app.
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

DARK_TEMPLATE = "plotly_dark"

CHART_TYPES = [
    "Bar Chart",
    "Line Chart",
    "Scatter Plot",
    "Histogram",
    "Box Plot",
    "Pie Chart",
    "Correlation Heatmap",
    "Treemap",
    "Sunburst",
]


def render_chart(df: pd.DataFrame, chart_type: str, x: str = None, y: str = None, color: str = None, title: str = None):
    """
    Builds and returns a Plotly figure based on the requested chart_type.

    Args:
        df: source DataFrame
        chart_type: one of CHART_TYPES
        x, y, color: column names (usage depends on chart_type)
        title: optional chart title

    Returns:
        plotly.graph_objects.Figure, or None with a raised ValueError on bad input.
    """
    if df is None or df.empty:
        raise ValueError("Cannot render chart: dataset is empty.")

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    title = title or (f"{chart_type}" + (f": {y} by {x}" if x and y else ""))

    if chart_type == "Bar Chart":
        if not x:
            raise ValueError("Bar Chart requires an 'x' column.")
        if y:
            fig = px.bar(df, x=x, y=y, color=color, title=title, template=DARK_TEMPLATE)
        else:
            counts = df[x].value_counts().reset_index()
            counts.columns = [x, "count"]
            fig = px.bar(counts, x=x, y="count", title=title, template=DARK_TEMPLATE)

    elif chart_type == "Line Chart":
        if not (x and y):
            raise ValueError("Line Chart requires both 'x' and 'y' columns.")
        fig = px.line(df, x=x, y=y, color=color, title=title, template=DARK_TEMPLATE)

    elif chart_type == "Scatter Plot":
        if not (x and y):
            raise ValueError("Scatter Plot requires both 'x' and 'y' columns.")
        fig = px.scatter(df, x=x, y=y, color=color, title=title, template=DARK_TEMPLATE, trendline=None)

    elif chart_type == "Histogram":
        if not x:
            raise ValueError("Histogram requires an 'x' column.")
        fig = px.histogram(df, x=x, color=color, title=title, template=DARK_TEMPLATE)

    elif chart_type == "Box Plot":
        if not y:
            raise ValueError("Box Plot requires a 'y' (numeric) column.")
        fig = px.box(df, x=x, y=y, color=color, title=title, template=DARK_TEMPLATE)

    elif chart_type == "Pie Chart":
        if not x:
            raise ValueError("Pie Chart requires a 'x' (category) column.")
        counts = df[x].value_counts().reset_index()
        counts.columns = [x, "count"]
        fig = px.pie(counts, names=x, values="count", title=title, template=DARK_TEMPLATE)

    elif chart_type == "Correlation Heatmap":
        if len(numeric_cols) < 2:
            raise ValueError("Correlation Heatmap requires at least 2 numeric columns.")
        corr = df[numeric_cols].corr(numeric_only=True)
        fig = px.imshow(
            corr, text_auto=".2f", aspect="auto",
            color_continuous_scale="RdBu_r", title=title or "Correlation Heatmap",
            template=DARK_TEMPLATE
        )

    elif chart_type == "Treemap":
        if not x:
            raise ValueError("Treemap requires an 'x' (category) column.")
        path = [x] if not color else [x, color]
        values = y if y and y in numeric_cols else None
        fig = px.treemap(df, path=path, values=values, title=title, template=DARK_TEMPLATE)

    elif chart_type == "Sunburst":
        if not x:
            raise ValueError("Sunburst requires at least an 'x' (category) column.")
        path = [x] if not color else [x, color]
        values = y if y and y in numeric_cols else None
        fig = px.sunburst(df, path=path, values=values, title=title, template=DARK_TEMPLATE)

    else:
        raise ValueError(f"Unsupported chart type: '{chart_type}'. Choose from {CHART_TYPES}")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#F8FAFC",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig
