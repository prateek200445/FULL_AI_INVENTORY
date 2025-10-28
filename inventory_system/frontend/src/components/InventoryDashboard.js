import React, { useState, useEffect } from 'react';

function InventoryDashboard({ inventory }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('productId');
  const [sortOrder, setSortOrder] = useState('asc');
  const [filteredInventory, setFilteredInventory] = useState([]);

  useEffect(() => {
    let result = [...inventory];

    // Apply search filter
    if (searchTerm) {
      result = result.filter(item =>
        item.ProductID.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply sorting
    result.sort((a, b) => {
      const aValue = sortBy === 'productId' ? a.ProductID : a.Quantity;
      const bValue = sortBy === 'productId' ? b.ProductID : b.Quantity;

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredInventory(result);
  }, [inventory, searchTerm, sortBy, sortOrder]);

  const toggleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const getStockStatus = (quantity) => {
    if (quantity === 0) return { label: 'Out of Stock', color: 'bg-red-500', textColor: 'text-red-700' };
    if (quantity < 100) return { label: 'Low Stock', color: 'bg-yellow-500', textColor: 'text-yellow-700' };
    if (quantity < 300) return { label: 'Medium', color: 'bg-blue-500', textColor: 'text-blue-700' };
    return { label: 'In Stock', color: 'bg-green-500', textColor: 'text-green-700' };
  };

  const totalProducts = inventory.length;
  const totalQuantity = inventory.reduce((sum, item) => sum + item.Quantity, 0);
  const lowStockCount = inventory.filter(item => item.Quantity < 100 && item.Quantity > 0).length;
  const outOfStockCount = inventory.filter(item => item.Quantity === 0).length;

  return (
    <div className="bg-white rounded-lg shadow-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center">
          <span className="mr-3 text-3xl">📊</span>
          Live Inventory Dashboard
        </h2>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-sm font-medium text-gray-600">Live Updates</span>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg p-4 shadow-md">
          <p className="text-sm opacity-90">Total Products</p>
          <p className="text-3xl font-bold mt-1">{totalProducts}</p>
        </div>
        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg p-4 shadow-md">
          <p className="text-sm opacity-90">Total Quantity</p>
          <p className="text-3xl font-bold mt-1">{totalQuantity.toLocaleString()}</p>
        </div>
        <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white rounded-lg p-4 shadow-md">
          <p className="text-sm opacity-90">Low Stock</p>
          <p className="text-3xl font-bold mt-1">{lowStockCount}</p>
        </div>
        <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-lg p-4 shadow-md">
          <p className="text-sm opacity-90">Out of Stock</p>
          <p className="text-3xl font-bold mt-1">{outOfStockCount}</p>
        </div>
      </div>

      {/* Search and Sort Controls */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div className="flex-1">
          <input
            type="text"
            placeholder="🔍 Search by Product ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
          />
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Sort by:</span>
          <button
            onClick={() => toggleSort('productId')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              sortBy === 'productId'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Product ID {sortBy === 'productId' && (sortOrder === 'asc' ? '↑' : '↓')}
          </button>
          <button
            onClick={() => toggleSort('quantity')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              sortBy === 'quantity'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Quantity {sortBy === 'quantity' && (sortOrder === 'asc' ? '↑' : '↓')}
          </button>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="w-full">
          <thead className="bg-gray-50 border-b-2 border-gray-200">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                Product ID
              </th>
              <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700">
                Quantity
              </th>
              <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700">
                Status
              </th>
              <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700">
                Stock Level
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredInventory.length === 0 ? (
              <tr>
                <td colSpan="4" className="px-6 py-12 text-center">
                  <div className="text-gray-400">
                    <p className="text-4xl mb-2">📦</p>
                    <p className="text-lg font-medium">No products found</p>
                    <p className="text-sm mt-1">
                      {searchTerm
                        ? 'Try adjusting your search'
                        : 'Add products to get started'}
                    </p>
                  </div>
                </td>
              </tr>
            ) : (
              filteredInventory.map((item, index) => {
                const status = getStockStatus(item.Quantity);
                const percentage = Math.min((item.Quantity / 500) * 100, 100);
                
                return (
                  <tr
                    key={item.ProductID || index}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <span className="font-mono font-semibold text-gray-800">
                        {item.ProductID}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className={`font-bold text-lg ${status.textColor}`}>
                        {item.Quantity.toLocaleString()}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium text-white ${status.color}`}>
                        {status.label}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div
                          className={`h-2.5 rounded-full transition-all ${status.color}`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Footer Info */}
      <div className="mt-6 flex items-center justify-between text-sm text-gray-600">
        <p>
          Showing <span className="font-semibold">{filteredInventory.length}</span> of{' '}
          <span className="font-semibold">{totalProducts}</span> products
        </p>
        <p className="text-xs">
          Last updated: {new Date().toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}

export default InventoryDashboard;
