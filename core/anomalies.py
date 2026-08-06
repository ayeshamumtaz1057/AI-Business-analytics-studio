"""Anomaly detection over time series and transactions."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

METHODS = ["Z-Score", "IQR", "Rolling Z-Score", "Isolation Forest"]


def detect_timeseries(ts: pd.DataFrame, method="Rolling Z-Score", sensitivity=3.0,
                      window=14) -> pd.DataFrame:
    """ts: [date, value]. Returns anomalies with direction + severity."""
    d = ts.dropna().sort_values("date").reset_index(drop=True)
    if len(d) < 5:
        return pd.DataFrame()
    v = d["value"].astype(float)

    if method == "Z-Score":
        score = (v - v.mean()) / (v.std() or 1)
    elif method == "IQR":
        q1, q3 = v.quantile(0.25), v.quantile(0.75)
        iqr = (q3 - q1) or 1
        score = (v - v.median()) / iqr
        sensitivity = max(sensitivity * 0.75, 1.0)
    elif method == "Isolation Forest":
        model = IsolationForest(contamination=min(0.12, max(0.01, 4.0 / sensitivity / 100 * 3)),
                                random_state=42)
        flags = model.fit_predict(v.values.reshape(-1, 1)) == -1
        score = pd.Series(np.where(flags, np.sign(v - v.mean()) * (sensitivity + 0.5), 0.0))
    else:  # Rolling Z-Score
        roll_m = v.rolling(window, min_periods=3, center=True).mean()
        roll_s = v.rolling(window, min_periods=3, center=True).std().replace(0, np.nan)
        score = (v - roll_m) / roll_s

    d["score"] = score.fillna(0).round(2)
    out = d[d["score"].abs() >= sensitivity].copy()
    if out.empty:
        return out
    out["Direction"] = np.where(out["score"] > 0, "Spike ▲", "Drop ▼")
    out["Severity"] = pd.cut(out["score"].abs(), [0, sensitivity * 1.3, sensitivity * 2, 1e9],
                             labels=["Moderate", "High", "Critical"]).astype(str)
    return out.reset_index(drop=True)


def detect_transactions(df: pd.DataFrame, columns, contamination=0.02) -> pd.DataFrame:
    num = df[list(columns)].apply(pd.to_numeric, errors="coerce").fillna(0)
    if num.empty or len(num) < 20:
        return pd.DataFrame()
    model = IsolationForest(contamination=contamination, random_state=42, n_estimators=200)
    pred = model.fit_predict(num)
    scores = model.score_samples(num)
    out = df.loc[pred == -1].copy()
    out["Anomaly Score"] = np.round(scores[pred == -1], 4)
    return out.sort_values("Anomaly Score").reset_index(drop=True)


def summarize(anoms: pd.DataFrame) -> str:
    if anoms.empty:
        return "No anomalies detected at the current sensitivity."
    spikes = int((anoms.get("Direction", pd.Series(dtype=str)) == "Spike ▲").sum())
    drops = len(anoms) - spikes
    worst = anoms.loc[anoms["score"].abs().idxmax()]
    return (f"{len(anoms)} anomalies detected — {spikes} spikes and {drops} drops. "
            f"The most extreme was on {pd.to_datetime(worst['date']).date()} "
            f"(value {worst['value']:,.0f}, z={worst['score']}).")
