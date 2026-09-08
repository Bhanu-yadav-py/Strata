"""
Strata — Training data builder (Step 2)
-----------------------------------------
Reads labeled_deposits.csv (from fetch_mrds_deposits.py) and generates
geologically-realistic satellite-derived features for each point.

When a real GeoTIFF from fetch_prep_satellite_data.py is available, this
script will sample features via rasterio. Until then, it generates
features using geologically-informed distributions that differ between
deposit (label=1) and background (label=0) points — the same approach
as the original make_synthetic_dataset() but anchored on real coordinates.

Usage:
    python build_training_csv.py
"""

import csv
import os
import random
import math

INPUT_CSV = os.path.join(os.path.dirname(__file__), "labeled_deposits.csv")
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "training_data.csv")
GEOTIFF_PATH = os.path.join(os.path.dirname(__file__), "mn_features.tif")

FEATURE_COLUMNS = [
    "ferric_iron_index",
    "ferrous_mineral_index",
    "laterite_index",
    "gossan_index",
    "ndvi",
    "slope",
    "elevation",
]

SEED = 42


def _try_rasterio_sampling(lat: float, lon: float) -> dict | None:
    """
    Attempt to sample real features from a GeoTIFF using rasterio.
    Returns None if the GeoTIFF doesn't exist or rasterio isn't installed.
    """
    if not os.path.exists(GEOTIFF_PATH):
        return None

    try:
        import rasterio
        import numpy as np

        with rasterio.open(GEOTIFF_PATH) as src:
            # GeoTIFF is expected to have 7 bands matching FEATURE_COLUMNS
            row, col = src.index(lon, lat)
            if 0 <= row < src.height and 0 <= col < src.width:
                values = [float(src.read(band + 1)[row, col]) for band in range(min(src.count, 7))]
                if len(values) == 7 and not any(math.isnan(v) for v in values):
                    return dict(zip(FEATURE_COLUMNS, values))
        return None
    except (ImportError, Exception):
        return None


def _generate_realistic_features(
    lat: float, lon: float, label: int, rng: random.Random
) -> dict:
    """
    Generate geologically-realistic features based on the label.

    Deposit-positive points get:
    - Higher ferric/ferrous/laterite/gossan indices (oxide-rich terrain)
    - Lower NDVI (less vegetation → exposed rock/laterite)
    - Moderate slope (hillslope deposits)
    - Elevation varies by region

    Background points get:
    - Lower mineral indices (typical soil/vegetation)
    - Higher NDVI (vegetated)
    - Variable slope and elevation
    """
    # Regional elevation baseline based on coordinates
    if lat > 22.5:  # Rajasthan/Northern
        base_elev = 350
    elif lat > 20.0 and lon < 82.0:  # MP/Maharashtra Deccan
        base_elev = 420
    elif lat > 20.0:  # Odisha/Jharkhand
        base_elev = 380
    elif lat > 16.0:  # AP
        base_elev = 200
    else:  # Karnataka
        base_elev = 550

    if label == 1:
        # Deposit-positive: elevated mineral indices, low vegetation
        features = {
            "ferric_iron_index": rng.gauss(1.38, 0.20),
            "ferrous_mineral_index": rng.gauss(1.22, 0.16),
            "laterite_index": rng.gauss(1.32, 0.18),
            "gossan_index": rng.gauss(1.42, 0.20),
            "ndvi": rng.gauss(0.14, 0.09),
            "slope": rng.gauss(9.5, 3.8),
            "elevation": rng.gauss(base_elev + 40, 70),
        }
    else:
        # Background: typical values, higher vegetation
        features = {
            "ferric_iron_index": rng.gauss(1.02, 0.16),
            "ferrous_mineral_index": rng.gauss(0.96, 0.13),
            "laterite_index": rng.gauss(0.97, 0.16),
            "gossan_index": rng.gauss(1.02, 0.16),
            "ndvi": rng.gauss(0.46, 0.17),
            "slope": rng.gauss(5.5, 4.5),
            "elevation": rng.gauss(base_elev, 110),
        }

    # Physical constraints
    features["slope"] = max(0.0, features["slope"])
    features["ndvi"] = max(-1.0, min(1.0, features["ndvi"]))
    features["elevation"] = max(0.0, features["elevation"])

    return features


def build_training_data():
    """
    Read labeled_deposits.csv and produce training_data.csv with 7 features + label.
    Tries rasterio first, falls back to realistic synthetic features.
    """
    if not os.path.exists(INPUT_CSV):
        print(f"[ERROR] {INPUT_CSV} not found. Run fetch_mrds_deposits.py first.")
        return

    rng = random.Random(SEED)
    used_rasterio = 0
    used_synthetic = 0

    rows = []
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            label = int(row["label"])

            # Try real raster sampling first
            features = _try_rasterio_sampling(lat, lon)
            if features:
                used_rasterio += 1
            else:
                features = _generate_realistic_features(lat, lon, label, rng)
                used_synthetic += 1

            out_row = {
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "name": row["name"],
                "label": label,
            }
            for col in FEATURE_COLUMNS:
                out_row[col] = round(features[col], 6)

            rows.append(out_row)

    # Write output
    fieldnames = ["latitude", "longitude", "name", "label"] + FEATURE_COLUMNS
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Wrote {len(rows)} training samples to {OUTPUT_CSV}")
    print(f"  -> {used_rasterio} from real GeoTIFF, {used_synthetic} from synthetic features")
    if used_rasterio == 0:
        print(f"  [WARN] No GeoTIFF found at {GEOTIFF_PATH} - using synthetic features")
        print(f"    Run fetch_prep_satellite_data.py with GEE to get real features")


if __name__ == "__main__":
    build_training_data()
