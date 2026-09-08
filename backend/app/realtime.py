"""
Strata — Real-Time Remote Sensing & DEM Telemetry Service.
Provides live digital elevation model (DEM) and surface telemetry for any coordinates on Earth.
Includes sub-second network queries, spatial caching, and geological baseline fallbacks.
"""

import json
import math
import urllib.request
import urllib.error
import time
from typing import Dict, Any, Optional

# In-memory spatial cache: key -> (timestamp, data)
_TELEMETRY_CACHE: Dict[str, Any] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour cache


def _cache_key(lat: float, lon: float) -> str:
    # Round to ~100m grid for caching
    return f"{round(lat, 3)}:{round(lon, 3)}"


def fetch_live_elevation_and_surface(lat: float, lon: float, timeout: float = 1.2) -> Dict[str, Any]:
    """
    Fetches real-time elevation and surface parameters from Open-Meteo Global DEM / Copernicus / SRTM.
    Returns dictionary with live measurements and telemetry metadata.
    """
    key = _cache_key(lat, lon)
    now = time.time()

    if key in _TELEMETRY_CACHE:
        cached_time, data = _TELEMETRY_CACHE[key]
        if now - cached_time < CACHE_TTL_SECONDS:
            res = dict(data)
            res["telemetry_mode"] = "live (cached)"
            return res

    elevation: Optional[float] = None
    slope: Optional[float] = None
    soil_moisture: Optional[float] = None
    surface_temp: Optional[float] = None
    direct_radiation: Optional[float] = None

    try:
        # 1. Fetch Elevation from Open-Meteo Elevation API
        # Sample center and a slight offset to estimate real-time slope gradient
        lat_offset = lat + 0.001  # ~110m north
        lon_offset = lon + 0.001  # ~100m east
        elev_url = (
            f"https://api.open-meteo.com/v1/elevation?"
            f"latitude={lat:.5f},{lat_offset:.5f},{lat:.5f}&"
            f"longitude={lon:.5f},{lon:.5f},{lon_offset:.5f}"
        )
        req = urllib.request.Request(elev_url, headers={"User-Agent": "Strata-Telemetry/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                elev_data = json.loads(response.read().decode("utf-8"))
                elevs = elev_data.get("elevation", [])
                if len(elevs) >= 1 and elevs[0] is not None:
                    elevation = round(float(elevs[0]), 1)
                    if len(elevs) >= 3 and elevs[1] is not None and elevs[2] is not None:
                        # Estimate slope gradient in degrees: atan(rise / run)
                        dh_lat = abs(elevs[1] - elevs[0])
                        dh_lon = abs(elevs[2] - elevs[0])
                        run_m = 110.0
                        grad = math.sqrt(dh_lat**2 + dh_lon**2) / run_m
                        slope = round(math.degrees(math.atan(grad)), 1)
    except Exception:
        pass

    try:
        # 2. Fetch Surface & Soil Telemetry from Open-Meteo Forecast/Telemetry API
        surf_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat:.4f}&longitude={lon:.4f}&"
            f"current=soil_temperature_0cm,soil_moisture_0_to_1cm,direct_radiation&timezone=auto"
        )
        req = urllib.request.Request(surf_url, headers={"User-Agent": "Strata-Telemetry/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                surf_data = json.loads(response.read().decode("utf-8"))
                current = surf_data.get("current", {})
                soil_moisture = current.get("soil_moisture_0_to_1cm")
                surface_temp = current.get("soil_temperature_0cm")
                direct_radiation = current.get("direct_radiation")
    except Exception:
        pass

    is_live = elevation is not None

    # Compute live pedological & climate weathering indices
    eff_slope = slope if (slope is not None and slope > 0) else 6.0
    eff_moisture = soil_moisture if (soil_moisture is not None and soil_moisture >= 0) else 0.20

    # 1. Soil Weathering Index:
    # Lateritization requires oxidising, well-drained profiles (moisture 0.12 - 0.26) on moderate hillslopes.
    # Waterlogged soils (>0.40) reduce Mn into soluble Mn2+; flat alluvium (<2° slope) lacks residual oxidation caps.
    drainage_bonus = max(0.0, min(0.35, (eff_slope - 2.0) * 0.04))
    if eff_moisture > 0.38:
        # Waterlogged reducing soil penalty
        moisture_factor = max(0.2, 1.0 - (eff_moisture - 0.38) * 3.0)
    elif eff_moisture < 0.06:
        # Hyper-arid non-weathered sand penalty
        moisture_factor = 0.35
    else:
        # Optimal leaching & oxidation zone
        moisture_factor = 1.05

    base_soil_weathering = 0.90 * moisture_factor + drainage_bonus
    soil_weathering = round(max(0.25, min(1.85, base_soil_weathering)), 3)

    # 2. Climate Weathering Index:
    # Secondary supergene concentration occurs in tropical wet-dry monsoon climates (14°N - 23.5°N).
    # Arid desert margins (<73°E, >25°N) or hyper-cold zones have low chemical weathering rates.
    is_arid_zone = (lon < 73.5 and lat > 24.5)
    is_delta_waterlogged = (lon > 85.0 and lat < 20.8 and (elevation or 50) < 30)
    is_gangetic_alluvium = (lat > 25.2 and lon > 78.0 and lon < 85.0)

    if is_arid_zone:
        base_climate = 0.28
        soil_profile_desc = "Arid Aeolian Sand (Zero Chemical Weathering / Barren)"
    elif is_delta_waterlogged:
        base_climate = 0.60
        soil_profile_desc = "Hydromorphic Deltaic Alluvium (Reducing Aquatic Regime / Barren)"
    elif is_gangetic_alluvium:
        base_climate = 0.72
        soil_profile_desc = "Quaternary Floodplain Alluvium (Deep Silt/Clay Cover / Barren)"
    elif (14.0 <= lat <= 23.8) and (73.5 <= lon <= 86.5):
        # Indian Peninsular Tropical Supergene Belt
        base_climate = 1.28
        soil_profile_desc = "Lateritic Ferruginous Loam (Supergene Oxide Enrichment Cap)"
    else:
        base_climate = 0.85
        soil_profile_desc = "Regional Undifferentiated Sedimentary/Crystalline Soil"

    climate_weathering = round(max(0.20, min(1.80, base_climate)), 3)

    result = {
        "elevation": elevation,
        "slope": slope,
        "soil_moisture": soil_moisture,
        "surface_temp": surface_temp,
        "direct_radiation": direct_radiation,
        "soil_weathering_index": soil_weathering,
        "climate_weathering_index": climate_weathering,
        "soil_profile_desc": soil_profile_desc,
        "telemetry_mode": "live" if is_live else "regional baseline (offline fallback)",
        "source": "Open-Meteo Global SRTM/Copernicus DEM & Surface Telemetry" if is_live else "Regional Geological Baseline",
    }

    if is_live:
        _TELEMETRY_CACHE[key] = (now, result)

    return result
