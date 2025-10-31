import { useState } from 'react';
import ForecastDashboard from './components/ForecastDashboard';
import RetrainDashboard from './components/RetrainDashboard';
import TariffAnalyzer from './components/TariffAnalyzer';
import { TrendingUp, RefreshCw, DollarSign, Activity, Globe, MessageCircle, IndianRupee, Layout } from 'lucide-react';
import './App_new.css';

export const API = {
  forecast: {
    base: "http://localhost:8002",
    forecast: "http://localhost:8002/forecast",
    retrain: "http://localhost:8002/retrain",
    modelStatus: "http://localhost:8002/model/status",
    plot: "http://localhost:8002/plot",
    health: "http://localhost:8002/",
    products: "http://localhost:8002/dataset/products",
  },
  tariff: {
    base: "http://localhost:8003",
    analyze: "http://localhost:8003/analyze-tariff",
    health: "http://localhost:8003/health",
  },
};

function App() {
  const [activeTab, setActiveTab] = useState('forecast');
  const [healthStatus, setHealthStatus] = useState({
    forecast: null,
    tariff: null
  });

  const tabs = [
    { id: 'forecast', name: 'Forecast', icon: TrendingUp, color: 'blue' },
    { id: 'retrain', name: 'Retrain Model', icon: RefreshCw, color: 'purple' },
    { id: 'tariff', name: 'Tariff Analyzer', icon: DollarSign, color: 'green' },
    { id: 'price-prediction', name: 'Price Prediction', icon: IndianRupee, color: 'teal', external: true, url: 'https://product-price-prediction-27fv.onrender.com' },
    { id: 'country-pricing', name: 'Country Based Pricing', icon: Globe, color: 'orange', external: true, url: 'https://country-based-prediction-3.onrender.com' },
    { id: 'inventory-assistant', name: 'Inventory Assistant', icon: MessageCircle, color: 'indigo', external: true, url: 'https://chatbot-ai-inventory.onrender.com/' },
    { id: 'inventory-sarthi', name: 'Inventory Sarthi ERP', icon: Layout, color: 'rose', external: true, url: 'https://9000-firebase-studio-1761631759166.cluster-aic6jbiihrhmyrqafasatvzbwe.cloudworkstations.dev' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-md border-b border-gray-200">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
                <Activity className="text-white" size={28} />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  AI Inventory Management
                </h1>
                <p className="text-sm text-gray-600">Personalized ERP System - Forecasting, Analysis & Intelligence Platform</p>
              </div>
            </div>

            {/* Health Status Indicators */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${healthStatus.forecast === 'online' ? 'bg-green-500' : 'bg-gray-300'} animate-pulse`}></div>
                <span className="text-xs text-gray-600">Forecast API</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${healthStatus.tariff === 'online' ? 'bg-green-500' : 'bg-gray-300'} animate-pulse`}></div>
                <span className="text-xs text-gray-600">Tariff API</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-6">
          <nav className="flex space-x-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              
              // Handle external link tabs
              if (tab.external) {
                return (
                  <a
                    key={tab.id}
                    href={tab.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-2 px-6 py-4 font-medium transition-all text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                  >
                    <Icon size={20} />
                    <span>{tab.name}</span>
                    <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                );
              }
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center space-x-2 px-6 py-4 font-medium transition-all relative
                    ${isActive 
                      ? 'text-blue-600 border-b-2 border-blue-600' 
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }
                  `}
                >
                  <Icon size={20} />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {activeTab === 'forecast' && <ForecastDashboard onHealthChange={(status) => setHealthStatus(prev => ({ ...prev, forecast: status }))} />}
        {activeTab === 'retrain' && <RetrainDashboard />}
        {activeTab === 'tariff' && <TariffAnalyzer onHealthChange={(status) => setHealthStatus(prev => ({ ...prev, tariff: status }))} />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center text-sm text-gray-600">
            <p>© 2025 AI Inventory Management System</p>
            <div className="flex items-center space-x-4">
              <span>Forecast API: Port 8002</span>
              <span>•</span>
              <span>Tariff API: Port 8003</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
