# Retrainable Model System - Setup Guide

## Overview
This project now supports **dynamic model retraining** with uploaded CSV files. The system merges new data with existing data, retrains both Prophet and LSTM models, and persists all artifacts for immediate use.

## Features ✨
- ✅ Upload CSV files to retrain the model
- ✅ Automatic data merging and deduplication
- ✅ Prophet + LSTM hybrid forecasting
- ✅ Persistent model storage (Prophet pickle + LSTM H5 weights)
- ✅ Real-time progress streaming during retraining
- ✅ Retrained models immediately available for forecasts
- ✅ Simple HTML test page for quick uploads

## Quick Start

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

Required packages:
- Flask, flask-cors
- pandas, numpy
- prophet
- tensorflow/keras
- scikit-learn
- matplotlib

### 2. Start Flask Server
```powershell
python app.py
```

Server runs at: `http://localhost:8000`

### 3. Test Upload Interface
Open in browser:
```
http://localhost:8000/static/retrain.html
```

## API Endpoints

### POST /retrain
Upload a CSV file to retrain the model with streaming progress.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` field containing CSV file

**Response:**
- Streaming text/event-stream with JSON objects:
  - `{"type": "progress", "data": "message"}` - Progress updates
  - `{"type": "result", "data": {...}}` - Final result with metadata

**Example (curl):**
```powershell
curl -F "file=@new_data.csv" http://localhost:8000/retrain
```

### POST /forecast
Get demand forecast with optional filters.

**Request:**
```json
{
  "days": 7,
  "product_id": "P123",
  "category": "Electronics",
  "region": "North",
  "min_rating": 4.0,
  "max_price": 100.0,
  "min_discount": 10.0
}
```

**Response:**
```json
{
  "Reorder Point": 150,
  "Safety Stock": 50,
  "Minimum Level": 50,
  "Maximum Level": 300,
  "Forecast": {
    "2025-10-29": {"forecast": 25.5, "lower_bound": 20.0, "upper_bound": 31.0}
  },
  "Warnings": ["✅ Inventory levels are healthy."]
}
```

## CSV Requirements

Uploaded CSV files must contain at minimum:
- `date` - Date column (will be parsed to datetime)
- `sales` - Sales/demand values

Optional columns for product-level tracking:
- `product_id` - Product identifier
- `category` - Product category
- `region` - Geographic region
- `rating` - Product rating
- `price` - Product price
- `discount` - Discount percentage

**Example CSV:**
```csv
date,sales,product_id,category,region,rating,price,discount
2025-01-01,100,P123,Electronics,North,4.5,299.99,10
2025-01-02,120,P123,Electronics,North,4.5,299.99,10
```

## Retraining Process

1. **Upload CSV** - File is saved to `uploads/` directory
2. **Validation** - Checks for required columns (`date`, `sales`)
3. **Merging** - Concatenates with existing `large_dataset.csv`
4. **Deduplication** - Removes duplicates by `(date, product_id)` or entire row
5. **Training** - Retrains Prophet (seasonality) + LSTM (sequential patterns)
6. **Persistence** - Saves:
   - `large_dataset.csv` - Updated combined dataset
   - `prophet_model.pkl` - Prophet model (pickled)
   - `lstm_model_retrained.h5` - LSTM weights
   - `lstm_scaler.pkl` - MinMax scaler for LSTM
   - `model_meta.json` - Metadata (training date, row count)
7. **Activation** - Updates global `GLOBAL_MODEL` for immediate use

## Model Artifacts

After retraining, the following files are created/updated:

| File | Description |
|------|-------------|
| `large_dataset.csv` | Combined dataset (old + new) |
| `prophet_model.pkl` | Trained Prophet model |
| `lstm_model_retrained.h5` | LSTM Keras model weights |
| `lstm_scaler.pkl` | MinMax scaler for LSTM |
| `model_meta.json` | Training metadata |
| `forecast_plot.png` | Latest forecast visualization |

## Frontend Integration

### React Component (Already Created)
Located at: `frontend/RetrainModel.jsx`

```jsx
import RetrainModel from './frontend/RetrainModel';

function App() {
  return (
    <div>
      <RetrainModel />
    </div>
  );
}
```

### Static HTML Test Page
Located at: `static/retrain.html`

Simple upload form with real-time progress display.

## Architecture

```
┌─────────────┐
│  Frontend   │
│  (React/    │
│   HTML)     │
└──────┬──────┘
       │ POST /retrain (multipart/form-data)
       │ POST /forecast (application/json)
       v
┌─────────────────────────────────┐
│  Flask Server (app.py)          │
│  - File upload handling         │
│  - Streaming progress response  │
│  - Background thread for train  │
└──────┬──────────────────────────┘
       │ calls
       v
┌─────────────────────────────────┐
│  Model Module (model.py)        │
│  - Data validation & merging    │
│  - Prophet + LSTM training      │
│  - Model persistence (save/load)│
│  - GLOBAL_MODEL cache           │
└─────────────────────────────────┘
```

## Progress Streaming

The `/retrain` endpoint uses Flask's `stream_with_context` to send real-time updates:

1. File upload completes
2. Background thread starts `retrain_model_with_queue()`
3. Progress messages pushed to queue:
   - "Reading uploaded CSV..."
   - "Merging datasets..."
   - "Starting Prophet training..."
   - "Prophet training complete"
   - "Starting LSTM training..."
   - "LSTM epoch 1/50 - loss=0.1234"
   - ...
   - "Saving model artifacts..."
4. Final result sent as JSON object
5. Stream closes

## Performance Notes

- **Prophet training**: 10-60 seconds (depends on data size)
- **LSTM training**: 20-120 seconds (50 epochs, varies with data)
- **Total retraining**: ~1-3 minutes for typical datasets
- **Startup time**: Instant if saved models exist; otherwise trains on startup

## Troubleshooting

### Model Not Loading on Startup
- Check if `large_dataset.csv` exists
- Verify artifact files (`prophet_model.pkl`, `lstm_model_retrained.h5`, `lstm_scaler.pkl`) are present
- Look for errors in console during module import

### Upload Fails with Column Error
- Ensure CSV has `date` and `sales` columns
- Check column names (case-sensitive)

### Retraining Hangs
- Prophet/LSTM training can take time on large datasets
- Check progress streaming in browser/client
- Verify TensorFlow is properly installed

### Forecast Uses Old Model
- Ensure retraining completed successfully
- Check `GLOBAL_MODEL` is updated (visible in logs)
- For filtered forecasts, model trains on-the-fly (expected behavior)

## Development

### Run in Debug Mode
```powershell
$env:FLASK_ENV="development"
python app.py
```

### Check Model Status
```python
import model
print(f"Global model: {model.GLOBAL_MODEL}")
print(f"Dataset rows: {len(model.df)}")
```

### Manual Retrain
```python
from model import retrain_model
result = retrain_model('path/to/new_data.csv')
print(result)
```

## Production Considerations

1. **Async Retraining**: Consider using Celery or RQ for background jobs
2. **Model Versioning**: Save timestamped model artifacts
3. **Validation**: Add stricter CSV validation and data quality checks
4. **Monitoring**: Log retraining events and model performance metrics
5. **Rollback**: Keep previous model versions for rollback capability
6. **Security**: Validate file types, limit upload sizes, sanitize inputs
7. **Scaling**: Use Redis/database for model artifact storage in distributed setups

## License
See main project LICENSE file.
