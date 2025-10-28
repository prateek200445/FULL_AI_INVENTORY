import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import Optional
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