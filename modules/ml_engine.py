"""
Machine Learning engine: automated Linear Regression modeling with evaluation metrics.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler


def run_linear_regression(df: pd.DataFrame, target_col: str, feature_cols: list, test_size: float = 0.2, random_state: int = 42) -> dict:
    """
    Trains a Linear Regression model to predict `target_col` from `feature_cols`.

    Returns a dict with:
        success (bool), error (str or None),
        r2, rmse, mae, coefficients (dict), intercept,
        y_test (list), y_pred (list)
    """
    if target_col not in df.columns:
        return {"success": False, "error": f"Target column '{target_col}' not found in dataset."}

    valid_features = [c for c in feature_cols if c in df.columns and c != target_col]
    if not valid_features:
        return {"success": False, "error": "No valid feature columns selected."}

    model_df = df[valid_features + [target_col]].copy()
    model_df = model_df.select_dtypes(include=[np.number])

    if target_col not in model_df.columns:
        return {"success": False, "error": f"Target column '{target_col}' must be numeric."}

    model_df = model_df.dropna()
    valid_features = [c for c in valid_features if c in model_df.columns]

    if not valid_features:
        return {"success": False, "error": "No numeric feature columns available after cleaning."}

    if len(model_df) < 10:
        return {"success": False, "error": "Not enough complete rows (need at least 10) to train a reliable model."}

    X = model_df[valid_features]
    y = model_df[target_col]

    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        model = LinearRegression()
        model.fit(X_train_scaled, y_train)

        y_pred = model.predict(X_test_scaled)

        r2 = r2_score(y_test, y_pred)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mae = mean_absolute_error(y_test, y_pred)

        coefficients = dict(zip(valid_features, model.coef_.tolist()))

        return {
            "success": True,
            "error": None,
            "r2": round(float(r2), 4),
            "rmse": round(rmse, 4),
            "mae": round(float(mae), 4),
            "coefficients": coefficients,
            "intercept": round(float(model.intercept_), 4),
            "y_test": y_test.tolist(),
            "y_pred": y_pred.tolist(),
            "features_used": valid_features,
            "target": target_col,
            "n_train": len(X_train),
            "n_test": len(X_test),
        }

    except Exception as e:
        return {"success": False, "error": f"Model training failed: {str(e)}"}
