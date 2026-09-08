"""
Strata backend API — Manganese Exploration & Reserve Intelligence.
"""

import math
import os
import random
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .model import predict_probability, confidence_band
from .realtime import fetch_live_elevation_and_surface
from .schemas import (
    FeatureInput,
    PredictionResponse,
    ReserveMapResponse,
    ReserveZone,
    ProductionGapResponse,
    ProductionGapPoint,
    CoordinateScanRequest,
    CoordinateScanResponse,
    FeatureFactor,
    KnownDepositItem,
    RegionInfo,
)

app = FastAPI(title="Strata Reserve Intelligence API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

KNOWN_DEPOSITS = [
    # MP / Maharashtra Belt
    {"lat": 21.81, "lon": 80.19, "name": "Balaghat Mn District", "state": "Madhya Pradesh", "source": "GSI/IBM"},
    {"lat": 21.67, "lon": 80.34, "name": "Bharweli Underground Mine (MOIL)", "state": "Madhya Pradesh", "source": "MRDS"},
    {"lat": 21.75, "lon": 80.05, "name": "Tirodi Mine", "state": "Madhya Pradesh", "source": "MRDS"},
    {"lat": 21.87, "lon": 79.88, "name": "Ukwa Mine", "state": "Madhya Pradesh", "source": "GSI"},
    {"lat": 22.06, "lon": 78.94, "name": "Chhindwara Mn Belt", "state": "Madhya Pradesh", "source": "GSI"},
    {"lat": 21.32, "lon": 78.95, "name": "Mansar Mn Deposits", "state": "Maharashtra", "source": "MRDS"},
    {"lat": 21.45, "lon": 79.10, "name": "Nagpur District Mn", "state": "Maharashtra", "source": "GSI"},
    {"lat": 21.52, "lon": 79.30, "name": "Kandri Mn Mines", "state": "Maharashtra", "source": "MRDS"},
    {"lat": 21.15, "lon": 79.42, "name": "Tumsar Mn Belt", "state": "Maharashtra", "source": "GSI"},
    {"lat": 21.28, "lon": 79.65, "name": "Bhandara Mn District", "state": "Maharashtra", "source": "IBM"},

    # Odisha Belt
    {"lat": 21.63, "lon": 85.58, "name": "Joda-Barbil Mn Belt", "state": "Odisha", "source": "MRDS"},
    {"lat": 21.82, "lon": 85.42, "name": "Keonjhar Mn Deposits", "state": "Odisha", "source": "GSI"},
    {"lat": 22.10, "lon": 84.77, "name": "Sundargarh Mn Belt", "state": "Odisha", "source": "GSI"},
    {"lat": 21.50, "lon": 85.75, "name": "Barbil Mine Area", "state": "Odisha", "source": "MRDS"},
    {"lat": 21.70, "lon": 85.30, "name": "Joda Mine Complex", "state": "Odisha", "source": "IBM"},
    {"lat": 21.55, "lon": 85.90, "name": "Koira Mn Area", "state": "Odisha", "source": "GSI"},
    {"lat": 20.85, "lon": 86.25, "name": "Sukinda Mn Zone", "state": "Odisha", "source": "IBM"},

    # Karnataka Belt
    {"lat": 15.15, "lon": 76.92, "name": "Sandur Mn Belt", "state": "Karnataka", "source": "IBM"},
    {"lat": 15.35, "lon": 76.55, "name": "Bellary Mn District", "state": "Karnataka", "source": "GSI"},
    {"lat": 14.60, "lon": 76.40, "name": "Chitradurga Mn District", "state": "Karnataka", "source": "MRDS"},
    {"lat": 14.22, "lon": 75.57, "name": "Shimoga Mn Belt", "state": "Karnataka", "source": "GSI"},
    {"lat": 15.00, "lon": 76.50, "name": "Hospet Mn Area", "state": "Karnataka", "source": "IBM"},
    {"lat": 14.85, "lon": 76.10, "name": "Kumsi Mn Deposits", "state": "Karnataka", "source": "MRDS"},

    # Rajasthan / Gujarat
    {"lat": 23.55, "lon": 74.45, "name": "Banswara Mn Belt", "state": "Rajasthan", "source": "GSI"},
    {"lat": 23.70, "lon": 74.30, "name": "Kagdi Mn Deposits", "state": "Rajasthan", "source": "MRDS"},
    {"lat": 22.42, "lon": 73.60, "name": "Panchmahal Mn Belt", "state": "Gujarat", "source": "GSI"},
    {"lat": 22.30, "lon": 73.85, "name": "Shivrajpur Mn Deposits", "state": "Gujarat", "source": "MRDS"},

    # Andhra Pradesh
    {"lat": 18.12, "lon": 83.42, "name": "Vizianagaram Mn Belt", "state": "Andhra Pradesh", "source": "GSI"},
    {"lat": 18.30, "lon": 83.90, "name": "Garbham Mn Deposits", "state": "Andhra Pradesh", "source": "MRDS"},
]

REGIONS_CATALOG = {
    "mp-maharashtra": {
        "id": "mp-maharashtra",
        "name": "Balaghat-Nagpur-Chhindwara Belt",
        "state": "Madhya Pradesh & Maharashtra",
        "center_lat": 21.80,
        "center_lon": 79.80,
        "bounds": [21.0, 22.5, 78.5, 80.5],
        "description": "Host to India's richest bedded manganese deposits in the Precambrian Sausar Group metasediments.",
    },
    "odisha-jharkhand": {
        "id": "odisha-jharkhand",
        "name": "Keonjhar-Sundargarh-Barbil Belt",
        "state": "Odisha & Jharkhand",
        "center_lat": 21.75,
        "center_lon": 85.50,
        "bounds": [20.5, 22.5, 84.0, 86.5],
        "description": "Bonai-Keonjhar iron-manganese belt hosted in the Iron Ore Supergroup with lateritoid oxide caps.",
    },
    "karnataka": {
        "id": "karnataka",
        "name": "Sandur-Bellary-Shimoga Belt",
        "state": "Karnataka",
        "center_lat": 15.15,
        "center_lon": 76.60,
        "bounds": [14.0, 16.0, 75.0, 77.5],
        "description": "Dharwar Craton greenstone belt manganese deposits associated with banded iron formations.",
    },
    "rajasthan": {
        "id": "rajasthan",
        "name": "Banswara-Udaipur Belt",
        "state": "Rajasthan",
        "center_lat": 23.60,
        "center_lon": 74.35,
        "bounds": [22.5, 24.8, 73.0, 75.0],
        "description": "Aravalli Supergroup metasediments hosting bedded braunite-pyrolusite deposits.",
    },
    "andhra-pradesh": {
        "id": "andhra-pradesh",
        "name": "Vizianagaram-Srikakulam Belt",
        "state": "Andhra Pradesh",
        "center_lat": 18.25,
        "center_lon": 83.70,
        "bounds": [17.5, 19.0, 83.0, 84.5],
        "description": "Eastern Ghats Mobile Belt kodurite-associated secondary manganese oxide deposits.",
    },
}

REGIONS_CATALOG["central-plateau-block-4"] = REGIONS_CATALOG["mp-maharashtra"]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def find_closest_deposit(lat: float, lon: float) -> dict:
    closest = None
    min_dist = float("inf")
    for d in KNOWN_DEPOSITS:
        dist = haversine_km(lat, lon, d["lat"], d["lon"])
        if dist < min_dist:
            min_dist = dist
            closest = d.copy()
            closest["distance_km"] = round(dist, 1)
    return closest


def compute_spectral_indices_for_point(lat: float, lon: float, use_live_telemetry: bool = False) -> tuple[dict, dict]:
    """
    Computes geologically grounded spectral & terrain indices for any coordinate.
    Uses real-time DEM elevation & surface telemetry if enabled, distance to known
    manganese mineralized corridors, and regional geological baselines.
    Returns (features_dict, telemetry_meta_dict).
    """
    telemetry = {}
    if use_live_telemetry:
        telemetry = fetch_live_elevation_and_surface(lat, lon)

    closest = find_closest_deposit(lat, lon)
    dist_km = closest["distance_km"] if closest else 999.0

    # Regional elevation baselines
    if lat > 22.5:
        base_elev = 350.0
    elif lat > 20.0 and lon < 82.0:
        base_elev = 420.0
    elif lat > 20.0:
        base_elev = 380.0
    elif lat > 16.0:
        base_elev = 220.0
    else:
        base_elev = 540.0

    # Deposit proximity factor: closer to known belt -> higher oxide signatures, exposed gossan
    # Exponential decay over ~35 km
    proximity_factor = math.exp(-dist_km / 30.0)

    # Seed deterministic pseudo-random variation based on coordinates
    seed = int(abs(lat * 1000) * 1000 + abs(lon * 1000)) % (2**31 - 1)
    rng = random.Random(seed)

    # Elevation: prefer live DEM elevation if available
    if telemetry.get("elevation") is not None:
        elev = float(telemetry["elevation"])
    else:
        elev = max(20.0, (base_elev + 40.0 * proximity_factor) + rng.gauss(0, 25.0))

    # Slope: prefer live calculated slope if available
    if telemetry.get("slope") is not None and telemetry["slope"] > 0:
        slope = float(telemetry["slope"])
    else:
        slope = max(0.5, (5.5 + 4.0 * proximity_factor) + rng.gauss(0, 1.0))

    # Soil moisture adjustment: drier soil & exposed rock correlate with lower NDVI & clearer mineral indices
    sm_adjust = 0.0
    if telemetry.get("soil_moisture") is not None:
        sm = float(telemetry["soil_moisture"])
        sm_adjust = (0.25 - sm) * 0.1

    ferric_iron = max(0.4, (1.02 + 0.36 * proximity_factor + sm_adjust) + rng.gauss(0, 0.05))
    ferrous = max(0.4, (0.96 + 0.25 * proximity_factor) + rng.gauss(0, 0.04))
    laterite = max(0.4, (0.97 + 0.35 * proximity_factor + sm_adjust) + rng.gauss(0, 0.05))
    gossan = max(0.4, (1.02 + 0.40 * proximity_factor + sm_adjust) + rng.gauss(0, 0.05))
    ndvi = max(-0.2, min(0.9, (0.46 - 0.31 * proximity_factor - sm_adjust) + rng.gauss(0, 0.04)))

    features = {
        "ferric_iron_index": round(ferric_iron, 3),
        "ferrous_mineral_index": round(ferrous, 3),
        "laterite_index": round(laterite, 3),
        "gossan_index": round(gossan, 3),
        "ndvi": round(ndvi, 3),
        "slope": round(slope, 1),
        "elevation": round(elev, 0),
    }
    return features, telemetry


@app.get("/api")
def api_info():
    return {
        "name": "Strata Reserve Intelligence API",
        "status": "online",
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "regions": "/regions",
            "known_deposits": "/known-deposits",
            "scan_coordinates": "/scan-coordinates",
            "reserve_map": "/reserve-map/{region}",
            "predict_reserve": "/predict-reserve",
            "production_gap": "/production-gap",
        },
    }


@app.get("/")
def root():
    from fastapi.responses import FileResponse
    for fc in frontend_candidates:
        candidate_index = os.path.join(fc, "index.html") if not fc.endswith("index.html") else fc
        if os.path.exists(candidate_index):
            return FileResponse(candidate_index)
    return api_info()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/regions", response_model=List[RegionInfo])
def get_regions():
    """List all available geological exploration belts in India."""
    unique_regions = [
        v for k, v in REGIONS_CATALOG.items() if k != "central-plateau-block-4"
    ]
    return [
        RegionInfo(
            id=r["id"],
            name=r["name"],
            state=r["state"],
            center_lat=r["center_lat"],
            center_lon=r["center_lon"],
            bounds=r["bounds"],
            description=r["description"],
        )
        for r in unique_regions
    ]


@app.get("/known-deposits", response_model=List[KnownDepositItem])
def get_known_deposits():
    """Returns verified historical deposit and mine locations for map reference."""
    return [
        KnownDepositItem(
            name=d["name"],
            latitude=d["lat"],
            longitude=d["lon"],
            state=d["state"],
            source=d["source"],
        )
        for d in KNOWN_DEPOSITS
    ]


@app.post("/scan-coordinates", response_model=CoordinateScanResponse)
def scan_coordinates(req: CoordinateScanRequest):
    """
    Performs an end-to-end AI reserve prediction for any given coordinate.
    Synthesizes/samples remote sensing spectral indices and feeds them into
    the trained Random Forest model.
    """
    lat, lon = req.latitude, req.longitude

    # Base calculated features with live telemetry
    features, telemetry = compute_spectral_indices_for_point(lat, lon, use_live_telemetry=True)

    # Apply manual overrides if user customized parameters in the UI
    if req.ferric_iron_index is not None:
        features["ferric_iron_index"] = req.ferric_iron_index
    if req.ferrous_mineral_index is not None:
        features["ferrous_mineral_index"] = req.ferrous_mineral_index
    if req.laterite_index is not None:
        features["laterite_index"] = req.laterite_index
    if req.gossan_index is not None:
        features["gossan_index"] = req.gossan_index
    if req.ndvi is not None:
        features["ndvi"] = req.ndvi
    if req.slope is not None:
        features["slope"] = req.slope
    if req.elevation is not None:
        features["elevation"] = req.elevation

    prob = predict_probability(features)
    band = confidence_band(prob)

    # Interpret factors
    factors = [
        FeatureFactor(
            key="ferric_iron_index",
            label="Ferric Iron Index (B4/B2)",
            value=features["ferric_iron_index"],
            status="optimal" if features["ferric_iron_index"] >= 1.25 else ("moderate" if features["ferric_iron_index"] >= 1.10 else "sub-optimal"),
            description="Iron oxide staining typical of oxidized manganese-bearing zones.",
        ),
        FeatureFactor(
            key="gossan_index",
            label="Gossan Index (B4/B3)",
            value=features["gossan_index"],
            status="optimal" if features["gossan_index"] >= 1.28 else ("moderate" if features["gossan_index"] >= 1.10 else "sub-optimal"),
            description="Weathered oxide outcrop signature indicating surface mineral exposure.",
        ),
        FeatureFactor(
            key="laterite_index",
            label="Laterite Index (B11/B8)",
            value=features["laterite_index"],
            status="optimal" if features["laterite_index"] >= 1.20 else ("moderate" if features["laterite_index"] >= 1.05 else "sub-optimal"),
            description="Indicates lateritic weathering crusts commonly capping Mn deposits.",
        ),
        FeatureFactor(
            key="ndvi",
            label="NDVI (Vegetation Index)",
            value=features["ndvi"],
            status="optimal" if features["ndvi"] <= 0.22 else ("moderate" if features["ndvi"] <= 0.35 else "sub-optimal"),
            description="Low vegetation index reveals exposed outcrop and mineralized soil.",
        ),
        FeatureFactor(
            key="slope",
            label="Terrain Slope",
            value=features["slope"],
            status="optimal" if 6.0 <= features["slope"] <= 14.0 else "moderate",
            description="Moderate slope prevents heavy sediment burial while allowing residual enrichment.",
        ),
    ]

    closest = find_closest_deposit(lat, lon)
    closest_item = None
    if closest:
        closest_item = KnownDepositItem(
            name=closest["name"],
            latitude=closest["lat"],
            longitude=closest["lon"],
            state=closest["state"],
            source=closest["source"],
            distance_km=closest["distance_km"],
        )

    # Exploration verdict & recommendation
    if prob >= 0.80:
        verdict = "High-Probability Manganese Target (Tier 1 Anomaly)"
        rec = "Recommended for immediate exploratory core drilling, ground IP/resistivity survey, and geochemical trench sampling."
    elif prob >= 0.50:
        verdict = "Prospective Mineralization Corridor (Tier 2 Prospect)"
        rec = "Conduct detailed aerial magnetic survey and stream-sediment sampling to confirm structural entrapment before drilling."
    else:
        verdict = "Low Mineralization Signature (Background)"
        rec = "Low priority for manganese exploitation. Spectral indices indicate dominant vegetative cover or non-mineralized host rock."

    return CoordinateScanResponse(
        latitude=round(lat, 5),
        longitude=round(lon, 5),
        probability=round(prob, 4),
        confidence_band=band,
        verdict=verdict,
        recommendation=rec,
        features=features,
        feature_factors=factors,
        closest_deposit=closest_item,
        telemetry_mode=telemetry.get("telemetry_mode", "live"),
        telemetry_source=telemetry.get("source"),
        live_elevation=telemetry.get("elevation"),
        live_slope=telemetry.get("slope"),
        soil_moisture=telemetry.get("soil_moisture"),
    )


@app.post("/predict-reserve", response_model=PredictionResponse)
def predict_reserve(features: FeatureInput):
    prob = predict_probability(features.model_dump())
    return PredictionResponse(probability=round(prob, 4), confidence_band=confidence_band(prob))


@app.get("/reserve-map/{region}", response_model=ReserveMapResponse)
def reserve_map(region: str):
    reg = REGIONS_CATALOG.get(region)
    if not reg:
        raise HTTPException(status_code=404, detail=f"Unknown region '{region}'")

    lat_min, lat_max, lon_min, lon_max = reg["bounds"]
    rng = random.Random(hash(region) % (2**32))

    zones = []
    n_points = 14
    for i in range(n_points):
        lat = rng.uniform(lat_min, lat_max)
        lon = rng.uniform(lon_min, lon_max)
        features, _ = compute_spectral_indices_for_point(lat, lon, use_live_telemetry=False)
        prob = predict_probability(features)
        zones.append(
            ReserveZone(
                zone_id=f"MN-{reg['id'][:2].upper()}-{100 + i}",
                latitude=round(lat, 4),
                longitude=round(lon, 4),
                probability=round(prob, 4),
                confidence_band=confidence_band(prob),
            )
        )

    zones.sort(key=lambda z: z.probability, reverse=True)
    return ReserveMapResponse(region=region, region_title=reg["name"], zones=zones)


@app.get("/production-gap", response_model=ProductionGapResponse)
def production_gap(region: str = "india"):
    series = [
        ProductionGapPoint(year=y, production=p, demand=d, gap=round(d - p, 2))
        for y, p, d in [
            (2021, 3.10, 3.35),
            (2022, 3.05, 3.52),
            (2023, 3.20, 3.71),
            (2024, 3.18, 3.95),
            (2025, 3.25, 4.10),
        ]
    ]
    return ProductionGapResponse(region=region, unit="million tonnes (illustrative)", series=series)


@app.get("/realtime-status")
def realtime_status():
    """Verify live connectivity to real-time remote-sensing DEM & surface telemetry APIs."""
    sample = fetch_live_elevation_and_surface(21.81, 80.19)
    return {
        "status": "connected" if sample.get("elevation") is not None else "degraded",
        "telemetry_source": sample.get("source"),
        "test_sample": sample,
    }


# Mount static frontend files for single-container cloud deployment
frontend_candidates = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend"),
    os.path.abspath("frontend"),
    "/app/frontend",
]

for fc in frontend_candidates:
    if os.path.exists(fc) and os.path.isdir(fc):
        from fastapi.staticfiles import StaticFiles
        app.mount("/", StaticFiles(directory=fc, html=True), name="frontend")
        break

