# AI Inventory Management Frontend

Modern React frontend for AI-powered inventory forecasting and tariff impact analysis.

## 🚀 Features

### 1. **Forecast Dashboard** (Port 8002)
- Generate sales forecasts for 1-365 days
- Filter by product ID, category, region
- Advanced filters: rating, price, discount
- Interactive charts with confidence intervals
- Detailed forecast tables

### 2. **Retrain Model** (Port 8002)
- Upload CSV files to retrain Prophet+LSTM models
- Real-time progress streaming (SSE)
- CSV format validation
- Success/error feedback

### 3. **Tariff Analyzer** (Port 8003)
- Analyze tariff impact on products
- Product-specific or category-wide analysis
- Price increase calculations
- Impact visualization with charts

## 📦 Tech Stack

- **React 19** - UI Framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **Axios** - HTTP client (optional)

## 🛠️ Setup

### Prerequisites
- Node.js 18+ installed
- Both backend APIs running:
  - Forecast API on `http://localhost:8002`
  - Tariff API on `http://localhost:8003`

### Installation

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Configure environment (optional):**
Create `.env.local`:
```env
VITE_FORECAST_API_URL=http://localhost:8002
VITE_TARIFF_API_URL=http://localhost:8003
```

3. **Start development server:**
```bash
npm run dev
```

The app will run on `http://localhost:5173`

## 🎯 Usage

### Forecast Tab
1. Select forecast parameters (days, product, filters)
2. Click "Get Forecast"
3. View charts and detailed predictions

### Retrain Tab
1. Upload CSV file with columns: `date`, `sales`
2. Click "Start Retraining"
3. Monitor real-time progress logs
4. Wait for completion confirmation

### Tariff Analyzer Tab
1. Enter product ID (or leave empty for category)
2. Set tariff percentage
3. Specify category
4. Click "Analyze Tariff Impact"
5. View price changes and impact charts

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ForecastDashboard.jsx   # Forecasting UI
│   │   ├── RetrainDashboard.jsx    # Model retraining
│   │   └── TariffAnalyzer.jsx      # Tariff analysis
│   ├── App_new.jsx                 # Main app component
│   ├── App_new.css                 # Custom styles
│   ├── main.jsx                    # Entry point
│   └── index_new.css               # Tailwind + global styles
├── package.json
├── vite.config.js
└── README.md
```

## 🔌 API Integration

### Forecast API (Port 8002)
```javascript
POST /forecast
{
  "days": 7,
  "product_id": "P001",
  "category": "Electronics"
}
```

### Retrain API (Port 8002)
```javascript
POST /retrain
Content-Type: multipart/form-data
file: <CSV file>
```

### Tariff API (Port 8003)
```javascript
POST /analyze-tariff
{
  "product_id": "PROD001",
  "tariff_percentage": 15.0,
  "category": "Electronics"
}
```

## 🎨 Customization

### Change API URLs
Edit `src/App_new.jsx`:
```javascript
export const API = {
  forecast: {
    base: "http://localhost:8002",
    // ...
  },
  tariff: {
    base: "http://localhost:8003",
    // ...
  },
};
```

### Modify Styles
- Edit `src/index_new.css` for global styles
- Edit `src/App_new.css` for component styles
- Tailwind classes in JSX files

## 📊 Screenshots

### Forecast Dashboard
- Interactive forecast chart
- Parameter selection
- Detailed data tables

### Retrain Dashboard
- CSV upload interface
- Real-time progress logs
- Success indicators

### Tariff Analyzer
- Price impact visualization
- Comparison charts
- Detailed impact breakdown

## 🐛 Troubleshooting

### API Connection Issues
- Ensure backend APIs are running
- Check CORS settings on backend
- Verify ports 8002 and 8003 are accessible

### Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Tailwind Not Working
Ensure `tailwind.config.js` and `postcss.config.js` are present

## 📝 Development

### Available Scripts

```bash
npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

## 🚢 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Static Hosting
```bash
# Upload `dist/` folder to:
# - Netlify
# - Vercel
# - GitHub Pages
# - AWS S3
```

## 📄 License

MIT License

## 👥 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

---

**Built with ❤️ for AI-powered inventory management**
