# 🤖 AI Inventory Management System

Complete AI-powered inventory forecasting and tariff impact analysis platform with React frontend.

## 🌟 System Overview

This system consists of **3 microservices**:

1. **Forecast & Retrain API** (Port 8002) - Prophet + LSTM forecasting with model retraining
2. **Tariff Analyzer API** (Port 8003) - ML-based tariff impact analysis
3. **React Frontend** (Port 5173) - Modern UI for all AI features

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 5173)               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Forecast   │  │   Retrain   │  │  Tariff Analyzer    │ │
│  │  Dashboard  │  │  Dashboard  │  │    Dashboard        │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────────────┘ │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
          │ HTTP/SSE        │ HTTP/SSE        │ HTTP
          │                 │                 │
┌─────────▼─────────────────▼────────┐ ┌──────▼────────────────┐
│  Forecast & Retrain API            │ │  Tariff Analyzer API  │
│  (Port 8002)                       │ │  (Port 8003)          │
│  ┌──────────────────────────────┐  │ │  ┌─────────────────┐  │
│  │ Prophet + LSTM Models        │  │ │  │ ML Impact Model │  │
│  │ - /forecast                  │  │ │  │ - /analyze-tariff│  │
│  │ - /retrain (SSE streaming)   │  │ │  │ - /health       │  │
│  │ - /model/status              │  │ │  └─────────────────┘  │
│  │ - /plot                      │  │ │                       │
│  └──────────────────────────────┘  │ │                       │
└────────────────────────────────────┘ └───────────────────────┘
```

---

## 🚀 Quick Start (One Command)

### Automated Startup
```powershell
cd d:\model_shardha
.\start_all_services.ps1
```

This will:
1. ✅ Start Forecast API on port 8002
2. ✅ Start Tariff API on port 8003
3. ✅ Start Frontend on port 5173
4. ✅ Open browser automatically

---

## 📦 Manual Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip
- npm

### Backend Setup

#### 1. Install Python Dependencies
```powershell
cd d:\model_shardha
pip install -r requirements.txt
```

#### 2. Start Forecast API (Terminal 1)
```powershell
cd d:\model_shardha
uvicorn new_full_api:app --reload --port 8002
```

**Available at:** `http://localhost:8002`

**Endpoints:**
- `POST /forecast` - Generate sales forecast
- `POST /retrain` - Retrain model with new data (SSE streaming)
- `GET /model/status` - Check model status
- `GET /plot` - Get forecast plot
- `GET /dataset/products` - List all products

#### 3. Start Tariff API (Terminal 2)
```powershell
cd d:\model_shardha
uvicorn main2:app --reload --port 8003
```

**Available at:** `http://localhost:8003`

**Endpoints:**
- `POST /analyze-tariff` - Analyze tariff impact
- `GET /health` - Health check

### Frontend Setup

#### 1. Install Dependencies (Terminal 3)
```powershell
cd d:\model_shardha\frontend
npm install
```

#### 2. Start Development Server
```powershell
npm run dev
```

**Available at:** `http://localhost:5173`

---

## 🎯 Features

### 1. **Forecast Dashboard** ⚡
- Generate forecasts for 1-365 days
- Filter by:
  - Product ID
  - Category
  - Region
  - Min Rating
  - Max Price
  - Min Discount
- Interactive charts with confidence intervals
- Detailed forecast tables
- Real-time API health monitoring

### 2. **Retrain Model** 🔄
- Upload CSV files (date, sales columns)
- Real-time progress streaming (Server-Sent Events)
- Automatic model reload
- Prophet + LSTM hybrid retraining
- Success/error feedback
- Progress logs display

### 3. **Tariff Analyzer** 💰
- Product-specific or category-wide analysis
- Calculate price impact of tariff changes
- Visual comparison charts
- Detailed impact tables
- Percentage increase calculations
- Summary statistics

---

## 📡 API Documentation

### Forecast API (Port 8002)

#### Generate Forecast
```bash
POST http://localhost:8002/forecast
Content-Type: application/json

{
  "days": 7,
  "product_id": "P001",
  "category": "Electronics",
  "region": "North America",
  "min_rating": 4.0,
  "max_price": 1000,
  "min_discount": 10
}
```

**Response:**
```json
{
  "forecast": [
    {
      "ds": "2025-10-30",
      "yhat": 150.5,
      "yhat_lower": 120.3,
      "yhat_upper": 180.7
    }
  ]
}
```

#### Retrain Model
```bash
POST http://localhost:8002/retrain
Content-Type: multipart/form-data

file: <CSV file with date,sales columns>
```

**Response:** Server-Sent Events (SSE) stream
```
data: {"status": "progress", "message": "Uploading file..."}
data: {"status": "progress", "message": "Training Prophet model..."}
data: {"status": "progress", "message": "Training LSTM model..."}
data: {"status": "complete", "message": "Model retrained successfully"}
```

### Tariff API (Port 8003)

#### Analyze Tariff Impact
```bash
POST http://localhost:8003/analyze-tariff
Content-Type: application/json

{
  "product_id": "PROD001",
  "tariff_percentage": 15.0,
  "category": "Electronics"
}
```

**Response:**
```json
{
  "impacts": [
    {
      "product_id": "PROD001",
      "current_price": 100.00,
      "price_increase": 15.00,
      "new_price": 115.00,
      "impact_percentage": 15.00
    }
  ],
  "summary": "Tariff of 15.0% will increase prices by $15.00 on average"
}
```

---

## 📁 Project Structure

```
d:\model_shardha\
│
├── new_full_api.py              # Forecast & Retrain API (Port 8002)
├── main2.py                     # Tariff Analyzer API (Port 8003)
├── model.py                     # ML models (Prophet + LSTM)
├── tariff_impact_model.py       # Tariff impact ML model
├── requirements.txt             # Python dependencies
├── start_all_services.ps1       # Automated startup script
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ForecastDashboard.jsx
│   │   │   ├── RetrainDashboard.jsx
│   │   │   └── TariffAnalyzer.jsx
│   │   ├── App_new.jsx          # Main app
│   │   ├── App_new.css          # Custom styles
│   │   ├── main.jsx             # Entry point
│   │   └── index_new.css        # Global styles
│   ├── package.json
│   ├── vite.config.js
│   ├── setup.ps1                # Frontend setup script
│   └── README_NEW.md
│
└── SYSTEM_README.md             # This file
```

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern async web framework
- **Prophet** - Time series forecasting
- **TensorFlow/Keras** - LSTM neural networks
- **Pandas** - Data manipulation
- **Uvicorn** - ASGI server

### Frontend
- **React 19** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Utility-first CSS
- **Recharts** - Data visualization
- **Lucide React** - Icon library

---

## 🧪 Testing

### Test Forecast API
```powershell
curl http://localhost:8002/
curl http://localhost:8002/model/status
```

### Test Tariff API
```powershell
curl http://localhost:8003/health
```

### Test Frontend
Open `http://localhost:5173` in browser

---

## 🔧 Configuration

### Change API Ports

#### Backend
Edit `start_all_services.ps1`:
```powershell
uvicorn new_full_api:app --reload --port 8002  # Change 8002
uvicorn main2:app --reload --port 8003         # Change 8003
```

#### Frontend
Edit `frontend/src/App_new.jsx`:
```javascript
export const API = {
  forecast: {
    base: "http://localhost:8002",  // Change URL
    // ...
  },
  tariff: {
    base: "http://localhost:8003",  // Change URL
    // ...
  },
};
```

---

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Kill process on specific port
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8002).OwningProcess -Force
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8003).OwningProcess -Force
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess -Force
```

### Backend Not Starting
- Check Python version: `python --version`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check for missing models or data files

### Frontend Build Errors
```powershell
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS Errors
- Ensure both backend APIs have CORS enabled
- Check `allow_origins=["*"]` in FastAPI apps

---

## 📊 Usage Examples

### Example 1: Generate 30-Day Forecast
1. Open Frontend → **Forecast** tab
2. Set Days: `30`
3. Select Product: `P001`
4. Click **Get Forecast**
5. View chart and table

### Example 2: Retrain Model
1. Open Frontend → **Retrain** tab
2. Upload CSV file (format: date,sales)
3. Click **Start Retraining**
4. Monitor progress logs
5. Wait for completion

### Example 3: Analyze Tariff Impact
1. Open Frontend → **Tariff Analyzer** tab
2. Product ID: `PROD001`
3. Tariff Percentage: `15`
4. Category: `Electronics`
5. Click **Analyze Tariff Impact**
6. View price changes and charts

---

## 🚢 Deployment

### Production Build

#### Backend
```powershell
# Use gunicorn with uvicorn workers
pip install gunicorn
gunicorn new_full_api:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8002
gunicorn main2:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8003
```

#### Frontend
```powershell
cd frontend
npm run build
# Deploy `dist/` folder to hosting service
```

---

## 📝 API Endpoints Summary

### Forecast API (8002)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/forecast` | Generate forecast |
| POST | `/retrain` | Retrain model (SSE) |
| GET | `/model/status` | Model info |
| GET | `/plot` | Forecast plot |
| GET | `/dataset/products` | List products |

### Tariff API (8003)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| POST | `/analyze-tariff` | Analyze tariff |

---

## 📄 License

MIT License

---

## 🎓 Credits

Built with:
- Prophet by Facebook Research
- TensorFlow by Google
- React by Meta
- FastAPI by Sebastián Ramírez

---

## 📞 Support

For issues:
1. Check backend logs in terminals
2. Check browser console for frontend errors
3. Verify all ports are accessible
4. Ensure data files are present

---

**🚀 Happy Forecasting!**
