"""Small dtype helpers that behave identically on pandas 2.x and 3.x.

pandas 3 introduced a dedicated string dtype, so `df[c].dtype == object` is no
longer a reliable test for "this is a text column".
"""
from __future__ import annotations

import pandas as pd
from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype, is_string_dtype


def is_text(s: pd.Series) -> bool:
    if is_numeric_dtype(s) or is_datetime64_any_dtype(s):
        return False
    return s.dtype == object or is_string_dtype(s) or str(s.dtype) in ("category", "str")


def text_columns(df: pd.DataFrame) -> list:
    return [c for c in df.columns if is_text(df[c])]


def numeric_columns(df: pd.DataFrame) -> list:
    return [c for c in df.columns if is_numeric_dtype(df[c])]
