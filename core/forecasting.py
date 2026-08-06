"""Time-series forecasting (Ridge on calendar + lag features, with fallbacks)."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

MODELS = ["Ridge Regression (trend + seasonality)", "Random Forest", "Moving Average", "Linear Trend"]


def _features(dates: pd.Series, t0) -> pd.DataFrame:
    d = pd.to_datetime(dates)
    t = (d - t0).dt.days.astype(float)
    return pd.DataFrame({
        "t": t,
        "dow_sin": np.sin(2 * np.pi * d.dt.dayofweek / 7),
        "dow_cos": np.cos(2 * np.pi * d.dt.dayofweek / 7),
        "moy_sin": np.sin(2 * np.pi * d.dt.month / 12),
        "moy_cos": np.cos(2 * np.pi * d.dt.month / 12),
        "dom": d.dt.day,
        "is_weekend": (d.dt.dayofweek >= 5).astype(int),
    })


def forecast(ts: pd.DataFrame, horizon: int = 90, model: str = MODELS[0],
             freq: str = "D") -> tuple[pd.DataFrame, dict]:
    """ts: DataFrame with columns [date, value]. Returns (forecast_df, metrics)."""
    ts = ts.dropna().sort_values("date").reset_index(drop=True)
    if len(ts) < 8:
        raise ValueError("Need at least 8 historical points to forecast.")

    t0 = ts["date"].min()
    X = _features(ts["date"], t0)
    y = ts["value"].astype(float).values

    step = {"D": "D", "W": "W", "M": "MS"}.get(freq, "D")
    future_dates = pd.date_range(ts["date"].max(), periods=horizon + 1, freq=step)[1:]
    Xf = _features(pd.Series(future_dates), t0)

    split = max(int(len(ts) * 0.8), len(ts) - 60)
    metrics = {}

    if model.startswith("Ridge"):
        est = Ridge(alpha=1.0)
    elif model.startswith("Random"):
        est = RandomForestRegressor(n_estimators=250, min_samples_leaf=2, random_state=42)
    elif model.startswith("Moving"):
        est = None
    else:
        est = Ridge(alpha=1e-6)
        X, Xf = X[["t"]], Xf[["t"]]

    if est is not None:
        est.fit(X.iloc[:split], y[:split])
        if split < len(ts):
            pred_v = est.predict(X.iloc[split:])
            metrics["MAE"] = float(mean_absolute_error(y[split:], pred_v))
            try:
                metrics["MAPE %"] = float(mean_absolute_percentage_error(y[split:], pred_v) * 100)
            except Exception:
                pass
        est.fit(X, y)
        pred = est.predict(Xf)
        resid = y - est.predict(X)
    else:
        window = min(14, max(3, len(ts) // 6))
        base = float(pd.Series(y).tail(window).mean())
        slope = float(np.polyfit(np.arange(len(y)), y, 1)[0])
        pred = base + slope * np.arange(1, horizon + 1)
        resid = y - pd.Series(y).rolling(window, min_periods=1).mean().values
        metrics["MAE"] = float(np.mean(np.abs(resid)))

    sigma = float(np.nanstd(resid)) or float(np.nanstd(y)) * 0.1
    growth = np.sqrt(np.arange(1, horizon + 1) / max(len(ts), 1) + 1)
    pred = np.clip(pred, 0, None)

    out = pd.DataFrame({
        "date": future_dates,
        "forecast": pred,
        "lower": np.clip(pred - 1.96 * sigma * growth, 0, None),
        "upper": pred + 1.96 * sigma * growth,
    })
    metrics["Historical total"] = float(y.sum())
    metrics["Forecast total"] = float(pred.sum())
    hist_window = float(pd.Series(y).tail(min(horizon, len(y))).sum())
    metrics["Expected growth %"] = ((pred.sum() - hist_window) / hist_window * 100
                                    if hist_window else np.nan)
    return out, metrics


def scenario(fc: pd.DataFrame, uplift_pct: float) -> pd.DataFrame:
    out = fc.copy()
    for c in ("forecast", "lower", "upper"):
        out[c] = out[c] * (1 + uplift_pct / 100)
    return out
