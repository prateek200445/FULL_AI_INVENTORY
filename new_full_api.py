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

# Initialize FastAPI with metadata
app = FastAPI(
    title="Inventory Forecast & Retrain API",
    description="Unified API for inventory forecasting and model retraining",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Serve static files (index.html test page)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload folder configuration
UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Track model file modification times for auto-reloading
MODEL_FILES_WATCH = {
    'lstm': Path("lstm_model_retrained.h5"),
    'scaler': Path("lstm_scaler.pkl"),
    'prophet': Path("prophet_model.pkl"),
    'dataset': Path("large_dataset.csv"),
}
last_modified_times = {}

def get_model_file_mtimes():
    """Get modification times for all model files."""
    mtimes = {}
    for name, path in MODEL_FILES_WATCH.items():
        if path.exists():
            mtimes[name] = os.path.getmtime(path)
        else:
            mtimes[name] = None
    return mtimes

def reload_global_model_if_needed():
    """Check if model files have been updated and reload GLOBAL_MODEL if necessary."""
    global last_modified_times
    current_mtimes = get_model_file_mtimes()

    # Check if any file has been modified
    files_changed = False
    for name, mtime in current_mtimes.items():
        if mtime is not None:
            if last_modified_times.get(name) != mtime:
                files_changed = True
                break

    if not files_changed:
        return False

    try:
        print("🔄 Detected model file changes, reloading...")

        # If dataset changed, reload it into model.df first
        dataset_path = MODEL_FILES_WATCH['dataset']
        if dataset_path.exists():
            try:
                df = pd.read_csv(dataset_path)
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                model.df = df
                print(f"📊 Dataset reloaded: {len(model.df)} rows, {model.df['product_id'].nunique() if 'product_id' in model.df.columns else 0} unique products")
            except Exception as e:
                print(f"⚠️ Failed to reload dataset: {e}")

        # If model artifacts exist, load them into a new InventoryForecastModel and update GLOBAL_MODEL
        if (MODEL_FILES_WATCH['prophet'].exists() and
            MODEL_FILES_WATCH['lstm'].exists() and
            MODEL_FILES_WATCH['scaler'].exists()):
            try:
                new_model = model.InventoryForecastModel()
                new_model.load(
                    MODEL_FILES_WATCH['prophet'],
                    MODEL_FILES_WATCH['lstm'],
                    MODEL_FILES_WATCH['scaler']
                )
                model.GLOBAL_MODEL = new_model
                print("✅ Global model reloaded successfully")
            except Exception as e:
                print(f"⚠️ Error loading model artifacts: {e}")

        # Update tracking timestamps
        last_modified_times = current_mtimes
        return True
    except Exception as e:
        print(f"⚠️ Error reloading model: {e}")
        return False

# Initialize modification times on startup
last_modified_times = get_model_file_mtimes()

# Pydantic models for request validation
class ForecastRequest(BaseModel):
    days: int = 7
    product_id: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    min_rating: Optional[float] = None
    max_price: Optional[float] = None
    min_discount: Optional[float] = None

# ============================================
# ENDPOINTS
# ============================================

@app.get("/", tags=["Health"])
def health_check():
    """API health check endpoint."""
    dataset_rows = 0
    unique_products = 0
    try:
        df = getattr(model, "df", None)
        if df is not None and not df.empty:
            dataset_rows = len(df)
            unique_products = df['product_id'].nunique() if 'product_id' in df.columns else 0
    except Exception:
        pass

    return {
        "status": "running",
        "service": "Inventory Forecast & Retrain API",
        "version": "2.0.0",
        "dataset_rows": dataset_rows,
        "unique_products": unique_products,
        "endpoints": {
            "forecast": "POST /forecast",
            "retrain": "POST /retrain",
            "plot": "GET /plot",
            "docs": "GET /docs"
        }
    }

@app.post("/forecast", tags=["Forecasting"])
def get_forecast(request: ForecastRequest):
    """
    Generate demand forecast based on historical data.
    """
    try:
        # Auto-reload model if files changed
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
    """
    Retrieve the generated forecast plot image.
    The plot is created during the /forecast call.
    """
    plot_path = Path("forecast_plot.png")
    if not plot_path.exists():
        raise HTTPException(status_code=404, detail="Plot not found. Call /forecast first.")
    return FileResponse(plot_path, media_type="image/png")

@app.post("/retrain", tags=["Model Management"])
async def retrain_model_endpoint(file: UploadFile = File(...)):
    """
    Upload a new CSV file to retrain the forecasting model.
    Streams progress using Server-Sent Events (SSE).
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")

        # Save uploaded file (handle BOM)
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / filename

        content = await file.read()
        with open(filepath, 'wb') as f:
            f.write(content)

        # Basic sanity check: ensure file readable by pandas
        try:
            uploaded_df = pd.read_csv(filepath, encoding='utf-8-sig', nrows=5)
        except Exception:
            # try fallback encodings
            uploaded_df = pd.read_csv(filepath, encoding='latin-1', nrows=5)

        # Create queue for progress streaming
        progress_queue = queue.Queue()

        # Generator for streaming response
        def generate_progress():
            # Start retraining in background thread
            def run_retrain():
                try:
                    # Use model's retrain queue function which should push progress into the queue
                    model.retrain_model_with_queue(
                        str(filepath),
                        progress_queue,
                        epochs=50,
                        batch_size=32,
                        fine_tune=True
                    )
                except Exception as e:
                    # Ensure any exception is reported to client
                    progress_queue.put(f"ERROR: {e}")
                    progress_queue.put({"status": "error", "message": str(e)})

            thread = threading.Thread(target=run_retrain, daemon=True)
            thread.start()

            # Stream progress messages
            while True:
                try:
                    msg = progress_queue.get(timeout=1)
                    if isinstance(msg, dict):
                        # Final result (dict) — send and break
                        yield f"data: [RESULT] {json.dumps(msg)}\n\n"
                        break
                    else:
                        # Regular progress string
                        # Ensure lines are safe strings
                        yield f"data: [PROGRESS] {str(msg)}\n\n"
                except queue.Empty:
                    # If thread finished and queue empty, exit loop
                    if not thread.is_alive():
                        break

            thread.join()

        return StreamingResponse(
            generate_progress(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/status", tags=["Model Management"])
def get_model_status():
    """
    Get current model status and metadata.
    """
    try:
        meta_path = Path("model_meta.json")
        if meta_path.exists():
            with open(meta_path, 'r') as f:
                meta = json.load(f)
        else:
            meta = {"status": "not trained"}

        # Add file info
        files_status = {}
        for name, path in MODEL_FILES_WATCH.items():
            files_status[name] = {
                "exists": path.exists(),
                "path": str(path),
                "size_kb": round(path.stat().st_size / 1024, 2) if path.exists() else 0,
                "mtime": os.path.getmtime(path) if path.exists() else None
            }

        df = getattr(model, "df", pd.DataFrame())
        dataset_rows = len(df) if not df.empty else 0
        unique_products = df['product_id'].nunique() if ('product_id' in df.columns and not df.empty) else 0

        return {
            "model_metadata": meta,
            "files": files_status,
            "global_model_loaded": model.GLOBAL_MODEL is not None,
            "dataset_rows": dataset_rows,
            "unique_products": unique_products
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dataset/products", tags=["Dataset"])
def get_products_list():
    """
    Get list of all unique products in the dataset.
    """
    try:
        df = getattr(model, "df", pd.DataFrame())
        if df.empty or 'product_id' not in df.columns:
            return {"total_products": 0, "products": []}

        products = df['product_id'].unique().tolist()
        return {
            "total_products": len(products),
            "products": sorted(products)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background periodic watcher that reloads model artifacts if changed
async def periodic_model_watcher(poll_interval: float = 2.0):
    while True:
        try:
            reloaded = reload_global_model_if_needed()
            # If reloaded, log (reload_global_model_if_needed already prints)
        except Exception as e:
            print(f"Watcher error: {e}")
        await asyncio.sleep(poll_interval)

@app.on_event("startup")
async def startup_event():
    """Initialize model state on startup and start watcher."""
    print("🚀 Starting Inventory Forecast & Retrain API...")
    # Ensure model.df exists in module
    if not hasattr(model, "df"):
        model.df = pd.DataFrame()
    try:
        if not model.df.empty:
            print(f"📊 Dataset loaded: {len(model.df)} rows")
    except Exception:
        pass

    if model.GLOBAL_MODEL:
        print("✅ Global model loaded from disk")
    else:
        print("⚠️ No pre-trained model found. Will train on first forecast or retrain.")
    print("🔄 Auto-reload enabled for model updates")

    # start background watcher
    asyncio.create_task(periodic_model_watcher())

# Run with: uvicorn new_full_api:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("new_full_api:app", host="0.0.0.0", port=8000, reload=False)