import os
import joblib
import numpy as np

MODEL_PATH = os.environ.get(
    "STRATA_MODEL_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "ml", "model.pkl"),
)

_bundle = None


def _load():
    global _bundle
    if _bundle is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"No model found at {MODEL_PATH}. Run `python ml/train_model.py` first."
            )
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


import pandas as pd


def predict_probability(features: dict) -> float:
    bundle = _load()
    model, feature_order = bundle["model"], bundle["features"]
    x = pd.DataFrame([[features[f] for f in feature_order]], columns=feature_order)
    return float(model.predict_proba(x)[0, 1])


def confidence_band(probability: float) -> str:
    if probability >= 0.85:
        return "high"
    if probability >= 0.6:
        return "moderate"
    return "emerging"
