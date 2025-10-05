# vercel-fastapi-demo

This repo contains a small FastAPI app designed to run as a serverless function on Vercel.

Features:
- POST / accepts JSON {"regions": [...], "threshold_ms": 180} and returns per-region metrics computed from a telemetry CSV
- CORS enabled for POST requests from any origin
- Supports telemetry from either a local file `api/telemetry.csv` or a remote CSV URL via the `TELEMETRY_URL` environment variable
- Gracefully returns an empty JSON object if telemetry is not available (safe for serverless deployment)

Deployment
----------
1. Ensure `api/index.py`, `vercel.json`, and `requirements.txt` are in the repository root.
2. If you want the service to compute metrics, either add `api/telemetry.csv` to the repo or set `TELEMETRY_URL` to the CSV URL:

   - To set TELEMETRY_URL on Vercel CLI:
     ```powershell
     npx vercel env add TELEMETRY_URL production
     ```

3. Deploy with:
   ```powershell
   npx vercel
   # or for production
   npx vercel --prod
   ```

Testing locally
---------------
Install dependencies and run locally with uvicorn:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn api.index:app --host 127.0.0.1 --port 8000
```

Sample POST request (PowerShell):

```powershell
$body = @{ regions = @("apac","emea"); threshold_ms = 156 } | ConvertTo-Json
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/' -Method Post -Body $body -ContentType 'application/json'
```

If `telemetry.csv` or `TELEMETRY_URL` is not present, the POST endpoint returns `{}`.
