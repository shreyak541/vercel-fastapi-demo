from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

app = FastAPI()

# ✅ Enable CORS for any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load the telemetry data
# (place your telemetry CSV in this folder for local testing; 
# on Vercel you might load from remote URL or static folder)
data = pd.read_csv("telemetry.csv")

@app.post("/")
async def get_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    result = {}
    for region in regions:
        df_region = data[data["region"] == region]
        if df_region.empty:
            continue

        avg_latency = df_region["latency_ms"].mean()
        p95_latency = np.percentile(df_region["latency_ms"], 95)
        avg_uptime = df_region["uptime"].mean()
        breaches = (df_region["latency_ms"] > threshold).sum()

        result[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 3),
            "breaches": int(breaches)
        }

    return result
