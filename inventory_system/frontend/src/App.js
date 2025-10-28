import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import HomePage from './components/HomePage';
import InventoryDashboard from './components/InventoryDashboard';
import './App.css';

const SOCKET_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

function App() {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [inventory, setInventory] = useState([]);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    // Initialize Socket.IO connection
    const newSocket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    });

    setSocket(newSocket);

    // Connection event handlers
    newSocket.on('connect', () => {
      console.log('Connected to server');
      setIsConnected(true);
      newSocket.emit('join_inventory_room');
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server');
      setIsConnected(false);
    });

    newSocket.on('connection_response', (data) => {
      console.log('Connection response:', data);
    });

    // Receive initial inventory on connect
    newSocket.on('initial_inventory', (data) => {
      console.log('Received initial inventory:', data.inventory);
      setInventory(data.inventory);
    });

    // Listen for real-time inventory updates
    newSocket.on('inventory_update', (data) => {
      console.log('Inventory update:', data);
      setInventory(data.inventory);
      
      // Show notification
      showNotification(data.message, data.action === 'sell' ? 'warning' : 'success');
    });

    // Cleanup on unmount
    return () => {
      newSocket.close();
    };
  }, []);

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000); // Auto-hide after 5 seconds
  };

  const handleStockUpdate = (result) => {
    if (result.success) {
      showNotification(result.message, result.action === 'sell' ? 'warning' : 'success');
    } else {
      showNotification(result.message, 'error');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold">📦 Real-Time Inventory Management</h1>
            <div className="flex items-center space-x-4">
              <div className={`flex items-center px-4 py-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`}>
                <div className={`w-3 h-3 rounded-full mr-2 ${
                  isConnected ? 'bg-white animate-pulse' : 'bg-gray-300'
                }`}></div>
                <span className="text-sm font-medium">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Notification Toast */}
      {notification && (
        <div className="fixed top-20 right-4 z-50 animate-slide-in">
          <div className={`px-6 py-4 rounded-lg shadow-lg text-white ${
            notification.type === 'success' ? 'bg-green-500' :
            notification.type === 'warning' ? 'bg-yellow-500' :
            notification.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
          }`}>
            <div className="flex items-center space-x-3">
              <span className="text-2xl">
                {notification.type === 'success' ? '✓' :
                 notification.type === 'warning' ? '⚠' :
                 notification.type === 'error' ? '✕' : 'ℹ'}
              </span>
              <p className="font-medium">{notification.message}</p>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - QR Input & Actions */}
          <div className="lg:col-span-1">
            <HomePage onStockUpdate={handleStockUpdate} />
          </div>

          {/* Right Panel - Inventory Dashboard */}
          <div className="lg:col-span-2">
            <InventoryDashboard inventory={inventory} />
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white mt-12">
        <div className="container mx-auto px-4 py-6 text-center">
          <p className="text-sm">
            Real-Time Inventory Management System | WebSocket-Powered | 
            <span className="ml-2">Total Products: {inventory.length}</span>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
