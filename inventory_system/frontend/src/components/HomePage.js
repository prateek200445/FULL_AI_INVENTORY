import React, { useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

function HomePage({ onStockUpdate }) {
  const [productId, setProductId] = useState('');
  const [quantity, setQuantity] = useState('');
  const [loading, setLoading] = useState(false);

  const handleUpdateStock = async (action) => {
    if (!productId.trim()) {
      alert('Please enter a Product ID');
      return;
    }

    if (!quantity || parseInt(quantity) <= 0) {
      alert('Please enter a valid quantity');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/update_stock`, {
        product_id: productId.trim().toUpperCase(),
        quantity: parseInt(quantity),
        action: action
      });

      if (response.data.success) {
        onStockUpdate({
          ...response.data,
          action: action
        });
        
        // Clear form on success
        setProductId('');
        setQuantity('');
      } else {
        onStockUpdate(response.data);
      }
    } catch (error) {
      console.error('Error updating stock:', error);
      onStockUpdate({
        success: false,
        message: error.response?.data?.message || 'Failed to update stock. Server error.'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleQRInput = (e) => {
    // Simulate QR code input - could integrate with actual QR scanner
    const value = e.target.value.toUpperCase();
    setProductId(value);
  };

  return (
    <div className="bg-white rounded-lg shadow-xl p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
        <span className="mr-3 text-3xl">🔍</span>
        Product Scanner
      </h2>

      {/* QR Code Input Section */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Product ID (QR Code)
        </label>
        <div className="relative">
          <input
            type="text"
            value={productId}
            onChange={handleQRInput}
            placeholder="Enter or scan Product ID (e.g., P001)"
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none transition-colors uppercase"
            disabled={loading}
          />
          <div className="absolute right-3 top-3 text-2xl">
            📱
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Tip: Use uppercase letters and numbers (e.g., P001, SKU123)
        </p>
      </div>

      {/* Quantity Input */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Quantity
        </label>
        <input
          type="number"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          placeholder="Enter quantity"
          min="1"
          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
          disabled={loading}
        />
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={() => handleUpdateStock('add')}
          disabled={loading}
          className="bg-gradient-to-r from-green-500 to-green-600 text-white py-4 rounded-lg font-semibold shadow-lg hover:from-green-600 hover:to-green-700 transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          <div className="flex items-center justify-center space-x-2">
            <span className="text-2xl">➕</span>
            <span>{loading ? 'Processing...' : 'Add Stock'}</span>
          </div>
        </button>

        <button
          onClick={() => handleUpdateStock('sell')}
          disabled={loading}
          className="bg-gradient-to-r from-red-500 to-red-600 text-white py-4 rounded-lg font-semibold shadow-lg hover:from-red-600 hover:to-red-700 transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          <div className="flex items-center justify-center space-x-2">
            <span className="text-2xl">➖</span>
            <span>{loading ? 'Processing...' : 'Sell Stock'}</span>
          </div>
        </button>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Quick Fill</h3>
        <div className="grid grid-cols-3 gap-2">
          {[10, 50, 100].map(value => (
            <button
              key={value}
              onClick={() => setQuantity(value.toString())}
              className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md text-sm font-medium transition-colors"
              disabled={loading}
            >
              {value}
            </button>
          ))}
        </div>
      </div>

      {/* Info Box */}
      <div className="mt-6 bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
        <div className="flex items-start">
          <span className="text-blue-500 text-xl mr-2">ℹ️</span>
          <div>
            <p className="text-sm text-blue-700 font-medium">Real-Time Updates</p>
            <p className="text-xs text-blue-600 mt-1">
              All changes are instantly broadcasted to connected clients via WebSocket
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
