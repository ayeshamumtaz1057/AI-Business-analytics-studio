"""
Automated data cleaning and transformation module.
"""
import pandas as pd
import numpy as np
from typing import Tuple, List


def get_column_types(df: pd.DataFrame) -> dict:
    """
    Categorize columns into Numeric, Categorical, and Date types.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Identify potential date columns
    date_cols = []
    categorical_cols = []

    for col in df.select_dtypes(include=['object', 'category', 'datetime']).columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_cols.append(col)
        else:
            # Check if strings look like dates
            sample = df[col].dropna().astype(str).head(20)
            if not sample.empty:
                try:
                    parsed = pd.to_datetime(sample, errors='coerce')
                    if parsed.notna().sum() / len(sample) > 0.7:
                        date_cols.append(col)
                        continue
                except Exception:
                    pass
            categorical_cols.append(col)

    return {
        "numeric": numeric_cols,
        "categorical": categorical_cols,
        "date": date_cols
    }


def clean_dataset(df: pd.DataFrame, drop_duplicates: bool = True, fill_na: str = "Mean/Mode") -> Tuple[pd.DataFrame, dict]:
    """
    Applies automated cleaning transformations based on user-selected options:
    - Removes duplicate rows (if drop_duplicates=True)
    - Removes completely empty columns
    - Converts date string columns to datetime
    - Handles missing values per fill_na:
        "Mean/Mode"  -> numeric NaNs filled with Median, categorical NaNs filled with Mode
        "Drop Rows"  -> rows containing any NaN are dropped
        "None"       -> missing values left untouched
    """
    cleaned_df = df.copy()
    stats = {
        "duplicates_removed": 0,
        "columns_removed": 0,
        "missing_imputed": 0,
        "dates_converted": 0
    }

    # 1. Deduplication
    if drop_duplicates:
        initial_rows = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        stats["duplicates_removed"] = initial_rows - len(cleaned_df)

    # 2. Remove entirely empty columns
    initial_cols = cleaned_df.shape[1]
    cleaned_df = cleaned_df.dropna(how='all', axis=1)
    stats["columns_removed"] = initial_cols - cleaned_df.shape[1]

    col_types = get_column_types(cleaned_df)

    # 3. Handle Date Conversions
    for col in col_types["date"]:
        if not pd.api.types.is_datetime64_any_dtype(cleaned_df[col]):
            try:
                cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                stats["dates_converted"] += 1
            except Exception:
                pass

    # 4. Handle missing values based on user selection
    total_missing_before = cleaned_df.isna().sum().sum()

    if fill_na == "Mean/Mode":
        for col in cleaned_df.columns:
            if cleaned_df[col].isna().sum() > 0:
                if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                    median_val = cleaned_df[col].median()
                    cleaned_df[col] = cleaned_df[col].fillna(median_val if pd.notna(median_val) else 0)
                else:
                    mode_val = cleaned_df[col].mode()
                    fill_val = mode_val[0] if not mode_val.empty else "Unknown"
                    cleaned_df[col] = cleaned_df[col].fillna(fill_val)
        stats["missing_imputed"] = int(total_missing_before)
    elif fill_na == "Drop Rows":
        before = len(cleaned_df)
        cleaned_df = cleaned_df.dropna()
        stats["missing_imputed"] = before - len(cleaned_df)
    # fill_na == "None": leave missing values untouched

    return cleaned_df, stats
