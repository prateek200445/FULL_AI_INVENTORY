import { useState } from 'react';
import ForecastDashboard from './components/ForecastDashboard';
import RetrainDashboard from './components/RetrainDashboard';
import TariffAnalyzer from './components/TariffAnalyzer';
import { TrendingUp, RefreshCw, DollarSign, Activity } from 'lucide-react';
import './App.css';

/* ========================
   API CONFIG
======================== */
const API = {
  forecast: {
    base: import.meta.env.VITE_FORECAST_API_URL || "http://localhost:8002",
    forecast: "http://localhost:8002/forecast",
    retrain: "http://localhost:8002/retrain",
    modelStatus: "http://localhost:8002/model/status",
    plot: "http://localhost:8002/plot",
    health: "http://localhost:8002/",
  },
  tariff: {
    base: import.meta.env.VITE_TARIFF_API_URL || "http://localhost:8003",
    analyze: "http://localhost:8003/analyze-tariff",
    health: "http://localhost:8003/health",
  },
};

/* ========================
   UTILITIES
======================== */
const j = (o) => JSON.stringify(o, null, 2);

export default function ApiDashboard() {
  const [activeTab, setActiveTab] = useState("tariff");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [toast, setToast] = useState(null);

  /* ====== TARIFF INPUTS ====== */
  const [tariff, setTariff] = useState({
    product_id: "PROD001",
    tariff_percentage: 15,
    category: "Electronics",
  });

  /* ====== FORECAST INPUTS ====== */
  const [forecast, setForecast] = useState({
    days: 7,
    product_id: "P001",
    category: "General",
    region: "India",
    min_rating: 0,
    max_price: 0,
    min_discount: 0,
  });

  /* ====== TOAST SYSTEM ====== */
  const showToast = (msg, type = "ok") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 2500);
  };

  /* ====== HANDLERS ====== */
  const runTariffAnalysis = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(API.tariff.analyze, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(tariff),
      });
      if (!res.ok) throw new Error("Bad response");
      const data = await res.json();
      setResult(data);
      showToast("Tariff Analysis Successful ✅");
    } catch (err) {
      showToast("Tariff Analysis Failed ❌", "error");
    } finally {
      setLoading(false);
    }
  };

  const runForecast = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(API.forecast.forecast, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(forecast),
      });
      if (!res.ok) throw new Error("Bad response");
      const data = await res.json();
      setResult(data);
      showToast("Forecast Retrieved ✅");
    } catch (err) {
      showToast("Forecast Request Failed ❌", "error");
    } finally {
      setLoading(false);
    }
  };

  /* ========================
     UI RENDER
  ========================= */
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      {/* Header */}
      <header className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Activity className="text-blue-400" /> Localhost API Dashboard
        </h1>

        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab("tariff")}
            className={`px-4 py-2 rounded-lg ${
              activeTab === "tariff"
                ? "bg-blue-600"
                : "bg-zinc-800 hover:bg-zinc-700"
            }`}
          >
            Tariff Impact
          </button>
          <button
            onClick={() => setActiveTab("forecast")}
            className={`px-4 py-2 rounded-lg ${
              activeTab === "forecast"
                ? "bg-green-600"
                : "bg-zinc-800 hover:bg-zinc-700"
            }`}
          >
            Forecast
          </button>
        </div>
      </header>

      {/* Panels */}
      <AnimatePresence mode="wait">
        {activeTab === "tariff" ? (
          <motion.div
            key="tariff"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="bg-zinc-900 p-6 rounded-2xl shadow-xl"
          >
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <BarChart3 className="text-blue-400" /> Tariff Impact Analysis
            </h2>

            <div className="grid md:grid-cols-3 gap-4">
              <input
                value={tariff.product_id}
                onChange={(e) =>
                  setTariff({ ...tariff, product_id: e.target.value })
                }
                className="bg-zinc-800 p-2 rounded"
                placeholder="Product ID"
              />
              <input
                type="number"
                value={tariff.tariff_percentage}
                onChange={(e) =>
                  setTariff({
                    ...tariff,
                    tariff_percentage: parseFloat(e.target.value),
                  })
                }
                className="bg-zinc-800 p-2 rounded"
                placeholder="Tariff %"
              />
              <input
                value={tariff.category}
                onChange={(e) =>
                  setTariff({ ...tariff, category: e.target.value })
                }
                className="bg-zinc-800 p-2 rounded"
                placeholder="Category"
              />
            </div>

            <button
              onClick={runTariffAnalysis}
              disabled={loading}
              className="mt-5 flex items-center gap-2 bg-blue-600 px-4 py-2 rounded-lg"
            >
              {loading ? <Loader2 className="animate-spin" /> : <UploadCloud />}
              Analyze
            </button>
          </motion.div>
        ) : (
          <motion.div
            key="forecast"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="bg-zinc-900 p-6 rounded-2xl shadow-xl"
          >
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Database className="text-green-400" /> Forecast Request
            </h2>

            <div className="grid md:grid-cols-3 gap-4">
              <select
                className="bg-zinc-800 p-2 rounded"
                value={forecast.product_id}
                onChange={(e) =>
                  setForecast({ ...forecast, product_id: e.target.value })
                }
              >
                {[...Array(15)].map((_, i) => (
                  <option key={i} value={`P00${i + 1}`}>
                    P00{i + 1}
                  </option>
                ))}
              </select>
              <input
                type="number"
                value={forecast.days}
                onChange={(e) =>
                  setForecast({ ...forecast, days: parseInt(e.target.value) })
                }
                className="bg-zinc-800 p-2 rounded"
                placeholder="Days"
              />
              <input
                value={forecast.category}
                onChange={(e) =>
                  setForecast({ ...forecast, category: e.target.value })
                }
                className="bg-zinc-800 p-2 rounded"
                placeholder="Category"
              />
              <input
                value={forecast.region}
                onChange={(e) =>
                  setForecast({ ...forecast, region: e.target.value })
                }
                className="bg-zinc-800 p-2 rounded"
                placeholder="Region"
              />
              <input
                type="number"
                value={forecast.min_rating}
                onChange={(e) =>
                  setForecast({ ...forecast, min_rating: +e.target.value })
                }
                className="bg-zinc-800 p-2 rounded"
                placeholder="Min Rating"
              />
              <input
                type="number"
                value={forecast.max_price}
                onChange={(e) =>
                  setForecast({ ...forecast, max_price: +e.target.value })
                }
                className="bg-zinc-800 p-2 rounded"
                placeholder="Max Price"
              />
              <input
                type="number"
                value={forecast.min_discount}
                onChange={(e) =>
                  setForecast({ ...forecast, min_discount: +e.target.value })
                }
                className="bg-zinc-800 p-2 rounded"
                placeholder="Min Discount"
              />
            </div>

            <button
              onClick={runForecast}
              disabled={loading}
              className="mt-5 flex items-center gap-2 bg-green-600 px-4 py-2 rounded-lg"
            >
              {loading ? <Loader2 className="animate-spin" /> : <RefreshCw />}
              Run Forecast
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Result */}
      {result && (
        <pre className="mt-6 bg-zinc-950 border border-zinc-800 p-4 rounded-lg text-sm overflow-auto">
          {j(result)}
        </pre>
      )}

      {/* Toast */}
      {toast && (
        <div
          className={`fixed bottom-4 right-4 px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 ${
            toast.type === "error"
              ? "bg-red-800 text-red-100"
              : "bg-green-800 text-green-100"
          }`}
        >
          {toast.type === "error" ? <XCircle /> : <CheckCircle2 />}
          {toast.msg}
        </div>
      )}
    </div>
  );
}