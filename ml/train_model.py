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
    "soil_weathering_index",
    "climate_weathering_index",
]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
RANDOM_SEED = 42


def make_synthetic_dataset(n_samples: int = 4000, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """
    Builds a synthetic feature table incorporating satellite band ratios,
    topography, and domain-grounded soil & climate weathering indices.
    """
    rng = np.random.default_rng(seed)
    n_pos = n_samples // 4
    n_neg = n_samples - n_pos

    positive = pd.DataFrame(
        {
            "ferric_iron_index": rng.normal(1.38, 0.16, n_pos),
            "ferrous_mineral_index": rng.normal(1.22, 0.14, n_pos),
            "laterite_index": rng.normal(1.34, 0.16, n_pos),
            "gossan_index": rng.normal(1.42, 0.18, n_pos),
            "ndvi": rng.normal(0.14, 0.08, n_pos),
            "slope": rng.normal(10.2, 3.5, n_pos),
            "elevation": rng.normal(430, 80, n_pos),
            "soil_weathering_index": rng.normal(1.36, 0.14, n_pos),
            "climate_weathering_index": rng.normal(1.32, 0.12, n_pos),
            "sample_weight": np.ones(n_pos, dtype=float),
        }
    )
    positive["label"] = 1

    negative = pd.DataFrame(
        {
            "ferric_iron_index": rng.normal(0.92, 0.14, n_neg),
            "ferrous_mineral_index": rng.normal(0.90, 0.12, n_neg),
            "laterite_index": rng.normal(0.85, 0.15, n_neg),
            "gossan_index": rng.normal(0.88, 0.14, n_neg),
            "ndvi": rng.normal(0.48, 0.16, n_neg),
            "slope": rng.normal(2.5, 2.0, n_neg),
            "elevation": rng.normal(220, 110, n_neg),
            "soil_weathering_index": rng.normal(0.55, 0.16, n_neg),
            "climate_weathering_index": rng.normal(0.65, 0.18, n_neg),
            "sample_weight": np.ones(n_neg, dtype=float),
        }
    )
    negative["label"] = 0

    df = pd.concat([positive, negative], ignore_index=True)
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    df["slope"] = df["slope"].clip(lower=0.1)
    df["ndvi"] = df["ndvi"].clip(-0.5, 1.0)
    df["soil_weathering_index"] = df["soil_weathering_index"].clip(lower=0.1, upper=2.0)
    df["climate_weathering_index"] = df["climate_weathering_index"].clip(lower=0.1, upper=2.0)
    return df


DATA_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "training_data.csv")


def load_dataset() -> pd.DataFrame:
    if os.path.exists(DATA_CSV):
        df = pd.read_csv(DATA_CSV)
        req_cols = set(FEATURE_COLUMNS + ["label"])
        if req_cols.issubset(df.columns):
            print(f"[INFO] Loaded domain-grounded deposit dataset from {DATA_CSV} ({len(df)} samples)")
            df["slope"] = df["slope"].clip(lower=0.1)
            df["ndvi"] = df["ndvi"].clip(-0.5, 1.0)
            if "sample_weight" not in df.columns:
                df["sample_weight"] = 1.0
            return df
    print("[INFO] Fallback to synthetic dataset generator.")
    return make_synthetic_dataset()


def train():
    df = load_dataset()
    X = df[FEATURE_COLUMNS]
    y = df["label"]
    weights = df["sample_weight"] if "sample_weight" in df.columns else pd.Series(1.0, index=df.index)

    X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
        X, y, weights, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    base_model = RandomForestClassifier(
        n_estimators=350,
        max_depth=7,
        min_samples_leaf=4,
        random_state=RANDOM_SEED,
        class_weight="balanced",
    )
    base_model.fit(X_train, y_train, sample_weight=w_train)

    from sklearn.calibration import CalibratedClassifierCV
    calibrated_model = CalibratedClassifierCV(estimator=base_model, method="sigmoid", cv=5)
    calibrated_model.fit(X_train, y_train, sample_weight=w_train)

    probs = calibrated_model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, probs)
    preds = calibrated_model.predict(X_test)

    print(f"Validation Calibrated ROC-AUC: {auc:.4f}\n")
    print(classification_report(y_test, preds, target_names=["incompatible/barren", "prospective reserve"]))

    importances = pd.Series(base_model.feature_importances_, index=FEATURE_COLUMNS).sort_values(
        ascending=False
    )
    print("Pedological & Geological Feature Importances:\n", importances.to_string())

    joblib.dump({"model": calibrated_model, "features": FEATURE_COLUMNS, "base_model": base_model}, MODEL_PATH)
    print(f"\nSaved calibrated model to {MODEL_PATH}")


if __name__ == "__main__":
    train()
