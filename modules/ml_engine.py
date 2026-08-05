"""
Automated Linear Regression modeling and evaluation engine.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from typing import Tuple, Dict, Any, Optional


def run_linear_regression(
    df: pd.DataFrame, target_col: str, feature_cols: list
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Fits a Scikit-Learn Linear Regression model and computes performance metrics.
    """
    if not target_col or not feature_cols:
        return None, "Target column and feature columns must be specified."

    # Filter numeric data without missing values
    data = df[[target_col] + feature_cols].dropna()
    
    # Filter strictly numeric types for simple automated training
    data = data.select_dtypes(include=[np.number])

    if data.shape[0] < 10:
        return None, "Insufficient clean numeric data points (minimum 10 required) for training."

    if target_col not in data.columns:
        return None, "Target column must be numeric."

    X = data[feature_cols]
    y = data[target_col]

    if X.empty:
        return None, "Selected features do not contain sufficient numeric data."

    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LinearRegression()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)

        # Prepare comparative table
        results_df = pd.DataFrame({
            "Actual": y_test.values,
            "Predicted": y_pred,
            "Residual": y_test.values - y_pred
        }).round(3)

        metrics = {
            "r2": round(r2, 4),
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "results_df": results_df,
            "model": model,
            "features": feature_cols,
            "target": target_col
        }
        return metrics, None

    except Exception as e:
        return None, f"ML Execution error: {str(e)}"
