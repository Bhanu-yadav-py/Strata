from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class FeatureInput(BaseModel):
    ferric_iron_index: float = Field(..., description="B4/B2 band ratio")
    ferrous_mineral_index: float = Field(..., description="B12/B8 band ratio")
    laterite_index: float = Field(..., description="B11/B8 band ratio")
    gossan_index: float = Field(..., description="B4/B3 band ratio")
    ndvi: float = Field(..., description="Normalized difference vegetation index")
    slope: float = Field(..., description="Terrain slope in degrees")
    elevation: float = Field(..., description="Elevation in meters")
    soil_weathering_index: Optional[float] = Field(0.70, description="Pedological lateritization & weathering score")
    climate_weathering_index: Optional[float] = Field(0.75, description="Tropical supergene weathering regime score")


class PredictionResponse(BaseModel):
    probability: float
    confidence_band: str


class ReserveZone(BaseModel):
    zone_id: str
    latitude: float
    longitude: float
    probability: float
    confidence_band: str


class ReserveMapResponse(BaseModel):
    region: str
    region_title: Optional[str] = None
    zones: List[ReserveZone]


class ProductionGapPoint(BaseModel):
    year: int
    production: float
    demand: float
    gap: float


class ProductionGapResponse(BaseModel):
    region: str
    unit: str
    series: List[ProductionGapPoint]


class CoordinateScanRequest(BaseModel):
    latitude: float
    longitude: float
    region_id: Optional[str] = None
    # Optional manual feature overrides
    ferric_iron_index: Optional[float] = None
    ferrous_mineral_index: Optional[float] = None
    laterite_index: Optional[float] = None
    gossan_index: Optional[float] = None
    ndvi: Optional[float] = None
    slope: Optional[float] = None
    elevation: Optional[float] = None
    soil_weathering_index: Optional[float] = None
    climate_weathering_index: Optional[float] = None


class FeatureFactor(BaseModel):
    key: str
    label: str
    value: float
    status: str  # "optimal", "moderate", "sub-optimal"
    description: str


class KnownDepositItem(BaseModel):
    name: str
    latitude: float
    longitude: float
    state: str
    source: str
    distance_km: Optional[float] = None


class CoordinateScanResponse(BaseModel):
    latitude: float
    longitude: float
    probability: float
    confidence_band: str
    verdict: str
    recommendation: str
    features: Dict[str, float]
    feature_factors: List[FeatureFactor]
    closest_deposit: Optional[KnownDepositItem] = None
    telemetry_mode: Optional[str] = "live"
    telemetry_source: Optional[str] = None
    live_elevation: Optional[float] = None
    live_slope: Optional[float] = None
    soil_moisture: Optional[float] = None
    soil_weathering_index: Optional[float] = None
    climate_weathering_index: Optional[float] = None
    soil_profile_desc: Optional[str] = None


class RegionInfo(BaseModel):
    id: str
    name: str
    state: str
    center_lat: float
    center_lon: float
    bounds: List[float]  # [lat_min, lat_max, lon_min, lon_max]
    description: str
