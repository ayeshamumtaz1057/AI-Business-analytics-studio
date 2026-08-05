"""
Statistical calculations and AI Insight Generation engine.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any


def calculate_metadata(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates primary descriptive KPIs for dataset metadata.
    """
    total_cells = df.shape[0] * df.shape[1]
    total_nulls = df.isna().sum().sum()
    null_pct = (total_nulls / total_cells * 100) if total_cells > 0 else 0
    dup_rows = df.duplicated().sum()
    dup_pct = (dup_rows / len(df) * 100) if len(df) > 0 else 0
    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "total_nulls": int(total_nulls),
        "null_pct": round(null_pct, 2),
        "duplicate_rows": int(dup_rows),
        "duplicate_pct": round(dup_pct, 2),
        "memory_mb": round(memory_mb, 2)
    }


def compute_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates detailed descriptive statistics for numerical columns.
    """
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return pd.DataFrame()

    stats_df = pd.DataFrame({
        "Mean": numeric_df.mean(),
        "Median": numeric_df.median(),
        "Mode": numeric_df.mode().iloc[0] if not numeric_df.mode().empty else np.nan,
        "Variance": numeric_df.var(),
        "Std Dev": numeric_df.std(),
        "Min": numeric_df.min(),
        "25% (Q1)": numeric_df.quantile(0.25),
        "75% (Q3)": numeric_df.quantile(0.75),
        "Max": numeric_df.max()
    })
    return stats_df.round(3)


def generate_ai_insights(df: pd.DataFrame, meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates automated analytical narratives, data quality scores, and recommendations.
    """
    insights = []
    recommendations = []

    # 1. Quality Score Calculation (Scale 0-100)
    quality_score = 100 - (meta["null_pct"] * 0.6 + meta["duplicate_pct"] * 0.4)
    quality_score = max(0, min(100, round(quality_score, 1)))

    # 2. Structure Insights
    insights.append(f"The dataset consists of **{meta['rows']:,}** rows and **{meta['columns']}** features.")
    
    if meta["null_pct"] > 0:
        insights.append(f"Missing data represents **{meta['null_pct']}%** of all values.")
        recommendations.append("Apply missing value imputation prior to downstream machine learning models.")
    else:
        insights.append("The dataset contains zero missing values.")

    if meta["duplicate_pct"] > 0:
        insights.append(f"Found **{meta['duplicate_rows']:,}** duplicate records ({meta['duplicate_pct']}%).")
        recommendations.append("Execute data deduplication to eliminate redundant observation rows.")

    # 3. Business Context Discovery (Top & Bottom Categories)
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    num_cols = df.select_dtypes(include=[np.number]).columns

    top_cat_insight = None
    if len(cat_cols) > 0 and len(num_cols) > 0:
        primary_cat = cat_cols[0]
        primary_num = num_cols[0]
        
        grouped = df.groupby(primary_cat)[primary_num].sum().sort_values(ascending=False)
        if not grouped.empty:
            highest_cat = grouped.index[0]
            highest_val = grouped.iloc[0]
            lowest_cat = grouped.index[-1]
            lowest_val = grouped.iloc[-1]
            
            top_cat_insight = {
                "category_col": primary_cat,
                "metric_col": primary_num,
                "highest_cat": str(highest_cat),
                "highest_val": round(highest_val, 2),
                "lowest_cat": str(lowest_cat),
                "lowest_val": round(lowest_val, 2)
            }
            insights.append(
                f"For **{primary_cat}**, the highest performing value based on **{primary_num}** is "
                f"**{highest_cat}** ({highest_val:,.2f}), while **{lowest_cat}** represents the lowest ({lowest_val:,.2f})."
            )

    if not recommendations:
        recommendations.append("Data hygiene is high. Proceed directly to feature engineering or predictive modeling.")

    summary_paragraph = (
        f"This dataset carries a overall Quality Score of {quality_score}/100. "
        f"It contains {meta['rows']} records across {meta['columns']} attributes. "
        f"Data completion rate sits at {100 - meta['null_pct']:.1f}% with "
        f"{'minimal' if meta['duplicate_pct'] < 5 else 'significant'} duplication detected."
    )

    return {
        "quality_score": quality_score,
        "summary": summary_paragraph,
        "insights": insights,
        "recommendations": recommendations,
        "top_cat_insight": top_cat_insight
    }
