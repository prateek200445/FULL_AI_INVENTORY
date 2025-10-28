import os
import json
import queue
import threading
import asyncio
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from werkzeug.utils import secure_filename
import pandas as pd
import model

# ==========================================================
# APP INITIALIZATION
# ==========================================================

app = FastAPI(
    title="Inventory Forecast & Retrain API",
    description="Unified API for inventory forecasting and model retraining",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Serve static folder
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# ==========================================================
# MODEL FILE WATCHING
# ==========================================================

MODEL_FILES_WATCH = {
    'lstm': Path("lstm_model_retrained.h5"),
    'scaler': Path("lstm_scaler.pkl"),
    'prophet': Path("prophet_model.pkl"),
    'dataset': Path("large_dataset.csv"),
}
last_modified_times = {}

def get_model_file_mtimes():
    mtimes = {}
    for name, path in MODEL_FILES_WATCH.items():
        mtimes[name] = os.path.getmtime(path) if path.exists() else None
    return mtimes

def reload_global_model_if_needed():
    """Auto reload if model/dataset changed"""
    global last_modified_times
    current_mtimes = get_model_file_mtimes()

    # Detect modification
    changed = any(
        current_mtimes.get(n) != last_modified_times.get(n)
        for n in MODEL_FILES_WATCH
        if current_mtimes.get(n)
    )
    if not changed:
        return False

    try:
        print("🔄 Detected model file changes, reloading...")
        dataset_path = MODEL_FILES_WATCH['dataset']
        if dataset_path.exists():
            try:
                df = pd.read_csv(dataset_path)
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                model.df = df.sort_values('date')
                print(f"📊 Dataset reloaded: {len(model.df)} rows")
            except Exception as e:
                print(f"⚠️ Failed to reload dataset: {e}")

        if all(MODEL_FILES_WATCH[k].exists() for k in ['prophet', 'lstm', 'scaler']):
            new_model = model.InventoryForecastModel()
            new_model.load(
                MODEL_FILES_WATCH['prophet'],
                MODEL_FILES_WATCH['lstm'],
                MODEL_FILES_WATCH['scaler']
            )
            model.GLOBAL_MODEL = new_model
            print("✅ Global model reloaded successfully")

        last_modified_times = current_mtimes
        return True

    except Exception as e:
        print(f"⚠️ Error reloading model: {e}")
        return False

last_modified_times = get_model_file_mtimes()

# ==========================================================
# REQUEST MODELS
# ==========================================================

class ForecastRequest(BaseModel):
    days: int = 7
    product_id: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    min_rating: Optional[float] = None
    max_price: Optional[float] = None
    min_discount: Optional[float] = None

# ==========================================================
# ENDPOINTS
# ==========================================================

@app.get("/", tags=["Health"])
def health_check():
    df = getattr(model, "df", pd.DataFrame())
    return {
        "status": "running",
        "service": "Inventory Forecast & Retrain API",
        "rows": len(df),
        "endpoints": ["/forecast", "/retrain", "/plot", "/model/status"]
    }

@app.post("/forecast", tags=["Forecasting"])
def get_forecast(request: ForecastRequest):
    try:
        reload_global_model_if_needed()
        result = model.forecast(
            days=request.days,
            product_id=request.product_id,
            category=request.category,
            region=request.region,
            min_rating=request.min_rating,
            max_price=request.max_price,
            min_discount=request.min_discount
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plot", tags=["Forecasting"])
def get_plot():
    plot_path = Path("forecast_plot.png")
    if not plot_path.exists():
        raise HTTPException(status_code=404, detail="Plot not found. Run /forecast first.")
    return FileResponse(plot_path, media_type="image/png")

@app.post("/retrain", tags=["Model Management"])
async def retrain_model_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")

    filename = secure_filename(file.filename)
    filepath = UPLOAD_FOLDER / filename
    content = await file.read()
    with open(filepath, 'wb') as f:
        f.write(content)

    # Check CSV validity
    try:
        pd.read_csv(filepath, nrows=5)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}")

    progress_queue = queue.Queue()

    def run_retrain():
        try:
            model.retrain_model_with_queue(
                str(filepath),
                progress_queue,
                epochs=50,
                batch_size=32,
                fine_tune=True
            )
        except Exception as e:
            progress_queue.put(f"ERROR: {e}")

    thread = threading.Thread(target=run_retrain, daemon=True)
    thread.start()

    def stream():
        while True:
            try:
                msg = progress_queue.get(timeout=1)
                yield f"data: {msg}\n\n"
            except queue.Empty:
                if not thread.is_alive():
                    break
        thread.join()

    return StreamingResponse(stream(), media_type="text/event-stream")

@app.get("/model/status", tags=["Model Management"])
def get_model_status():
    df = getattr(model, "df", pd.DataFrame())
    return {
        "loaded": model.GLOBAL_MODEL is not None,
        "dataset_rows": len(df),
        "watched_files": {n: str(p) for n, p in MODEL_FILES_WATCH.items()}
    }

# ==========================================================
# BACKGROUND WATCHER (SAFE)
# ==========================================================

async def periodic_model_watcher(poll_interval: float = 5.0):
    while True:
        try:
            reload_global_model_if_needed()
        except Exception as e:
            print(f"Watcher error: {e}")
        await asyncio.sleep(poll_interval)

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Inventory Forecast & Retrain API")
    asyncio.create_task(periodic_model_watcher())

# ==========================================================
# MAIN ENTRY (Render fix)
# ==========================================================
# 🚀 Render automatically runs uvicorn — do NOT call uvicorn.run() directly.
# ✅ Just ensure it binds correctly with this entrypoint:
# uvicorn new_full_api:app --host 0.0.0.0 --port ${PORT:-8000}

