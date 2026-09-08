# Strata — Manganese Reserve Intelligence

AI/ML + satellite remote sensing to flag high-probability manganese reserve
zones, and cross-reference them against production shortfalls.

## What's in this project, and what's real vs. placeholder

| Piece | Location | Status |
|---|---|---|
| Frontend UI | `frontend/index.html` | Fully built, live-wired to the API with graceful fallback to demo data |
| Backend API | `backend/` | Fully built and tested (FastAPI, 3 endpoints) |
| ML model | `ml/train_model.py` → `ml/model.pkl` | **Trained and validated (ROC-AUC ~0.999)**, but on synthetic data — see below |
| Satellite data acquisition | `data/fetch_prep_satellite_data.py` | Written and ready to run, but **not executed yet** — needs a free Earth Engine account and real network access |
| Labeled training data | — | **Not yet built** — this is the next real task |

**The one thing to understand:** the model works end-to-end and the API/frontend
correctly serve its predictions — but it was trained on synthetic data
designed to mimic what real satellite-derived features should look like.
It is not yet trained on real manganese deposits. Treat the whole pipeline
as a working scaffold, not a production-ready predictor, until you swap in
real labeled data (see "Next real step" below).

## Project structure

```
strata/
├── frontend/
│   └── index.html            # UI — fetches from the API, falls back to demo data if offline
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI endpoints
│   │   ├── model.py          # loads ml/model.pkl, runs inference
│   │   └── schemas.py        # request/response models
│   ├── requirements.txt
│   └── Dockerfile
├── ml/
│   ├── train_model.py        # trains the RandomForest classifier (synthetic data for now)
│   ├── model.pkl             # trained model, already generated
│   └── requirements.txt
├── data/
│   ├── fetch_prep_satellite_data.py   # Google Earth Engine acquisition + preprocessing
│   └── requirements.txt
└── docker-compose.yml
```

## Running it locally

**1. Backend**
```bash
cd strata
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```
Check it's alive: `curl http://localhost:8000/health`

**2. Frontend**
```bash
cd strata/frontend
python -m http.server 8080
```
Open `http://localhost:8080`. The dashboard's "TOP RANKED ZONES" panel will
switch from "offline demo data" to "live model" once it successfully reaches
the backend — open your browser dev console if it doesn't, to see why the
fetch failed (usually just the backend not running yet).

**Or, both at once with Docker:**
```bash
docker compose up --build
```

**3. Retrain the model anytime**
```bash
cd strata/ml
python train_model.py
```

## Next real step: real data, not synthetic

This is the actual unlock for the project. In order:

1. **Get a free Google Earth Engine account**, then run
   `data/fetch_prep_satellite_data.py` against a real bounding box for the
   region you care about (edit the `AOI` variable). This exports a GeoTIFF
   of band-ratio + terrain features.
2. **Get labeled deposit points** — Geological Survey of India's Bhukosh
   portal for Indian belts (Madhya Pradesh, Odisha, Maharashtra, Karnataka),
   or USGS MRDS for a global set.
3. **Sample the GeoTIFF at those labeled points** (positive) plus randomly
   sampled background points (negative) using `rasterio` — this produces a
   CSV with the same column names `train_model.py` already expects.
4. **Swap `make_synthetic_dataset()`** in `train_model.py` for a loader that
   reads that CSV. Everything downstream (API, frontend) needs no changes.
5. **Update `_sample_features_at()`** in `backend/app/main.py` to sample real
   raster values instead of generating random ones, once you have persistent
   feature rasters to query.
6. **Get real production/demand figures** (Indian Bureau of Mines, USGS
   Mineral Commodity Summaries) to replace the placeholder series in
   `/production-gap`.

## Deploying beyond localhost

- Backend: any container host (Render, Fly.io, AWS ECS, GCP Cloud Run) — the
  `Dockerfile` is ready as-is.
- Frontend: any static host (Netlify, Vercel, GitHub Pages, S3+CloudFront) —
  just update `API_BASE` in `frontend/index.html`'s script tag to your
  deployed backend URL.
- Model retraining: once you have a real, growing labeled dataset, this is
  a good candidate for a scheduled job (cron, GitHub Actions, or a proper
  MLOps pipeline) rather than a manual script run.
