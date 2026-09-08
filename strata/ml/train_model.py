"""
Strata — Model training (Phase 3)
----------------------------------
Trains the manganese reserve-probability classifier.

IMPORTANT — DATA SOURCE:
This script trains on SYNTHETIC data by default (see `make_synthetic_dataset`),
built to mimic the feature distribution you'd get from
`data/fetch_prep_satellite_data.py` (band-ratio indices + terrain) joined
against labeled deposit / background points. It exists so the full
pipeline (train -> serve -> predict) is real and runnable end-to-end
today, without requiring satellite downloads or GSI/MRDS access first.

TO TRAIN ON REAL DATA:
Replace `make_synthetic_dataset()` with a loader that reads a CSV built by
sampling your exported GeoTIFF (from fetch_prep_satellite_data.py) at:
  - known deposit coordinates (GSI Bhukosh / USGS MRDS)   -> label = 1
  - randomly sampled background coordinates               -> label = 0
Keep the same column names and `train()` runs unchanged.

Usage:
  python train_model.py
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
import joblib
import os

FEATURE_COLUMNS = [
    "ferric_iron_index",
    "ferrous_mineral_index",
    "laterite_index",
    "gossan_index",
    "ndvi",
    "slope",
    "elevation",
]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
RANDOM_SEED = 42


def make_synthetic_dataset(n_samples: int = 4000, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """
    Builds a synthetic feature table with a *realistic* signal baked in:
    deposit-positive points get elevated iron/laterite/gossan indices,
    moderate slope, and lower vegetation (NDVI), matching the geological
    intuition that exposed, weathered, oxide-rich terrain on moderate
    slopes is more likely to host near-surface Mn/Fe deposits.
    """
    rng = np.random.default_rng(seed)
    n_pos = n_samples // 4
    n_neg = n_samples - n_pos

    positive = pd.DataFrame(
        {
            "ferric_iron_index": rng.normal(1.35, 0.18, n_pos),
            "ferrous_mineral_index": rng.normal(1.20, 0.15, n_pos),
            "laterite_index": rng.normal(1.30, 0.20, n_pos),
            "gossan_index": rng.normal(1.40, 0.22, n_pos),
            "ndvi": rng.normal(0.15, 0.10, n_pos),
            "slope": rng.normal(9.0, 4.0, n_pos),
            "elevation": rng.normal(410, 90, n_pos),
        }
    )
    positive["label"] = 1

    negative = pd.DataFrame(
        {
            "ferric_iron_index": rng.normal(1.00, 0.15, n_neg),
            "ferrous_mineral_index": rng.normal(0.95, 0.12, n_neg),
            "laterite_index": rng.normal(0.95, 0.15, n_neg),
            "gossan_index": rng.normal(1.00, 0.15, n_neg),
            "ndvi": rng.normal(0.45, 0.18, n_neg),
            "slope": rng.normal(6.0, 5.0, n_neg),
            "elevation": rng.normal(380, 120, n_neg),
        }
    )
    negative["label"] = 0

    df = pd.concat([positive, negative], ignore_index=True)
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    df["slope"] = df["slope"].clip(lower=0)
    df["ndvi"] = df["ndvi"].clip(-1, 1)
    return df


DATA_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "training_data.csv")


def load_dataset() -> pd.DataFrame:
    if os.path.exists(DATA_CSV):
        df = pd.read_csv(DATA_CSV)
        req_cols = set(FEATURE_COLUMNS + ["label"])
        if req_cols.issubset(df.columns):
            print(f"[INFO] Loaded labeled deposit dataset from {DATA_CSV} ({len(df)} samples)")
            df["slope"] = df["slope"].clip(lower=0)
            df["ndvi"] = df["ndvi"].clip(-1, 1)
            return df
    print("[INFO] Fallback to synthetic dataset generator.")
    return make_synthetic_dataset()


def train():
    df = load_dataset()
    X = df[FEATURE_COLUMNS]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=5,
        random_state=RANDOM_SEED,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    probs = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, probs)
    preds = model.predict(X_test)

    print(f"Validation ROC-AUC: {auc:.4f}\n")
    print(classification_report(y_test, preds, target_names=["no reserve", "reserve"]))

    importances = pd.Series(model.feature_importances_, index=FEATURE_COLUMNS).sort_values(
        ascending=False
    )
    print("Feature importances:\n", importances.to_string())

    joblib.dump({"model": model, "features": FEATURE_COLUMNS}, MODEL_PATH)
    print(f"\nSaved model to {MODEL_PATH}")


if __name__ == "__main__":
    train()
