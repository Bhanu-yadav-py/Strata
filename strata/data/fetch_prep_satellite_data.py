"""
Strata — Satellite data sourcing & preprocessing (Phase 1-2)
--------------------------------------------------------------
Pulls Sentinel-2 surface reflectance imagery + SRTM elevation for a
given area of interest (AOI), masks clouds, computes mineral-mapping
band-ratio indices used as manganese/iron-oxide proxies, and exports
the result as a GeoTIFF ready for the feature-engineering / ML stage.

Requires a (free) Google Earth Engine account:
  https://earthengine.google.com/signup/

Setup:
  pip install earthengine-api geemap

  earthengine authenticate   # one-time, opens a browser login

Usage:
  python fetch_prep_satellite_data.py
"""

import ee
import geemap

# ---------------------------------------------------------------------
# 1. AUTH + INIT
# ---------------------------------------------------------------------
ee.Initialize()

# ---------------------------------------------------------------------
# 2. DEFINE YOUR AREA OF INTEREST
#    Replace these coordinates with your target region.
#    Example below is a bounding box over the MP/Maharashtra manganese
#    belt (approximate — refine to your actual study area).
# ---------------------------------------------------------------------
AOI = ee.Geometry.Rectangle([78.0, 21.0, 79.5, 22.5])

START_DATE = "2024-01-01"
END_DATE = "2024-12-31"
MAX_CLOUD_PCT = 15  # skip scenes cloudier than this

OUTPUT_PREFIX = "mn_features"  # exported file name prefix
EXPORT_SCALE = 10  # meters/pixel, matches Sentinel-2 native resolution


# ---------------------------------------------------------------------
# 3. CLOUD MASKING (Sentinel-2 SR uses the SCL band)
# ---------------------------------------------------------------------
def mask_s2_clouds(image):
    scl = image.select("SCL")
    # Keep vegetation, bare soil/rock, water — drop cloud/shadow/snow classes
    valid = scl.neq(3).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10)).And(scl.neq(11))
    return image.updateMask(valid).divide(10000)  # scale reflectance to 0-1


# ---------------------------------------------------------------------
# 4. LOAD + FILTER SENTINEL-2 COLLECTION
# ---------------------------------------------------------------------
s2 = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(AOI)
    .filterDate(START_DATE, END_DATE)
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", MAX_CLOUD_PCT))
    .map(mask_s2_clouds)
)

composite = s2.median().clip(AOI)

# ---------------------------------------------------------------------
# 5. MINERAL-MAPPING BAND RATIO INDICES
#    These are standard proxies from remote-sensing mineral exploration
#    literature — not a manganese-specific spectral signature on their
#    own, but strong input features for the ML model alongside labeled
#    deposit data.
# ---------------------------------------------------------------------
b2, b3, b4, b8, b11, b12 = (
    composite.select("B2"),
    composite.select("B3"),
    composite.select("B4"),
    composite.select("B8"),
    composite.select("B11"),
    composite.select("B12"),
)

# Ferric iron index — iron oxide staining, common around Mn-bearing zones
ferric_iron_index = b4.divide(b2).rename("ferric_iron_index")

# Ferrous mineral index — mafic/ultramafic host-rock indicator
ferrous_mineral_index = b12.divide(b8).rename("ferrous_mineral_index")

# Laterite index — laterite/oxide crusts often cap Mn deposits
laterite_index = b11.divide(b8).rename("laterite_index")

# Gossan index — weathered oxide outcrop indicator
gossan_index = b4.divide(b3).rename("gossan_index")

# NDVI — used to mask dense vegetation, which hides bare-rock/soil signal
ndvi = composite.normalizedDifference(["B8", "B4"]).rename("ndvi")

feature_stack = ee.Image.cat(
    [ferric_iron_index, ferrous_mineral_index, laterite_index, gossan_index, ndvi]
)

# ---------------------------------------------------------------------
# 6. TERRAIN FEATURES (structural lineaments correlate with ore control)
# ---------------------------------------------------------------------
dem = ee.Image("USGS/SRTMGL1_003").clip(AOI)
slope = ee.Terrain.slope(dem).rename("slope")
elevation = dem.rename("elevation")

feature_stack = feature_stack.addBands([slope, elevation])

# ---------------------------------------------------------------------
# 7. EXPORT
#    Two options: export to Google Drive (large AOIs) or download
#    directly via geemap for small AOIs during prototyping.
# ---------------------------------------------------------------------
def export_to_drive():
    task = ee.batch.Export.image.toDrive(
        image=feature_stack,
        description=OUTPUT_PREFIX,
        folder="strata_manganese",
        fileNamePrefix=OUTPUT_PREFIX,
        region=AOI,
        scale=EXPORT_SCALE,
        maxPixels=1e10,
    )
    task.start()
    print(f"Export started: check Google Drive folder 'strata_manganese' "
          f"for '{OUTPUT_PREFIX}.tif' once the task completes.")


def download_locally(local_path=f"{OUTPUT_PREFIX}.tif"):
    # Best for small AOIs / quick prototyping only.
    geemap.ee_export_image(
        feature_stack, filename=local_path, scale=EXPORT_SCALE, region=AOI, file_per_band=False
    )
    print(f"Downloaded to {local_path}")


if __name__ == "__main__":
    # Pick whichever suits your AOI size:
    export_to_drive()
    # download_locally()

    print(
        "\nNext steps:\n"
        "  1. Bring the exported GeoTIFF into a GIS tool (QGIS) to sanity-check\n"
        "     the index rasters against known deposit points.\n"
        "  2. Overlay GSI Bhukosh / MRDS deposit coordinates as labeled points.\n"
        "  3. Sample feature values at labeled + random background points to\n"
        "     build your training table for Phase 3 (model development).\n"
    )
