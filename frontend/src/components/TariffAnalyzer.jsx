import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { DollarSign, Package, TrendingDown, TrendingUp, Loader2, AlertCircle, Activity, IndianRupee, Target, ShoppingCart, Lightbulb } from 'lucide-react';
import { API } from '../App_new';

export default function TariffAnalyzer({ onHealthChange }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    product_id: 'P001',
    tariff_percentage: 15,
    category: 'Electronics'
  });

  // Check API health on mount
  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const res = await fetch(API.tariff.health);
      const data = await res.json();
      onHealthChange?.(data.status === 'healthy' ? 'online' : 'offline');
    } catch (err) {
      onHealthChange?.('offline');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'tariff_percentage' ? parseFloat(value) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(API.tariff.analyze, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || `API Error: ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to analyze tariff impact');
    } finally {
      setLoading(false);
    }
  };

  const getWarningColor = (level) => {
    switch (level) {
      case 'LOW': return 'green';
      case 'MEDIUM': return 'yellow';
      case 'HIGH': return 'orange';
      case 'CRITICAL': return 'red';
      default: return 'gray';
    }
  };

  const formatCurrency = (value) => {
    return `₹${parseFloat(value).toFixed(2)}`;
  };

  return (
    <div className="space-y-6">
      {/* Tariff Form */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center space-x-2 mb-6">
          <DollarSign className="text-green-600" size={24} />
          <h2 className="text-2xl font-bold text-gray-800">Tariff Impact Analysis</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Product ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Package size={16} className="inline mr-1" />
                Product ID
              </label>
              <input
                type="text"
                name="product_id"
                value={formData.product_id}
                onChange={handleInputChange}
                placeholder="e.g., P001"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">Leave empty for category analysis</p>
            </div>

            {/* Tariff Percentage */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <TrendingUp size={16} className="inline mr-1" />
                Tariff Percentage
              </label>
              <input
                type="number"
                name="tariff_percentage"
                value={formData.tariff_percentage}
                onChange={handleInputChange}
                min="0"
                max="100"
                step="0.1"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
              <p className="text-xs text-gray-500 mt-1">Tariff rate to apply (0-100%)</p>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Activity size={16} className="inline mr-1" />
                Category
              </label>
              <input
                type="text"
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                placeholder="e.g., Electronics"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">Product category</p>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-green-500 to-green-600 text-white py-3 rounded-lg font-semibold hover:from-green-600 hover:to-green-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                <span>Analyzing Impact...</span>
              </>
            ) : (
              <>
                <DollarSign size={20} />
                <span>Analyze Tariff Impact</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <h3 className="font-semibold text-red-800">Error</h3>
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg p-6 shadow-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium opacity-90">Current Avg Price</h3>
                <IndianRupee size={20} />
              </div>
              <p className="text-3xl font-bold">{formatCurrency(result.current_metrics.average_price)}</p>
              <p className="text-xs opacity-75 mt-1">Before tariff</p>
            </div>

            <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-lg p-6 shadow-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium opacity-90">Estimated New Price</h3>
                <TrendingUp size={20} />
              </div>
              <p className="text-3xl font-bold">{formatCurrency(result.projected_impact.estimated_new_price)}</p>
              <p className="text-xs opacity-75 mt-1">After {formData.tariff_percentage}% tariff</p>
            </div>

            <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-lg p-6 shadow-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium opacity-90">Sales Impact</h3>
                <TrendingDown size={20} />
              </div>
              <p className="text-3xl font-bold">{result.projected_impact.estimated_sales_change}</p>
              <p className="text-xs opacity-75 mt-1">Projected change</p>
            </div>
          </div>

          {/* Current vs Projected Metrics */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Current vs Projected Comparison</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Current Metrics */}
              <div className="border-2 border-blue-200 rounded-lg p-4 bg-blue-50">
                <h4 className="font-semibold text-blue-800 mb-3 flex items-center">
                  <Activity size={18} className="mr-2" />
                  Current Metrics
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">Average Price:</span>
                    <span className="font-bold text-blue-600">{formatCurrency(result.current_metrics.average_price)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">Average Sales (Daily):</span>
                    <span className="font-bold text-blue-600">{result.current_metrics.average_sales.toFixed(2)} units</span>
                  </div>
                </div>
              </div>

              {/* Projected Impact */}
              <div className="border-2 border-orange-200 rounded-lg p-4 bg-orange-50">
                <h4 className="font-semibold text-orange-800 mb-3 flex items-center">
                  <Target size={18} className="mr-2" />
                  Projected Impact
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">New Price:</span>
                    <span className="font-bold text-orange-600">{formatCurrency(result.projected_impact.estimated_new_price)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">Sales Change:</span>
                    <span className="font-bold text-red-600">{result.projected_impact.estimated_sales_change}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">Projected Daily Sales:</span>
                    <span className="font-bold text-orange-600">{result.projected_impact.projected_daily_sales.toFixed(2)} units</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Price Comparison Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Price Impact Visualization</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={[
                {
                  name: 'Before Tariff',
                  price: result.current_metrics.average_price,
                },
                {
                  name: 'After Tariff',
                  price: result.projected_impact.estimated_new_price,
                }
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="name" stroke="#6b7280" />
                <YAxis stroke="#6b7280" label={{ value: 'Price (₹)', angle: -90, position: 'insideLeft' }} />
                <Tooltip 
                  formatter={(value) => formatCurrency(value)}
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                />
                <Bar dataKey="price" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Recommendations Section */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              <Lightbulb className="mr-2 text-yellow-500" size={24} />
              AI Recommendations
            </h3>

            {/* Warning Level */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Warning Level:</span>
                <span className={`px-4 py-2 rounded-full text-sm font-bold bg-${getWarningColor(result.recommendations.warning_level)}-100 text-${getWarningColor(result.recommendations.warning_level)}-800`}>
                  {result.recommendations.warning_level}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Stock Strategy:</span>
                <span className="px-4 py-2 rounded-full text-sm font-bold bg-blue-100 text-blue-800">
                  {result.recommendations.stock_strategy.replace(/_/g, ' ')}
                </span>
              </div>
            </div>

            {/* Action Items */}
            <div className="mb-6">
              <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                <ShoppingCart size={18} className="mr-2" />
                Action Items
              </h4>
              <ul className="space-y-2">
                {result.recommendations.action_items.map((item, index) => (
                  <li key={index} className="flex items-start space-x-2 text-sm text-gray-700">
                    <span className="text-green-600 font-bold">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* AI Analysis */}
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4">
              <h4 className="font-semibold text-purple-800 mb-3 flex items-center">
                <Activity size={18} className="mr-2" />
                AI-Powered Analysis
              </h4>
              <div className="text-sm text-gray-700 whitespace-pre-wrap max-h-96 overflow-y-auto">
                {result.recommendations.ai_analysis}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
