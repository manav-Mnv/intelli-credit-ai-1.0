"""
ML Model Training Script
Trains and saves an XGBoost credit risk model.
Run once: python ml/train_model.py
"""
import os
import pickle
import numpy as np
import json

# --- Synthetic Dataset Generation ---
# Features: [debt_equity, profit_margin, current_ratio, interest_coverage, roe, debt_to_assets, ebitda_margin, revenue_growth]

def generate_training_data(n_samples: int = 5000):
    """Generate realistic synthetic credit data."""
    np.random.seed(42)

    # Healthy companies (class 0 = no default)
    n_good = int(n_samples * 0.7)
    good = np.column_stack([
        np.random.uniform(0.2, 1.8, n_good),   # D/E: low-moderate
        np.random.uniform(5, 25, n_good),        # Profit margin: decent
        np.random.uniform(1.2, 3.5, n_good),     # Current ratio: good
        np.random.uniform(2.5, 8, n_good),        # Interest coverage: good
        np.random.uniform(8, 25, n_good),         # ROE: decent
        np.random.uniform(0.2, 0.55, n_good),    # Debt/Assets: moderate
        np.random.uniform(10, 28, n_good),        # EBITDA margin: ok
        np.random.uniform(2, 18, n_good),         # Revenue growth: positive
    ])

    # Distressed companies (class 1 = high default risk)
    n_bad = n_samples - n_good
    bad = np.column_stack([
        np.random.uniform(2, 6, n_bad),           # D/E: high
        np.random.uniform(-10, 5, n_bad),         # Profit margin: thin/negative
        np.random.uniform(0.5, 1.2, n_bad),       # Current ratio: tight
        np.random.uniform(0.5, 2, n_bad),         # Interest coverage: weak
        np.random.uniform(-5, 8, n_bad),          # ROE: weak/negative
        np.random.uniform(0.6, 0.95, n_bad),      # Debt/Assets: heavy
        np.random.uniform(-5, 8, n_bad),          # EBITDA margin: thin
        np.random.uniform(-20, 2, n_bad),         # Revenue growth: declining
    ])

    # Add some noise
    good += np.random.normal(0, 0.15, good.shape)
    bad  += np.random.normal(0, 0.15, bad.shape)

    X = np.vstack([good, bad])
    y = np.array([0] * n_good + [1] * n_bad)

    # Shuffle
    idx = np.random.permutation(len(y))
    return X[idx], y[idx]


def train_and_save():
    try:
        import xgboost as xgb
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report, roc_auc_score
        print("Training XGBoost credit risk model...")

        X, y = generate_training_data(n_samples=5000)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.08,
            subsample=0.85,
            colsample_bytree=0.85,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
            early_stopping_rounds=20,
        )
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False,
        )

        # Evaluate
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_prob)
        report = classification_report(y_test, y_pred, target_names=["Good", "Default"])

        print(f"\n✅ Model trained successfully!")
        print(f"   AUC-ROC: {auc:.4f}")
        print(f"\nClassification report:\n{report}")

        # Save model
        os.makedirs("models", exist_ok=True)
        model_path = "models/credit_risk_xgb.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        print(f"\n💾 Model saved to {model_path}")

        # Save feature info
        feature_info = {
            "features": [
                "debt_equity_ratio",
                "profit_margin",
                "current_ratio",
                "interest_coverage",
                "roe",
                "debt_to_assets",
                "ebitda_margin",
                "revenue_growth",
            ],
            "model_type": "XGBoostClassifier",
            "n_estimators": 200,
            "auc_roc": round(auc, 4),
            "n_training_samples": 5000,
        }
        with open("models/model_info.json", "w") as f:
            json.dump(feature_info, f, indent=2)

        print("📋 Feature info saved to models/model_info.json")
        return model_path

    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install xgboost scikit-learn")
        return None


if __name__ == "__main__":
    train_and_save()
