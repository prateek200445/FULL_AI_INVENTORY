import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { TrendingUp, Calendar, Package, MapPin, Star, DollarSign, Percent, Search, Loader2, AlertCircle, Camera } from 'lucide-react';
import { API } from '../App_new';
import QRScanner from './QRScanner';

export default function ForecastDashboard({ onHealthChange }) {
  const [loading, setLoading] = useState(false);
  const [forecastData, setForecastData] = useState(null);
  const [error, setError] = useState(null);
  const [products, setProducts] = useState([]);
  const [showQRScanner, setShowQRScanner] = useState(false);

  const [formData, setFormData] = useState({
    days: 7,
    product_id: '',
    category: '',
    region: '',
    min_rating: '',
    max_price: '',
    min_discount: ''
  });

  // Check API health on mount
  useEffect(() => {
    checkHealth();
    fetchProducts();
  }, []);

  const checkHealth = async () => {
    try {
      const res = await fetch(API.forecast.health);
      const data = await res.json();
      onHealthChange?.(data.status === 'running' ? 'online' : 'offline');
    } catch (err) {
      onHealthChange?.('offline');
    }
  };

  const fetchProducts = async () => {
    try {
      const res = await fetch(API.forecast.products);
      const data = await res.json();
      setProducts(data.products || []);
    } catch (err) {
      console.error('Failed to fetch products:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleQRScan = (decodedText) => {
    console.log(`🎯 QR Scan successful! Product ID: ${decodedText}`);
    // Set the scanned product ID in the form
    setFormData(prev => ({
      ...prev,
      product_id: decodedText
    }));
    setShowQRScanner(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setForecastData(null);

    try {
      // Clean up form data (remove empty strings)
      const cleanedData = Object.entries(formData).reduce((acc, [key, value]) => {
        if (value !== '' && value !== null) {
          acc[key] = key === 'days' ? parseInt(value) : 
                     ['min_rating', 'max_price', 'min_discount'].includes(key) ? parseFloat(value) : value;
        }
        return acc;
      }, {});

      const res = await fetch(API.forecast.forecast, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cleanedData)
      });

      if (!res.ok) {
        throw new Error(`API Error: ${res.status}`);
      }

      const data = await res.json();
      
      // Transform the API response to match frontend expectations
      const transformedData = {
        ...data,
        forecast: data.Forecast ? Object.entries(data.Forecast).map(([date, values]) => ({
          ds: date,
          yhat: values.forecast,
          yhat_lower: values.lower_bound,
          yhat_upper: values.upper_bound
        })) : [],
        reorder_point: data['Reorder Point'],
        safety_stock: data['Safety Stock'],
        minimum_level: data['Minimum Level'],
        maximum_level: data['Maximum Level'],
        warnings: data.Warnings || []
      };
      
      setForecastData(transformedData);
    } catch (err) {
      setError(err.message || 'Failed to fetch forecast');
    } finally {
      setLoading(false);
    }
  };

  const formatChartData = () => {
    if (!forecastData?.forecast) return [];
    
    return forecastData.forecast.map((item, index) => ({
      date: item.ds,
      predicted: Math.round(item.yhat),
      lower: Math.round(item.yhat_lower),
      upper: Math.round(item.yhat_upper),
      day: index + 1
    }));
  };

  return (
    <div className="space-y-6">
      {/* Forecast Form */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center space-x-2 mb-6">
          <TrendingUp className="text-blue-600" size={24} />
          <h2 className="text-2xl font-bold text-gray-800">Forecast Parameters</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Days */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar size={16} className="inline mr-1" />
                Forecast Days
              </label>
              <input
                type="number"
                name="days"
                value={formData.days}
                onChange={handleInputChange}
                min="1"
                max="365"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            {/* Product ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Package size={16} className="inline mr-1" />
                Product ID
              </label>
              <div className="flex space-x-2">
                <select
                  name="product_id"
                  value={formData.product_id}
                  onChange={handleInputChange}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Products</option>
                  <option value="P001">P001</option>
                  <option value="P002">P002</option>
                  <option value="P003">P003</option>
                  <option value="P004">P004</option>
                  <option value="P005">P005</option>
                  <option value="P006">P006</option>
                  <option value="P007">P007</option>
                  <option value="P008">P008</option>
                  <option value="P009">P009</option>
                  <option value="P010">P010</option>
                  <option value="P011">P011</option>
                  <option value="P012">P012</option>
                  <option value="P013">P013</option>
                  <option value="P014">P014</option>
                  <option value="P015">P015</option>
                  <option value="P016">P016</option>
                  <option value="P017">P017</option>
                  <option value="P018">P018</option>
                  <option value="P019">P019</option>
                  <option value="P020">P020</option>
                  <option value="P021">P021</option>
                  <option value="P022">P022</option>
                  <option value="P023">P023</option>
                  {products.filter(p => !p.match(/^P0\d{2}$/)).map(prod => (
                    <option key={prod} value={prod}>{prod}</option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={() => setShowQRScanner(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
                  title="Scan QR Code"
                >
                  <Camera size={20} />
                </button>
              </div>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Search size={16} className="inline mr-1" />
                Category
              </label>
              <input
                type="text"
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                placeholder="e.g., Electronics"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Region */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <MapPin size={16} className="inline mr-1" />
                Region
              </label>
              <input
                type="text"
                name="region"
                value={formData.region}
                onChange={handleInputChange}
                placeholder="e.g., North America"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Min Rating */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Star size={16} className="inline mr-1" />
                Min Rating
              </label>
              <input
                type="number"
                name="min_rating"
                value={formData.min_rating}
                onChange={handleInputChange}
                min="0"
                max="5"
                step="0.1"
                placeholder="0.0 - 5.0"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Max Price */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <DollarSign size={16} className="inline mr-1" />
                Max Price
              </label>
              <input
                type="number"
                name="max_price"
                value={formData.max_price}
                onChange={handleInputChange}
                min="0"
                placeholder="Maximum price"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Min Discount */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Percent size={16} className="inline mr-1" />
                Min Discount %
              </label>
              <input
                type="number"
                name="min_discount"
                value={formData.min_discount}
                onChange={handleInputChange}
                min="0"
                max="100"
                placeholder="Minimum discount"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white py-3 rounded-lg font-semibold hover:from-blue-600 hover:to-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                <span>Generating Forecast...</span>
              </>
            ) : (
              <>
                <TrendingUp size={20} />
                <span>Get Forecast</span>
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

      {/* Forecast Results */}
      {forecastData && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg p-6 shadow-lg">
              <h3 className="text-sm font-medium opacity-90">Total Forecast</h3>
              <p className="text-3xl font-bold mt-2">
                {forecastData.forecast?.reduce((sum, item) => sum + item.yhat, 0).toFixed(0)}
              </p>
              <p className="text-xs opacity-75 mt-1">units over {formData.days} days</p>
            </div>

            <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg p-6 shadow-lg">
              <h3 className="text-sm font-medium opacity-90">Daily Average</h3>
              <p className="text-3xl font-bold mt-2">
                {(forecastData.forecast?.reduce((sum, item) => sum + item.yhat, 0) / formData.days).toFixed(0)}
              </p>
              <p className="text-xs opacity-75 mt-1">units per day</p>
            </div>

            <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg p-6 shadow-lg">
              <h3 className="text-sm font-medium opacity-90">Forecast Period</h3>
              <p className="text-3xl font-bold mt-2">{formData.days}</p>
              <p className="text-xs opacity-75 mt-1">days ahead</p>
            </div>
          </div>

          {/* Inventory Metrics - Show if available */}
          {(forecastData.reorder_point || forecastData.safety_stock) && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {forecastData.reorder_point && (
                <div className="bg-white border-2 border-orange-200 rounded-lg p-4 shadow">
                  <h4 className="text-xs font-medium text-orange-600 mb-1">Reorder Point</h4>
                  <p className="text-2xl font-bold text-orange-700">{forecastData.reorder_point}</p>
                  <p className="text-xs text-gray-500 mt-1">units</p>
                </div>
              )}
              {forecastData.safety_stock && (
                <div className="bg-white border-2 border-blue-200 rounded-lg p-4 shadow">
                  <h4 className="text-xs font-medium text-blue-600 mb-1">Safety Stock</h4>
                  <p className="text-2xl font-bold text-blue-700">{forecastData.safety_stock}</p>
                  <p className="text-xs text-gray-500 mt-1">units</p>
                </div>
              )}
              {forecastData.minimum_level && (
                <div className="bg-white border-2 border-red-200 rounded-lg p-4 shadow">
                  <h4 className="text-xs font-medium text-red-600 mb-1">Minimum Level</h4>
                  <p className="text-2xl font-bold text-red-700">{forecastData.minimum_level}</p>
                  <p className="text-xs text-gray-500 mt-1">units</p>
                </div>
              )}
              {forecastData.maximum_level && (
                <div className="bg-white border-2 border-green-200 rounded-lg p-4 shadow">
                  <h4 className="text-xs font-medium text-green-600 mb-1">Maximum Level</h4>
                  <p className="text-2xl font-bold text-green-700">{forecastData.maximum_level}</p>
                  <p className="text-xs text-gray-500 mt-1">units</p>
                </div>
              )}
            </div>
          )}

          {/* Warnings - Show if available */}
          {forecastData.warnings && forecastData.warnings.length > 0 && (
            <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-bold text-yellow-800 mb-3 flex items-center">
                <AlertCircle className="mr-2" size={24} />
                Inventory Warnings & Recommendations
              </h3>
              <ul className="space-y-2">
                {forecastData.warnings.map((warning, index) => (
                  <li key={index} className="text-sm text-yellow-900 flex items-start">
                    <span className="text-yellow-600 font-bold mr-2">•</span>
                    <span>{warning}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Forecast Visualization</h3>
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={formatChartData()}>
                <defs>
                  <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="date" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="upper" 
                  stroke="#93c5fd" 
                  fill="#dbeafe" 
                  fillOpacity={0.3}
                  name="Upper Bound"
                />
                <Area 
                  type="monotone" 
                  dataKey="predicted" 
                  stroke="#3b82f6" 
                  fill="url(#colorPredicted)" 
                  name="Predicted Sales"
                />
                <Area 
                  type="monotone" 
                  dataKey="lower" 
                  stroke="#93c5fd" 
                  fill="#dbeafe" 
                  fillOpacity={0.3}
                  name="Lower Bound"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Forecast Table */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Detailed Forecast</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b-2 border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Date</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Predicted</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Lower Bound</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Upper Bound</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {forecastData.forecast?.map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-800">{item.ds}</td>
                      <td className="px-4 py-3 text-sm text-right font-semibold text-blue-600">
                        {Math.round(item.yhat)}
                      </td>
                      <td className="px-4 py-3 text-sm text-right text-gray-600">
                        {Math.round(item.yhat_lower)}
                      </td>
                      <td className="px-4 py-3 text-sm text-right text-gray-600">
                        {Math.round(item.yhat_upper)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* QR Scanner Modal */}
      {showQRScanner && (
        <QRScanner 
          onScan={handleQRScan}
          onClose={() => setShowQRScanner(false)}
        />
      )}
    </div>
  );
}
