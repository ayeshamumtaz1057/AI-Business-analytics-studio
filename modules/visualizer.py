"""
Interactive Plotly charting generator engine.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


TEMPLATE = "plotly_dark"
COLOR_SEQUENCE = px.colors.qualitative.Plotly


def render_chart(chart_type: str, df: pd.DataFrame, x_col: str, y_col: str = None, color_col: str = None) -> go.Figure:
    """
    Renders dynamic Plotly charts based on user configuration.
    """
    fig = go.Figure()

    if chart_type == "Bar Chart":
        fig = px.bar(df, x=x_col, y=y_col, color=color_col, template=TEMPLATE, color_discrete_sequence=COLOR_SEQUENCE)

    elif chart_type == "Line Chart":
        fig = px.line(df, x=x_col, y=y_col, color=color_col, template=TEMPLATE)

    elif chart_type == "Scatter Plot":
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, template=TEMPLATE, trendline="ols" if y_col else None)

    elif chart_type == "Pie Chart":
        fig = px.pie(df, names=x_col, values=y_col, template=TEMPLATE)

    elif chart_type == "Histogram":
        fig = px.histogram(df, x=x_col, color=color_col, template=TEMPLATE, marginal="box")

    elif chart_type == "Box Plot":
        fig = px.box(df, x=x_col, y=y_col, color=color_col, template=TEMPLATE)

    elif chart_type == "Correlation Matrix":
        num_df = df.select_dtypes(include=[np.number])
        if not num_df.empty:
            corr = num_df.corr().round(2)
            fig = px.imshow(corr, text_auto=True, template=TEMPLATE, color_continuous_scale="Viridis")
        else:
            fig.add_annotation(text="No numeric columns available for correlation", showarrow=False)

    elif chart_type == "Treemap":
        if color_col and color_col != x_col:
            fig = px.treemap(df, path=[x_col, color_col], values=y_col, template=TEMPLATE)
        else:
            fig = px.treemap(df, path=[x_col], values=y_col, template=TEMPLATE)

    elif chart_type == "Sunburst Chart":
        if color_col and color_col != x_col:
            fig = px.sunburst(df, path=[x_col, color_col], values=y_col, template=TEMPLATE)
        else:
            fig = px.sunburst(df, path=[x_col], values=y_col, template=TEMPLATE)

    elif chart_type == "Area Chart":
        fig = px.area(df, x=x_col, y=y_col, color=color_col, template=TEMPLATE)

    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig
