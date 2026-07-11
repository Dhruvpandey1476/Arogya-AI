"""
Training script for disease prediction model.
Run this BEFORE the hackathon.

Dataset: https://www.kaggle.com/datasets/itachi9604/disease-symptom-description-dataset
Download and place as: backend/data/raw/disease_symptom.csv
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))  # insert at the beginning

import config

DATASET_PATH = config.DISEASE_DATASET_PATH
MODEL_OUTPUT_PATH = config.DISEASE_MODEL_PATH


def load_and_preprocess():
    print("Loading dataset...")
    df = pd.read_csv(DATASET_PATH)

    df.columns = [c.strip() for c in df.columns]

    symptom_cols = [c for c in df.columns if c.startswith("Symptom")]
    target_col = "Disease"

    # Collect every unique symptom
    all_symptoms = set()

    for col in symptom_cols:
        vals = (
            df[col]
            .dropna()
            .astype(str)
            .str.strip()
        )
        all_symptoms.update(vals)

    all_symptoms = sorted(all_symptoms)

    # Binary feature matrix
    X = pd.DataFrame(0, index=df.index, columns=all_symptoms)

    for col in symptom_cols:
        for idx, symptom in df[col].items():
            if pd.notna(symptom):
                symptom = str(symptom).strip()
                X.at[idx, symptom] = 1

    y = df[target_col].str.strip().values

    print("Feature matrix:", X.shape)
    print("Diseases:", len(np.unique(y)))

    return X.values, y, list(X.columns)

def train():
    X, y, feature_names = load_and_preprocess()

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    print("\nTraining ensemble model (RF + XGBoost + SVM)...")

    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    xgb = XGBClassifier(
        n_estimators=200, random_state=42, use_label_encoder=False,
        eval_metric="mlogloss", tree_method="hist"
    )
    svm = SVC(probability=True, kernel="rbf", random_state=42)

    ensemble = VotingClassifier(
        estimators=[("rf", rf), ("xgb", xgb), ("svm", svm)],
        voting="soft",
        n_jobs=-1,
    )

    ensemble.fit(X_train, y_train)

    # Evaluate
    y_pred = ensemble.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy: {acc:.4f} ({acc*100:.1f}%)")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # Save
    MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_OUTPUT_PATH, "wb") as f:
        pickle.dump({
            "model": ensemble,
            "label_encoder": le,
            "feature_names": list(feature_names),
        }, f)

    print(f"\nModel saved to {MODEL_OUTPUT_PATH}")
    return acc


if __name__ == "__main__":
    train()
