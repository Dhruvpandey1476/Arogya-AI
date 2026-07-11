"""
Training script for severity classification model.
Generates synthetic training data using medical rules, then trains XGBoost.
Run this BEFORE the hackathon.
"""

import numpy as np
import pandas as pd
import pickle
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

import config

OUTPUT_PATH = config.SEVERITY_MODEL_PATH
SYNTHETIC_DATA_PATH = config.SEVERITY_DATASET_PATH

SEVERITY_MAP = {"Low": 0, "Medium": 1, "High": 2, "Emergency": 3}
REVERSE_MAP = {v: k for k, v in SEVERITY_MAP.items()}

HIGH_RISK_FLAG_WEIGHT = 3
MEDIUM_RISK_FLAG_WEIGHT = 1


def generate_synthetic_data(n_samples: int = 5000) -> pd.DataFrame:
    """Generate synthetic severity training data based on medical rules."""
    np.random.seed(42)
    records = []

    for _ in range(n_samples):
        pain_scale = np.random.randint(0, 11)
        duration_days = np.random.randint(1, 30)
        symptom_count = np.random.randint(1, 10)
        high_risk_count = np.random.randint(0, 4)
        medium_risk_count = np.random.randint(0, 5)
        fever_flag = np.random.randint(0, 2)
        fever_val = np.random.uniform(37.0, 40.5) if fever_flag else 37.0
        elderly = np.random.randint(0, 2)
        child = np.random.randint(0, 2)

        # Rule-based label generation
        if (
            pain_scale >= 9
            or high_risk_count >= 2
            or (high_risk_count >= 1 and pain_scale >= 7)
        ):
            severity = 3  # Emergency
        elif (
            pain_scale >= 7
            or (fever_flag and fever_val > 39.5)
            or (high_risk_count >= 1)
            or (elderly and symptom_count >= 5)
        ):
            severity = 2  # High
        elif (
            pain_scale >= 5
            or duration_days > 7
            or medium_risk_count >= 2
            or (fever_flag and fever_val > 38.5)
        ):
            severity = 1  # Medium
        else:
            severity = 0  # Low

        # Add some noise to prevent perfect rule memorization
        if np.random.random() < 0.05:
            severity = max(0, min(3, severity + np.random.choice([-1, 1])))

        records.append({
            "pain_scale": pain_scale,
            "duration_days": duration_days,
            "symptom_count": symptom_count,
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "fever_flag": fever_flag,
            "fever_val": fever_val,
            "elderly": elderly,
            "child": child,
            "severity": severity,
        })

    return pd.DataFrame(records)


def train():
    print("Generating synthetic severity data...")
    df = generate_synthetic_data(5000)

    SYNTHETIC_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SYNTHETIC_DATA_PATH, index=False)
    print(f"Saved synthetic data: {SYNTHETIC_DATA_PATH}")

    feature_cols = [
        "pain_scale", "duration_days", "symptom_count",
        "high_risk_count", "medium_risk_count",
        "fever_flag", "fever_val", "elderly", "child",
    ]
    X = df[feature_cols].values
    y = df["severity"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training severity XGBoost classifier...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        random_state=42,
        eval_metric="mlogloss",
        tree_method="hist",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {acc:.4f} ({acc*100:.1f}%)")
    print(classification_report(y_test, y_pred, target_names=["Low", "Medium", "High", "Emergency"]))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "wb") as f:
        pickle.dump({
            "model": model,
            "feature_names": feature_cols,
        }, f)

    print(f"Severity model saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    train()
