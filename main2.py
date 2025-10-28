import os
# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from tariff_impact_model import TariffImpactModel

app = FastAPI(title="Tariff Impact Analysis API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the model
model = TariffImpactModel()

class TariffRequest(BaseModel):
    product_id: Optional[str] = None
    tariff_percentage: float
    category: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "product_id": "PROD001",
                "tariff_percentage": 15.0,
                "category": "Electronics"
            }
        }

@app.get("/")
async def root():
    """Root endpoint to check if API is running"""
    return {
        "status": "online",
        "message": "Tariff Impact Analysis API is running",
        "version": "1.0.0"
    }

@app.post("/analyze-tariff")
async def analyze_tariff(request: TariffRequest):
    """
    Analyze tariff impact on products or categories
    
    Examples:
    1. Product-specific analysis:
    {
        "product_id": "PROD001",
        "tariff_percentage": 15.0,
        "category": "Electronics"
    }
    
    2. Category-level analysis:
    {
        "tariff_percentage": 10.0,
        "category": "Electronics"
    }
    """
    try:
        result = model.analyze_tariff_impact(
            product_id=request.product_id,
            tariff_percentage=request.tariff_percentage,
            category=request.category
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Analysis failed",
                "message": str(e),
                "type": type(e).__name__
            }
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Try to access the dataset to verify model is working
        if model.df is not None:
            return {
                "status": "healthy",
                "database": "connected",
                "records": len(model.df)
            }
        return {
            "status": "degraded",
            "message": "Dataset not loaded"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# Error Handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)