"""
Strata — Labeled deposit dataset builder (Step 1)
---------------------------------------------------
Builds a labeled CSV of known manganese deposit locations (positive samples)
and randomly sampled background points (negative samples) for model training.

Deposit coordinates are sourced from published geological survey records
(USGS MRDS, GSI Bhukosh, published literature) for the major Indian
manganese belts: MP/Maharashtra, Odisha, and Karnataka.

Usage:
    python fetch_mrds_deposits.py
"""

import csv
import os
import random

# ---------------------------------------------------------------------------
# Known manganese deposit locations in India
# Sources:
#   - USGS MRDS (Mineral Resources Data System)
#   - GSI (Geological Survey of India) published reports
#   - Indian Bureau of Mines district-level mineral maps
#   - Published literature on Indian manganese deposits
#
# Each entry: (latitude, longitude, name, state, source)
# ---------------------------------------------------------------------------

KNOWN_DEPOSITS = [
    # --- Madhya Pradesh / Maharashtra Belt (Nagpur–Balaghat–Chhindwara) ---
    (21.81, 80.19, "Balaghat Mn District", "Madhya Pradesh", "GSI/IBM"),
    (21.67, 80.34, "Bharweli Mine", "Madhya Pradesh", "MRDS"),
    (21.75, 80.05, "Tirodi Mine", "Madhya Pradesh", "MRDS"),
    (21.87, 79.88, "Ukwa Mine", "Madhya Pradesh", "GSI"),
    (22.06, 78.94, "Chhindwara Mn Belt", "Madhya Pradesh", "GSI"),
    (22.14, 78.62, "Sausar Group Deposits", "Madhya Pradesh", "Literature"),
    (21.95, 79.15, "Ramtek Mn Deposits", "Maharashtra", "MRDS"),
    (21.45, 79.10, "Nagpur District Mn", "Maharashtra", "GSI"),
    (21.32, 78.95, "Mansar Mn Deposits", "Maharashtra", "MRDS"),
    (21.15, 79.42, "Tumsar Mn Belt", "Maharashtra", "GSI"),
    (21.28, 79.65, "Bhandara Mn District", "Maharashtra", "IBM"),
    (21.52, 79.30, "Kandri Mn Mines", "Maharashtra", "MRDS"),
    (21.65, 78.80, "Saoner Mn Belt", "Maharashtra", "GSI"),
    (22.30, 78.50, "Seoni District Mn", "Madhya Pradesh", "GSI"),
    (22.45, 78.10, "Betul Mn Occurrences", "Madhya Pradesh", "Literature"),
    (21.40, 79.55, "Sakoli Belt Deposits", "Maharashtra", "GSI"),
    (21.60, 79.00, "Manegaon Mine", "Maharashtra", "MRDS"),
    (21.72, 80.25, "Waraseoni Mn Area", "Madhya Pradesh", "GSI"),
    (21.90, 79.50, "Katangi Mn Belt", "Madhya Pradesh", "GSI"),
    (22.20, 78.30, "Pandhurna Mn Deposits", "Madhya Pradesh", "Literature"),

    # --- Odisha Belt (Keonjhar–Sundargarh–Jajpur) ---
    (21.63, 85.58, "Joda–Barbil Mn Belt", "Odisha", "MRDS"),
    (21.82, 85.42, "Keonjhar Mn Deposits", "Odisha", "GSI"),
    (22.10, 84.77, "Sundargarh Mn Belt", "Odisha", "GSI"),
    (21.50, 85.75, "Barbil Mine Area", "Odisha", "MRDS"),
    (21.70, 85.30, "Joda Mine Complex", "Odisha", "IBM"),
    (21.55, 85.90, "Koira Mn Area", "Odisha", "GSI"),
    (21.45, 85.50, "Noamundi Mn Zone", "Odisha", "MRDS"),
    (21.38, 85.65, "Gurumahisani Mn", "Odisha", "Literature"),
    (22.25, 84.50, "Bonai Mn Belt", "Odisha", "GSI"),
    (21.90, 85.15, "Champua Mn Deposits", "Odisha", "GSI"),
    (20.95, 86.10, "Jajpur Mn District", "Odisha", "GSI"),
    (20.85, 86.25, "Sukinda Mn Zone", "Odisha", "IBM"),
    (21.30, 85.80, "Gua Mn Deposits", "Odisha", "MRDS"),
    (22.00, 84.95, "Rajgangpur Mn Area", "Odisha", "GSI"),
    (21.75, 85.60, "Bamebari Mine", "Odisha", "IBM"),

    # --- Karnataka Belt (Shimoga–Chitradurga–Bellary) ---
    (14.22, 75.57, "Shimoga Mn Belt", "Karnataka", "GSI"),
    (14.60, 76.40, "Chitradurga Mn District", "Karnataka", "MRDS"),
    (15.15, 76.92, "Sandur Mn Belt", "Karnataka", "IBM"),
    (15.35, 76.55, "Bellary Mn District", "Karnataka", "GSI"),
    (14.85, 76.10, "Kumsi Mn Deposits", "Karnataka", "MRDS"),
    (15.00, 76.50, "Hospet Mn Area", "Karnataka", "IBM"),
    (14.45, 75.80, "Honnali Mn Belt", "Karnataka", "GSI"),
    (14.75, 76.25, "Holalkere Mn Zone", "Karnataka", "Literature"),
    (15.50, 76.80, "Koppal Mn Deposits", "Karnataka", "GSI"),
    (14.95, 76.70, "Kudligi Mn Belt", "Karnataka", "MRDS"),

    # --- Rajasthan (Banswara–Udaipur) ---
    (23.55, 74.45, "Banswara Mn Belt", "Rajasthan", "GSI"),
    (23.70, 74.30, "Kagdi Mn Deposits", "Rajasthan", "MRDS"),
    (24.58, 73.71, "Udaipur Mn Occurrences", "Rajasthan", "Literature"),

    # --- Gujarat (Panchmahal–Vadodara) ---
    (22.42, 73.60, "Panchmahal Mn Belt", "Gujarat", "GSI"),
    (22.30, 73.85, "Shivrajpur Mn Deposits", "Gujarat", "MRDS"),

    # --- Andhra Pradesh (Vizianagaram–Srikakulam) ---
    (18.12, 83.42, "Vizianagaram Mn Belt", "Andhra Pradesh", "GSI"),
    (18.30, 83.90, "Garbham Mn Deposits", "Andhra Pradesh", "MRDS"),
    (18.45, 84.00, "Srikakulam Mn Zone", "Andhra Pradesh", "Literature"),

    # --- Jharkhand ---
    (22.80, 85.95, "Singhbhum Mn Belt", "Jharkhand", "GSI"),
    (22.65, 86.15, "Chaibasa Mn Deposits", "Jharkhand", "MRDS"),

    # --- Goa ---
    (15.40, 74.00, "North Goa Mn Occurrences", "Goa", "Literature"),
]


# ---------------------------------------------------------------------------
# Region bounding boxes for background point generation
# ---------------------------------------------------------------------------
REGION_BOUNDS = {
    "mp-maharashtra": (21.0, 23.0, 77.5, 80.5),
    "odisha": (20.5, 22.5, 84.0, 86.5),
    "karnataka": (14.0, 16.0, 75.0, 77.5),
    "rajasthan": (23.0, 25.0, 73.0, 75.0),
    "andhra": (17.5, 19.0, 83.0, 84.5),
    "jharkhand": (22.0, 23.5, 85.5, 86.5),
}

# Minimum distance (degrees) between a background point and any known deposit
MIN_DEPOSIT_DISTANCE = 0.05  # ~5.5 km


def generate_background_points(n_per_region: int = 60, seed: int = 42) -> list:
    """
    Generate random background (negative-label) points across all regions,
    ensuring none are too close to known deposits.
    """
    rng = random.Random(seed)
    deposit_coords = [(d[0], d[1]) for d in KNOWN_DEPOSITS]
    background = []

    for region_name, (lat_min, lat_max, lon_min, lon_max) in REGION_BOUNDS.items():
        count = 0
        attempts = 0
        while count < n_per_region and attempts < n_per_region * 20:
            lat = rng.uniform(lat_min, lat_max)
            lon = rng.uniform(lon_min, lon_max)
            attempts += 1

            # Check distance to all known deposits
            too_close = any(
                abs(lat - dlat) < MIN_DEPOSIT_DISTANCE and abs(lon - dlon) < MIN_DEPOSIT_DISTANCE
                for dlat, dlon in deposit_coords
            )
            if not too_close:
                background.append((lat, lon, f"BG-{region_name}-{count:03d}", region_name, "random"))
                count += 1

    return background


def build_labeled_dataset(output_path: str = None) -> str:
    """
    Combine known deposits (label=1) with background points (label=0)
    and write to CSV.
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "labeled_deposits.csv")

    positives = [
        {
            "latitude": d[0],
            "longitude": d[1],
            "name": d[2],
            "state_region": d[3],
            "source": d[4],
            "label": 1,
        }
        for d in KNOWN_DEPOSITS
    ]

    background = generate_background_points()
    negatives = [
        {
            "latitude": b[0],
            "longitude": b[1],
            "name": b[2],
            "state_region": b[3],
            "source": b[4],
            "label": 0,
        }
        for b in background
    ]

    all_points = positives + negatives
    rng = random.Random(42)
    rng.shuffle(all_points)

    fieldnames = ["latitude", "longitude", "name", "state_region", "source", "label"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_points)

    n_pos = len(positives)
    n_neg = len(negatives)
    print(f"[OK] Wrote {n_pos + n_neg} labeled points to {output_path}")
    print(f"  - {n_pos} positive (known deposits)")
    print(f"  - {n_neg} negative (background)")
    return output_path


if __name__ == "__main__":
    build_labeled_dataset()
