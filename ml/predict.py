"""
Predict default probability using saved XGBoost model.
Used by risk_engine.py when a trained model file exists.
"""
import pickle
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

_model = None
_model_path = os.path.join(os.path.dirname(__file__), "models", "credit_risk_xgb.pkl")


def load_model():
    global _model
    if _model is not None:
        return _model
    if os.path.exists(_model_path):
        try:
            with open(_model_path, "rb") as f:
                _model = pickle.load(f)
            logger.info(f"Loaded trained XGBoost model from {_model_path}")
        except Exception as e:
            logger.warning(f"Failed to load saved model: {e}")
    return _model


def predict_default_probability(
    debt_equity: float = 1.0,
    profit_margin: float = 10.0,
    current_ratio: float = 1.5,
    interest_coverage: float = 3.0,
    roe: float = 10.0,
    debt_to_assets: float = 0.5,
    ebitda_margin: float = 12.0,
    revenue_growth: float = 5.0,
) -> float:
    """Return default probability (0-1) from the trained XGBoost model."""
    model = load_model()
    if not model:
        # Heuristic fallback
        risk = min(1.0, max(0.0,
            (max(0, debt_equity - 1) * 0.12) +
            (max(0, 5 - profit_margin) * 0.025) +
            (max(0, 1.5 - current_ratio) * 0.18) +
            (max(0, 2 - interest_coverage) * 0.12)
        ))
        return round(risk, 4)

    features = np.array([[
        debt_equity, profit_margin, current_ratio, interest_coverage,
        roe, debt_to_assets, ebitda_margin, revenue_growth,
    ]])
    try:
        return round(float(model.predict_proba(features)[0][1]), 4)
    except Exception as e:
        logger.warning(f"Model prediction failed: {e}")
        return 0.3
