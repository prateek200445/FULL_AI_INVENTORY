# 🚀 QUICK START - Retrainable Model System

## In 60 Seconds

### 1️⃣ Install & Run
```powershell
pip install -r requirements.txt
python app.py
```

### 2️⃣ Test Upload
Open: http://localhost:8000/static/retrain.html
Upload: test_upload.csv
Watch: Real-time progress

### 3️⃣ Get Forecast
```powershell
curl -H "Content-Type: application/json" -d "{\"days\":7}" http://localhost:8000/forecast
```

---

## 📌 Quick Reference

### API Endpoints
```
POST /retrain        - Upload CSV, retrain model (streaming progress)
POST /forecast       - Get demand forecast with filters
GET  /               - Health check
GET  /static/*       - Static files (HTML test page)
```

### Required CSV Columns
```
date      - Date (YYYY-MM-DD format)
sales     - Sales/demand values
```

### Optional CSV Columns
```
product_id, category, region, rating, price, discount
```

### Model Artifacts
```
large_dataset.csv           - Combined dataset
prophet_model.pkl          - Prophet model
lstm_model_retrained.h5    - LSTM weights
lstm_scaler.pkl           - LSTM scaler
model_meta.json           - Metadata
```

---

## 🎯 Example Usage

### Upload & Retrain (curl)
```powershell
curl -F "file=@test_upload.csv" http://localhost:8000/retrain
```

### Forecast (No Filters)
```powershell
curl -X POST http://localhost:8000/forecast -H "Content-Type: application/json" -d '{"days":7}'
```

### Forecast (With Filters)
```powershell
curl -X POST http://localhost:8000/forecast -H "Content-Type: application/json" -d '{
  "days": 7,
  "product_id": "P001",
  "category": "Electronics",
  "min_rating": 4.0
}'
```

---

## 🧪 Test It

### Automated Test
```powershell
python test_integration.py
```

### Manual Test
1. Start server: `python app.py`
2. Open browser: http://localhost:8000/static/retrain.html
3. Upload: test_upload.csv
4. Watch progress stream

---

## 📁 Key Files

```
app.py                          Flask server
model.py                        ML models & retraining
frontend/RetrainModel.jsx       React component
static/retrain.html            HTML test page
test_upload.csv                Sample data
test_integration.py            Test script
README_RETRAIN.md              Full docs
IMPLEMENTATION_SUMMARY.md      Complete overview
```

---

## ⚡ Performance

- Upload: < 1s
- Prophet training: 10-30s
- LSTM training: 30-90s
- Total retraining: ~1-2 min

---

## 🎉 Features

✅ CSV upload with validation
✅ Data merge & deduplication
✅ Prophet + LSTM hybrid forecasting
✅ Real-time progress streaming
✅ Model persistence (save/load)
✅ Immediate model availability
✅ React + HTML interfaces
✅ Comprehensive documentation

---

## 🆘 Troubleshooting

**Server won't start?**
→ Check dependencies: `pip install -r requirements.txt`

**Upload fails?**
→ Ensure CSV has `date` and `sales` columns

**Slow retraining?**
→ Normal for large datasets (Prophet + 50 LSTM epochs)

**Old model still used?**
→ Check for errors in retraining stream

---

## 📚 Full Documentation

See `README_RETRAIN.md` for:
- Detailed API documentation
- Architecture diagrams
- CSV format specifications
- Troubleshooting guide
- Production deployment tips

---

**Need help?** Check the full docs or run the integration test!
