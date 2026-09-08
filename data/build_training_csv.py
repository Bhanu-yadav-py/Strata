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
    "soil_weathering_index",
    "climate_weathering_index",
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
            row, col = src.index(lon, lat)
            if 0 <= row < src.height and 0 <= col < src.width:
                values = [float(src.read(band + 1)[row, col]) for band in range(min(src.count, len(FEATURE_COLUMNS)))]
                if len(values) == len(FEATURE_COLUMNS) and not any(math.isnan(v) for v in values):
                    return dict(zip(FEATURE_COLUMNS, values))
        return None
    except (ImportError, Exception):
        return None


def _generate_realistic_features(
    lat: float,
    lon: float,
    label: int,
    soil_type: str,
    climate_type: str,
    rng: random.Random,
) -> dict:
    """
    Generate geologically & pedologically realistic features.

    Deposit-positive points:
    - High ferric/ferrous/laterite/gossan indices (oxide-rich capping)
    - Low NDVI (exposed bedrock and lateritic profile)
    - Moderate slope (hillslope supergene enrichment)
    - High soil_weathering_index (lateritoid oxidation)
    - High climate_weathering_index (tropical wet-dry monsoon cycle)

    Incompatible negative points:
    - Characteristics derived directly from their verified soil & climate types
      (e.g., deep alluvium, hydromorphic reducing deltas, arid aeolian sand, basalt vertisols).
    """
    if label == 1:
        # Known deposit belt regional elevation baselines
        if lat > 22.5:  # Rajasthan
            base_elev = 360
        elif lat > 20.0 and lon < 82.0:  # MP/Maharashtra
            base_elev = 420
        elif lat > 20.0:  # Odisha/Jharkhand
            base_elev = 390
        elif lat > 16.0:  # AP
            base_elev = 210
        else:  # Karnataka
            base_elev = 560

        features = {
            "ferric_iron_index": rng.gauss(1.38, 0.16),
            "ferrous_mineral_index": rng.gauss(1.22, 0.14),
            "laterite_index": rng.gauss(1.34, 0.16),
            "gossan_index": rng.gauss(1.42, 0.18),
            "ndvi": rng.gauss(0.14, 0.08),
            "slope": rng.gauss(10.2, 3.5),
            "elevation": rng.gauss(base_elev + 45, 60),
            "soil_weathering_index": rng.gauss(1.36, 0.14),
            "climate_weathering_index": rng.gauss(1.32, 0.12),
        }
    else:
        # Incompatible barren environments modeled on pedological realities
        if soil_type == "aeolian_sand":
            # Arid desert: dry quartz sand, no weathering, no vegetation
            features = {
                "ferric_iron_index": rng.gauss(0.72, 0.08),
                "ferrous_mineral_index": rng.gauss(0.68, 0.08),
                "laterite_index": rng.gauss(0.65, 0.09),
                "gossan_index": rng.gauss(0.70, 0.08),
                "ndvi": rng.gauss(0.08, 0.04),
                "slope": rng.gauss(2.5, 1.2),
                "elevation": rng.gauss(240, 50),
                "soil_weathering_index": rng.gauss(0.32, 0.08),
                "climate_weathering_index": rng.gauss(0.25, 0.06),
            }
        elif soil_type == "hydromorphic_saline_alluvium":
            # Waterlogged coastal delta: reducing environment, flat
            features = {
                "ferric_iron_index": rng.gauss(0.85, 0.10),
                "ferrous_mineral_index": rng.gauss(0.92, 0.10),
                "laterite_index": rng.gauss(0.78, 0.10),
                "gossan_index": rng.gauss(0.80, 0.10),
                "ndvi": rng.gauss(0.52, 0.12),
                "slope": rng.gauss(0.8, 0.5),
                "elevation": rng.gauss(25, 15),
                "soil_weathering_index": rng.gauss(0.40, 0.10),
                "climate_weathering_index": rng.gauss(0.65, 0.10),
            }
        elif soil_type == "quaternary_alluvium":
            # Deep Gangetic alluvial plain: thick fertile silt/clay, flat
            features = {
                "ferric_iron_index": rng.gauss(0.94, 0.10),
                "ferrous_mineral_index": rng.gauss(0.95, 0.10),
                "laterite_index": rng.gauss(0.88, 0.11),
                "gossan_index": rng.gauss(0.92, 0.10),
                "ndvi": rng.gauss(0.55, 0.14),
                "slope": rng.gauss(1.6, 0.9),
                "elevation": rng.gauss(150, 45),
                "soil_weathering_index": rng.gauss(0.52, 0.10),
                "climate_weathering_index": rng.gauss(0.76, 0.10),
            }
        elif soil_type == "vertisol_black_cotton":
            # Deccan basalt flood plain: smectite montmorillonite clay
            features = {
                "ferric_iron_index": rng.gauss(1.04, 0.12),
                "ferrous_mineral_index": rng.gauss(1.08, 0.11),
                "laterite_index": rng.gauss(0.95, 0.12),
                "gossan_index": rng.gauss(0.98, 0.11),
                "ndvi": rng.gauss(0.40, 0.12),
                "slope": rng.gauss(3.5, 1.8),
                "elevation": rng.gauss(520, 75),
                "soil_weathering_index": rng.gauss(0.74, 0.11),
                "climate_weathering_index": rng.gauss(0.78, 0.10),
            }
        else:
            # General platform sandstones or granulite basement
            features = {
                "ferric_iron_index": rng.gauss(1.00, 0.12),
                "ferrous_mineral_index": rng.gauss(0.95, 0.11),
                "laterite_index": rng.gauss(0.94, 0.12),
                "gossan_index": rng.gauss(1.00, 0.12),
                "ndvi": rng.gauss(0.38, 0.14),
                "slope": rng.gauss(4.2, 2.2),
                "elevation": rng.gauss(420, 80),
                "soil_weathering_index": rng.gauss(0.68, 0.12),
                "climate_weathering_index": rng.gauss(0.82, 0.11),
            }

    # Physical constraints
    features["slope"] = max(0.1, features["slope"])
    features["ndvi"] = max(-0.5, min(1.0, features["ndvi"]))
    features["elevation"] = max(5.0, features["elevation"])
    features["soil_weathering_index"] = max(0.1, min(2.0, features["soil_weathering_index"]))
    features["climate_weathering_index"] = max(0.1, min(2.0, features["climate_weathering_index"]))

    return features


def build_training_data():
    """
    Read labeled_deposits.csv and produce training_data.csv with 9 features + label + sample_weight.
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
            soil_type = row.get("soil_type", "quaternary_alluvium" if label == 0 else "lateritic_gravelly_loam")
            climate_type = row.get("climate_type", "subhumid_alluvial" if label == 0 else "tropical_wet_dry_supergene")
            confidence = float(row.get("confidence", 1.0))

            # Try real raster sampling first
            features = _try_rasterio_sampling(lat, lon)
            if features:
                used_rasterio += 1
            else:
                features = _generate_realistic_features(lat, lon, label, soil_type, climate_type, rng)
                used_synthetic += 1

            out_row = {
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "name": row["name"],
                "soil_type": soil_type,
                "climate_type": climate_type,
                "sample_weight": round(confidence, 3),
                "label": label,
            }
            for col in FEATURE_COLUMNS:
                out_row[col] = round(features[col], 6)

            rows.append(out_row)

    # Write output
    fieldnames = ["latitude", "longitude", "name", "soil_type", "climate_type", "sample_weight", "label"] + FEATURE_COLUMNS
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Wrote {len(rows)} training samples to {OUTPUT_CSV}")
    print(f"  -> {used_rasterio} from real GeoTIFF, {used_synthetic} from soil/climate-informed synthetic features")
    if used_rasterio == 0:
        print(f"  [INFO] Using domain-calibrated pedological & climate synthetic distributions.")


if __name__ == "__main__":
    build_training_data()
