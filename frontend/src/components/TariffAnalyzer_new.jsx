import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { DollarSign, Package, TrendingDown, TrendingUp, Loader2, AlertCircle, Activity, CheckCircle, Shield, Lightbulb } from 'lucide-react';
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
        throw new Error(errorData.detail || 'API Error');
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
    const colors = {
      'LOW': 'green',
      'MEDIUM': 'yellow',
      'HIGH': 'orange',
      'CRITICAL': 'red'
    };
    return colors[level] || 'gray';
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
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
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg p-6 shadow-lg">
              <h3 className="text-sm font-medium opacity-90">Current Avg Price</h3>
              <p className="text-3xl font-bold mt-2">
                {formatCurrency(result.current_metrics?.average_price || 0)}
              </p>
              <p className="text-xs opacity-75 mt-1">Before tariff</p>
            </div>

            <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-lg p-6 shadow-lg">
              <h3 className="text-sm font-medium opacity-90">New Price (Est.)</h3>
              <p className="text-3xl font-bold mt-2">
                {formatCurrency(result.projected_impact?.estimated_new_price || 0)}
              </p>
              <p className="text-xs opacity-75 mt-1">After {result.tariff_percentage}% tariff</p>
            </div>

            <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-lg p-6 shadow-lg">
              <h3 className="text-sm font-medium opacity-90">Sales Impact</h3>
              <p className="text-3xl font-bold mt-2">
                {result.projected_impact?.estimated_sales_change || '0%'}
              </p>
              <p className="text-xs opacity-75 mt-1">Estimated change</p>
            </div>

            <div className={`bg-gradient-to-br from-${getWarningColor(result.recommendations?.warning_level)}-500 to-${getWarningColor(result.recommendations?.warning_level)}-600 text-white rounded-lg p-6 shadow-lg`}>
              <h3 className="text-sm font-medium opacity-90">Warning Level</h3>
              <p className="text-3xl font-bold mt-2">
                {result.recommendations?.warning_level || 'N/A'}
              </p>
              <p className="text-xs opacity-75 mt-1">{result.recommendations?.stock_strategy || 'N/A'}</p>
            </div>
          </div>

          {/* Price Comparison Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Price Impact Visualization</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={[
                {
                  name: 'Current',
                  price: result.current_metrics?.average_price || 0,
                  fill: '#3b82f6'
                },
                {
                  name: 'After Tariff',
                  price: result.projected_impact?.estimated_new_price || 0,
                  fill: '#ef4444'
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

          {/* Current Metrics */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
              <Activity size={20} className="text-blue-600" />
              <span>Current Market Metrics</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-700 mb-1">Average Price</p>
                <p className="text-2xl font-bold text-blue-900">
                  {formatCurrency(result.current_metrics?.average_price || 0)}
                </p>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm text-green-700 mb-1">Average Daily Sales</p>
                <p className="text-2xl font-bold text-green-900">
                  {(result.current_metrics?.average_sales || 0).toFixed(2)} units
                </p>
              </div>
            </div>
          </div>

          {/* Projected Impact */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
              <TrendingUp size={20} className="text-red-600" />
              <span>Projected Impact</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-700 mb-1">Estimated New Price</p>
                <p className="text-2xl font-bold text-red-900">
                  {formatCurrency(result.projected_impact?.estimated_new_price || 0)}
                </p>
              </div>
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <p className="text-sm text-orange-700 mb-1">Sales Change</p>
                <p className="text-2xl font-bold text-orange-900">
                  {result.projected_impact?.estimated_sales_change || '0%'}
                </p>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <p className="text-sm text-purple-700 mb-1">Projected Daily Sales</p>
                <p className="text-2xl font-bold text-purple-900">
                  {(result.projected_impact?.projected_daily_sales || 0).toFixed(2)} units
                </p>
              </div>
            </div>
          </div>

          {/* AI Recommendations */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
              <Shield size={20} className={`text-${getWarningColor(result.recommendations?.warning_level)}-600`} />
              <span>Recommendations & Strategy</span>
            </h3>

            <div className="space-y-4">
              {/* Warning Level */}
              <div className={`bg-${getWarningColor(result.recommendations?.warning_level)}-50 border border-${getWarningColor(result.recommendations?.warning_level)}-200 rounded-lg p-4`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-gray-800">Warning Level:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-bold text-white bg-${getWarningColor(result.recommendations?.warning_level)}-600`}>
                    {result.recommendations?.warning_level || 'N/A'}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-gray-800">Stock Strategy:</span>
                  <span className="text-gray-700">{result.recommendations?.stock_strategy || 'N/A'}</span>
                </div>
              </div>

              {/* Action Items */}
              {result.recommendations?.action_items && result.recommendations.action_items.length > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-800 mb-3 flex items-center space-x-2">
                    <CheckCircle size={18} />
                    <span>Action Items</span>
                  </h4>
                  <ul className="space-y-2">
                    {result.recommendations.action_items.map((item, index) => (
                      <li key={index} className="flex items-start space-x-2 text-blue-700">
                        <span className="mt-1">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* AI Analysis */}
              {result.recommendations?.ai_analysis && (
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h4 className="font-semibold text-purple-800 mb-3 flex items-center space-x-2">
                    <Lightbulb size={18} />
                    <span>AI-Powered Analysis</span>
                  </h4>
                  <div className="text-sm text-purple-700 whitespace-pre-wrap max-h-96 overflow-y-auto">
                    {result.recommendations.ai_analysis}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Product Information */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Analysis Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Product ID:</span>
                <span className="ml-2 font-semibold text-gray-800">{result.product_id}</span>
              </div>
              <div>
                <span className="text-gray-600">Category:</span>
                <span className="ml-2 font-semibold text-gray-800">{result.category}</span>
              </div>
              <div>
                <span className="text-gray-600">Tariff Rate:</span>
                <span className="ml-2 font-semibold text-gray-800">{result.tariff_percentage}%</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
