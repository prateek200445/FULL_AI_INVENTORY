import os
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import model

# Initialize FastAPI with metadata
app = FastAPI(
    title="Inventory Forecast API",
    description="API for inventory forecasting and management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track model file modification times for auto-reloading
MODEL_FILES_WATCH = {
    'lstm': Path("lstm_model_retrained.h5"),
    'scaler': Path("lstm_scaler.pkl"),
    'prophet': Path("prophet_model.pkl"),
    'dataset': Path("large_dataset.csv"),  # Also watch the dataset file
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
    
    if files_changed:
        try:
            # Reload the global model from disk
            print("🔄 Detected model file changes, reloading...")
            
            if (MODEL_FILES_WATCH['prophet'].exists() and 
                MODEL_FILES_WATCH['lstm'].exists() and 
                MODEL_FILES_WATCH['scaler'].exists()):
                
                # CRITICAL: Reload the dataset first (it might have been updated during retraining)
                dataset_path = Path("large_dataset.csv")
                if dataset_path.exists():
                    print("📊 Reloading updated dataset...")
                    model.df = pd.read_csv(dataset_path)
                    if 'date' in model.df.columns:
                        model.df['date'] = pd.to_datetime(model.df['date'])
                    model.df = model.df.sort_values('date')
                    print(f"✅ Dataset reloaded: {len(model.df)} rows, {model.df['product_id'].nunique()} unique products")
                
                # Create new model instance and load from disk
                new_model = model.InventoryForecastModel()
                new_model.load(
                    MODEL_FILES_WATCH['prophet'],
                    MODEL_FILES_WATCH['lstm'],
                    MODEL_FILES_WATCH['scaler']
                )
                
                # Update global model
                model.GLOBAL_MODEL = new_model
                last_modified_times = current_mtimes
                print("✅ Model reloaded successfully!")
                return True
        except Exception as e:
            print(f"⚠️ Failed to reload model: {e}")
    
    return False

# Background task to watch model files
async def model_file_watcher():
    """Background task that periodically checks for model file updates."""
    global last_modified_times
    last_modified_times = get_model_file_mtimes()
    
    while True:
        await asyncio.sleep(2)  # Check every 2 seconds
        reload_global_model_if_needed()

@app.on_event("startup")
async def startup_event():
    """Start the model file watcher on app startup."""
    asyncio.create_task(model_file_watcher())
    print("🚀 Model file watcher started")

# Custom OpenAPI schema configuration
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Inventory Forecast API",
        version="1.0.0",
        description="API for inventory forecasting and management",
        routes=app.routes,
    )
    
    # Add custom configurations
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

class ForecastRequest(BaseModel):
    days: int = 7
    product_id: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    min_rating: Optional[float] = None
    max_price: Optional[float] = None
    min_discount: Optional[float] = None

@app.get("/")
async def root():
    return {"status": "Inventory Forecast API is running"}

@app.post("/forecast")
async def get_forecast(request: ForecastRequest):
    # Check if model files have been updated before forecasting
    reload_global_model_if_needed()
    
    try:
        result = model.forecast(
            days=request.days,
            product_id=request.product_id,
            category=request.category,
            region=request.region,
            min_rating=request.min_rating,
            max_price=request.max_price,
            min_discount=request.min_discount
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plot")
async def get_plot():
    try:
        return FileResponse("forecast_plot.png")
    except Exception as e:
        raise HTTPException(status_code=404, detail="Plot not found")