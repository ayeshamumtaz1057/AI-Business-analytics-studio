"""Auto-detection of semantic column roles (date / revenue / customer ...)."""
from __future__ import annotations
import re

import pandas as pd
from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype

from .config import ROLES, ROLE_PATTERNS
from .utils import is_text


def _is_dateish(s: pd.Series) -> bool:
    if is_datetime64_any_dtype(s):
        return True
    if is_text(s):
        sample = s.dropna().astype(str).head(40)
        if sample.empty:
            return False
        ok = pd.to_datetime(sample, errors="coerce", format="mixed").notna().mean()
        return ok > 0.8
    return False


def auto_map(df: pd.DataFrame) -> dict:
    """Best-effort mapping of dataframe columns onto semantic roles."""
    mapping = {r: None for r in ROLES}
    used = set()

    def score(role: str, column) -> int:
        """Higher is better; 0 means the column cannot fill this role."""
        name = str(column).lower().strip()
        m = re.search(ROLE_PATTERNS[role], name)
        if not m:
            return 0
        if role in ("revenue", "profit", "cost", "quantity") and not is_numeric_dtype(df[column]):
            return 0
        if role == "date" and not _is_dateish(df[column]):
            return 0
        token = re.sub(r"[^a-z]", "", m.group(0))
        base = 10
        if name in (token, token + "s"):          # exact column name match
            base = 40
        elif name.startswith(token):              # e.g. "category_name"
            base = 30
        elif name.endswith(token):                # e.g. "order_date"
            base = 20
        # a column whose name also matches an *earlier*, more specific role loses points
        for other in ROLES:
            if other != role and re.search(ROLE_PATTERNS[other], name):
                base -= 4
        return base

    for role in ROLES:
        candidates = [(score(role, c), c) for c in df.columns if c not in used]
        candidates = [(s_, c) for s_, c in candidates if s_ > 0]
        if candidates:
            best = max(candidates, key=lambda t: t[0])[1]
            mapping[role] = best
            used.add(best)

    # Fallbacks -----------------------------------------------------------
    if mapping["date"] is None:
        for c in df.columns:
            if c not in used and _is_dateish(df[c]):
                mapping["date"] = c
                used.add(c)
                break
    if mapping["revenue"] is None:
        nums = [c for c in df.columns if is_numeric_dtype(df[c]) and c not in used]
        if nums:
            # pick the numeric column with the largest total — usually the money column
            best = max(nums, key=lambda c: float(pd.to_numeric(df[c], errors="coerce").abs().sum()))
            mapping["revenue"] = best
            used.add(best)
    return mapping


def coerce_types(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """Return a copy with mapped date/numeric columns coerced to proper dtypes."""
    out = df.copy()
    d = mapping.get("date")
    if d and d in out.columns and not is_datetime64_any_dtype(out[d]):
        out[d] = pd.to_datetime(out[d], errors="coerce", format="mixed")
    for role in ("revenue", "profit", "cost", "quantity"):
        c = mapping.get(role)
        if c and c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    return out
