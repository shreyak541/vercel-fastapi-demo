from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import os
import io
import requests


app = FastAPI()

# Enable CORS for any origin and allow GET/POST
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# Lazy-load telemetry data so the module import won't fail if file is missing
# Supports local file api/telemetry.csv or remote CSV via TELEMETRY_URL env var
_DATA_PATH = os.path.join(os.path.dirname(__file__), "telemetry.csv")
_data = None
_data_loaded = False

def load_data():
    """Return a pandas.DataFrame or None.

    Priority:
    1. If TELEMETRY_URL env var is set, try download and parse CSV.
    2. Else, if api/telemetry.csv exists, read it.
    3. Otherwise return None.
    """
    global _data, _data_loaded
    if _data_loaded:
        return _data

    telemetry_url = os.environ.get("TELEMETRY_URL")
    if telemetry_url:
        try:
            resp = requests.get(telemetry_url, timeout=10)
            resp.raise_for_status()
            _data = pd.read_csv(io.StringIO(resp.text))
        except Exception:
            _data = None
            _data_loaded = True
            return None
        _data_loaded = True
        return _data

    if os.path.exists(_DATA_PATH):
        try:
            _data = pd.read_csv(_DATA_PATH)
        except Exception:
            _data = None
        _data_loaded = True
        return _data

    _data_loaded = True
    _data = None
    return None


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/favicon.ico")
async def favicon():
    return ""


@app.post("/")
async def get_metrics(request: Request):
    data = load_data()

    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    # If no telemetry available, return empty result (safe for serverless checks)
    if data is None:
        return {}

    result = {}
    for region in regions:
        df_region = data[data["region"] == region]
        if df_region.empty:
            continue

        avg_latency = df_region["latency_ms"].mean()
        p95_latency = np.percentile(df_region["latency_ms"], 95)
        avg_uptime = df_region["uptime"].mean()
        breaches = int((df_region["latency_ms"] > threshold).sum())

        result[region] = {
            "avg_latency": round(float(avg_latency), 2),
            "p95_latency": round(float(p95_latency), 2),
            "avg_uptime": round(float(avg_uptime), 3),
            "breaches": breaches,
        }

    return result
