# Inventory Forecast & Retrain API — Frontend Docs

Version: 2.0.0  
Base URL (dev): https://full-ai-inventory.onrender.com/ 

Summary
- Purpose: provide demand forecasts and allow dataset uploads to retrain forecasting models (Prophet + LSTM).
- Main flows:
  - Forecasting: POST /forecast → returns forecast, inventory metrics and a saved plot file (forecast_plot.png).
  - Retraining: POST /retrain (multipart CSV) → streams training progress via Server-Sent Events (SSE), returns final status object.
  - Monitor: GET /model/status, GET /dataset/products, GET /plot.

Authentication
- None implemented in server. If you need auth, add a header-based check in the API.

Common responses
- Success objects are JSON. Retrain publishes progress strings (SSE) and final dict: {"status": "success", "message": "...", "meta": {...}}.
- Error format from API endpoints: HTTP error responses 4xx/5xx with a `detail` string.

Endpoints

1) Health
- GET /
- Response: basic status and dataset counts
  Example:
  {
    "status":"running",
    "service":"Inventory Forecast & Retrain API",
    "version":"2.0.0",
    "dataset_rows": 1234,
    "unique_products": 42,
    "endpoints": { ... }
  }

2) Forecast
- POST /forecast
- Content-Type: application/json
- Request body (ForecastRequest):
  - days: integer (default 7)
  - product_id: string (optional)
  - category: string (optional)
  - region: string (optional)
  - min_rating: float (optional)
  - max_price: float (optional)
  - min_discount: float (optional)
- Example request:
  {
    "days": 14,
    "product_id": "P021",
    "region": "us-west"
  }
- Example response (abridged):
  {
    "Reorder Point": 120,
    "Safety Stock": 30,
    "Minimum Level": 30,
    "Maximum Level": 360,
    "Forecast": {
      "2025-10-29": {"forecast": 50.2, "lower_bound": 40.0, "upper_bound": 60.0},
      ...
    },
    "Plot File": "forecast_plot.png",
    "Warnings": [...]
  }
- Notes:
  - The endpoint uses a global retrained model when no filters are provided; otherwise it trains on filtered data before responding.
  - The forecast image is saved as `forecast_plot.png` (use GET /plot to download it).

3) Get plot image
- GET /plot
- Returns: PNG image `forecast_plot.png`.
- 404 if no plot exists.

4) Retrain (upload CSV)
- POST /retrain
- Accepts: multipart/form-data with a single file field named `file`. File must be a `.csv`.
- Behavior:
  - Server saves upload to `uploads/<filename>`.
  - Server starts retraining in background and streams progress via SSE (text/event-stream).
  - Final event contains JSON result dict: {"status":"success" or "error", "message": "...", "meta": {...}}.
- Example curl (SSE):
  curl -N -v -F "file=@/path/to/your.csv" http://localhost:8000/retrain
- Example JS (EventSource-like pattern using fetch streaming):
  ```javascript
  async function uploadCsv(file) {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch('/retrain', { method: 'POST', body: form });
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      // SSE messages are newline separated ("data: ...\n\n")
      const parts = buf.split('\n\n');
      buf = parts.pop(); // incomplete tail
      for (const p of parts) {
        if (!p.trim()) continue;
        const line = p.split('\n').find(l => l.startsWith('data:'));
        if (!line) continue;
        const payload = line.replace(/^data:\s*/, '');
        if (payload.startsWith('[PROGRESS]')) {
          console.log('progress:', payload.replace('[PROGRESS]','').trim());
        } else if (payload.startsWith('[RESULT]')) {
          const result = JSON.parse(payload.replace('[RESULT]','').trim());
          console.log('result:', result);
        }
      }
    }
  }
  ```
- Important:
  - The retrain function requires the uploaded CSV to include required columns (see CSV spec below). If the server responds with:
    data: [RESULT] {"status":"error","message":"Uploaded CSV is missing required columns: {'date','sales'}"}
    → ensure CSV contains the required headers.

5) Model status
- GET /model/status
- Returns metadata and file info:
  {
    "model_metadata": {...} || {"status":"not trained"},
    "files": {
      "lstm": {"exists":true,"path":"lstm_model_retrained.h5","size_kb":123.45,"mtime":...},
      "scaler": {...},
      "prophet": {...},
      "dataset": {...}
    },
    "global_model_loaded": true|false,
    "dataset_rows": int,
    "unique_products": int
  }

6) Dataset products
- GET /dataset/products
- Returns unique product list:
  {
    "total_products": 42,
    "products": ["P001","P002", ...]
  }

CSV format (required)
- Required columns: date, sales
  - `date`: parseable by pandas (ISO8601 recommended, e.g. 2025-10-28 or 2025-10-28T00:00:00)
  - `sales`: numeric (integer or float)
- Optional columns (recommended for better granularity): product_id, category, region, rating, price, discount
- Example CSV:
  date,sales,product_id,category,region,price,discount
  2025-10-01,12,P021,beverages,us-west,9.99,0
  2025-10-02,15,P021,beverages,us-west,9.99,0
- Encoding: utf-8 (BOM handled by server); if issues try saving as UTF-8 without BOM.

Common errors and fixes
- Error: Uploaded CSV is missing required columns: {'date','sales'}
  - Fix: ensure CSV header includes `date` and `sales` exactly (case-sensitive currently). If frontend can pre-process, normalize headers to lowercase `date` and `sales`.
- Error: Parsed 'date' column produced all NaT values
  - Fix: ensure `date` values are in a parseable format.
- Error: Parsed 'sales' column contains no numeric values
  - Fix: ensure `sales` is numeric (no stray currency signs or commas).

Frontend integration tips
- Retrain SSE: Use fetch streaming as shown, or open a long-polling connection. The server sends progress strings and a final JSON dict as SSE `data:` frames prefixed with [PROGRESS] or [RESULT].
- File upload: use <input type="file"> and FormData; submit to POST /retrain with field name `file`.
- Polling: After retrain completes, call GET /model/status to confirm artifact files exist and dataset rows count updated. Use GET /dataset/products to refresh product lists.
- Plot: After /forecast completes, call GET /plot to download the PNG.

Developer notes (backend behaviour)
- Forecasting uses Prophet + optional LSTM. If no filter is provided and a global retrained model exists, the global model is used. If filters provided, a fresh model is trained on the filtered rows for the request.
- Retrain merges uploaded CSV with server dataset (`large_dataset.csv`), deduplicates by (date, product_id) if present, retrains Prophet and (optionally) LSTM (fine-tune), saves model artifacts: prophet_model.pkl, lstm_model_retrained.h5, lstm_scaler.pkl and updates model_meta.json.

Contact / Debugging
- If frontend sees missing-columns error, copy the uploaded CSV header row and paste into a quick debug:
  ```bash
  python - <<PY
  import pandas as pd
  print(pd.read_csv('uploads/your.csv', nrows=0, encoding='utf-8-sig').columns.tolist())
  PY
  ```
- Provide header output to backend dev for a quick mapping fix.

Changelog
- v2.0.0: SSE retrain progress, Prophet + LSTM combined forecasting, auto-reload of saved artifacts.

-- end of document