"""
Analytics module for statistical calculations and automated insights.
"""
import pandas as pd
import numpy as np


def calculate_metadata(df: pd.DataFrame) -> dict:
    """
    Calculates high-level metadata used in the Executive Dataset Overview.

    Returns a dict with:
        rows, columns, null_cells, null_pct, duplicate_rows,
        numeric_columns, categorical_columns, data_health_score
    """
    total_cells = df.shape[0] * df.shape[1] if df.shape[1] else 0
    null_cells = int(df.isna().sum().sum())
    null_pct = round((null_cells / total_cells) * 100, 2) if total_cells else 0.0
    duplicate_rows = int(df.duplicated().sum())

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    # Data Health Score (0-100): penalizes missing data and duplicate rows
    completeness = 100 - null_pct
    dup_penalty = min(20, (duplicate_rows / max(len(df), 1)) * 100)
    health_score = max(0, round(completeness - dup_penalty, 1))

    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "null_cells": null_cells,
        "null_pct": null_pct,
        "duplicate_rows": duplicate_rows,
        "numeric_columns": len(numeric_cols),
        "categorical_columns": len(categorical_cols),
        "data_health_score": health_score,
    }


def compute_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes descriptive summary statistics for all numeric columns.
    Falls back to an empty-but-valid DataFrame if there are no numeric columns.
    """
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return pd.DataFrame({"Info": ["No numeric columns found in dataset."]})
    return numeric_df.describe().T.reset_index().rename(columns={"index": "Column"})


def generate_ai_insights(df: pd.DataFrame, meta: dict) -> dict:
    """
    Generates rule-based insights and recommendations about the dataset.
    Returns {"insights": [...], "recommendations": [...]}
    """
    insights = []
    recommendations = []

    # Size / shape insight
    insights.append(
        f"Dataset contains {meta['rows']:,} rows and {meta['columns']} columns "
        f"({meta['numeric_columns']} numeric, {meta['categorical_columns']} categorical)."
    )

    # Missing data
    if meta["null_pct"] > 0:
        insights.append(f"Missing data accounts for {meta['null_pct']}% of all cells.")
        if meta["null_pct"] > 15:
            recommendations.append(
                "High proportion of missing values detected — consider reviewing data "
                "collection processes or applying an imputation strategy."
            )
    else:
        insights.append("No missing values detected — dataset is complete.")

    # Duplicates
    if meta["duplicate_rows"] > 0:
        insights.append(f"{meta['duplicate_rows']} duplicate row(s) were found in the raw data.")
        recommendations.append("Enable duplicate removal to ensure metrics aren't inflated.")

    # Numeric column insights (skew, outliers, correlation)
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        for col in numeric_df.columns[:5]:
            series = numeric_df[col].dropna()
            if series.empty:
                continue
            skew = series.skew()
            if abs(skew) > 1:
                direction = "right" if skew > 0 else "left"
                insights.append(f"'{col}' is heavily {direction}-skewed (skew={skew:.2f}).")

        if len(numeric_df.columns) >= 2:
            corr = numeric_df.corr(numeric_only=True)
            corr_pairs = (
                corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
                .stack()
                .sort_values(key=lambda s: s.abs(), ascending=False)
            )
            if not corr_pairs.empty:
                top_pair = corr_pairs.index[0]
                top_val = corr_pairs.iloc[0]
                if abs(top_val) > 0.6:
                    insights.append(
                        f"Strong correlation ({top_val:.2f}) found between "
                        f"'{top_pair[0]}' and '{top_pair[1]}'."
                    )
                    recommendations.append(
                        f"Explore the relationship between '{top_pair[0]}' and "
                        f"'{top_pair[1]}' further using regression or scatter analysis."
                    )

    # Categorical column insights (dominant category)
    categorical_df = df.select_dtypes(exclude=[np.number])
    for col in categorical_df.columns[:3]:
        counts = categorical_df[col].value_counts()
        if not counts.empty:
            top_val = counts.index[0]
            top_share = round((counts.iloc[0] / len(categorical_df)) * 100, 1)
            if top_share > 50:
                insights.append(
                    f"'{col}' is dominated by '{top_val}' ({top_share}% of records)."
                )

    if meta["data_health_score"] >= 90:
        recommendations.append("Data quality is excellent — ready for modeling or reporting.")
    elif meta["data_health_score"] >= 70:
        recommendations.append("Data quality is good, with minor cleanup opportunities remaining.")
    else:
        recommendations.append("Data quality needs attention before it's used for critical decisions.")

    if not insights:
        insights.append("No notable patterns detected in this dataset.")
    if not recommendations:
        recommendations.append("No specific recommendations — dataset looks ready to use.")

    return {"insights": insights, "recommendations": recommendations}
