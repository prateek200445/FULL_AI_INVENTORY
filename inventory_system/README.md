# Real-Time Inventory Management System

A full-stack real-time inventory management system with **QR code scanning**, **WebSocket broadcasting**, and **React frontend**. Built with Flask-SocketIO backend and React + TailwindCSS frontend.

---

## 🚀 Features

### Backend (Flask-SocketIO)
- ✅ **RESTful API** for inventory management (Add, Sell, Get)
- ✅ **WebSocket real-time broadcasting** - All clients receive instant updates
- ✅ **Thread-safe CSV operations** using `threading.Lock()`
- ✅ **CORS enabled** for cross-origin requests
- ✅ **Modular architecture** (main.py, inventory_handler.py, socket_events.py)
- ✅ **Stub forecast endpoint** for future ML integration

### Frontend (React + TailwindCSS)
- ✅ **QR code input simulation** (Product ID scanning)
- ✅ **Real-time dashboard** with live inventory updates
- ✅ **Add/Sell stock buttons** with instant feedback
- ✅ **WebSocket integration** (Socket.IO client)
- ✅ **Search & Sort** functionality
- ✅ **Stock status indicators** (In Stock, Low Stock, Out of Stock)
- ✅ **Responsive design** with Tailwind CSS
- ✅ **Toast notifications** for user feedback

---

## 📁 Project Structure

```
inventory_system/
│
├── backend/                     # Flask-SocketIO Backend
│   ├── main.py                  # Flask app with SocketIO
│   ├── inventory_handler.py     # Thread-safe CSV operations
│   ├── socket_events.py         # WebSocket event handlers
│   ├── inventory.csv            # CSV database (ProductID, Quantity)
│   ├── .env                     # Environment variables
│   └── requirements.txt         # Python dependencies
│
├── frontend/                    # React Frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── HomePage.js      # QR input & Add/Sell buttons
│   │   │   └── InventoryDashboard.js  # Real-time inventory table
│   │   ├── App.js               # Main app with Socket.IO
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   └── tailwind.config.js
│
└── README.md                    # This file
```

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** and npm
- **Git** (optional)

---

### Backend Setup

1. **Navigate to backend folder:**
   ```powershell
   cd d:\model_shardha\inventory_system\backend
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment variables** (`.env` already created):
   ```env
   FLASK_PORT=5000
   FLASK_DEBUG=True
   INVENTORY_CSV_PATH=inventory.csv
   SECRET_KEY=your-secret-key-here
   CORS_ORIGINS=http://localhost:3000
   ```

5. **Run the Flask-SocketIO server:**
   ```powershell
   python main.py
   ```

   **Expected output:**
   ```
   Starting Flask-SocketIO server on port 5000
   CORS enabled for: http://localhost:3000
   Inventory CSV: inventory.csv
    * Running on http://0.0.0.0:5000
   ```

---

### Frontend Setup

1. **Navigate to frontend folder:**
   ```powershell
   cd d:\model_shardha\inventory_system\frontend
   ```

2. **Install dependencies:**
   ```powershell
   npm install
   ```

3. **Create `.env` file (optional):**
   ```env
   REACT_APP_BACKEND_URL=http://localhost:5000
   ```

4. **Run the React development server:**
   ```powershell
   npm start
   ```

   **Expected output:**
   ```
   Compiled successfully!
   You can now view inventory-frontend in the browser.
   
   Local:            http://localhost:3000
   On Your Network:  http://192.168.x.x:3000
   ```

---

## 📡 API Endpoints

### HTTP REST API

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `GET` | `/health` | Health check | - |
| `GET` | `/api/inventory` | Get all inventory | - |
| `GET` | `/api/inventory/<product_id>` | Get specific product | - |
| `POST` | `/api/update_stock` | Add or sell stock | `{"product_id": "P001", "quantity": 10, "action": "add"}` |
| `POST` | `/api/add_product` | Add new product | `{"product_id": "P001", "initial_quantity": 100}` |
| `DELETE` | `/api/remove_product/<product_id>` | Remove product | - |
| `GET` | `/api/forecast/<product_id>` | Forecast demand (stub) | - |

### WebSocket Events

| Event | Direction | Description | Payload |
|-------|-----------|-------------|---------|
| `connect` | Client → Server | Client connects | - |
| `disconnect` | Client → Server | Client disconnects | - |
| `join_inventory_room` | Client → Server | Join updates room | - |
| `initial_inventory` | Server → Client | Send current inventory on connect | `{"inventory": [...]}` |
| `inventory_update` | Server → All Clients | Broadcast stock update | `{"product_id": "P001", "action": "add", "quantity": 10, ...}` |

---

## 🔄 WebSocket Flow

```
┌─────────────┐                ┌─────────────┐                ┌─────────────┐
│  Client 1   │                │   Server    │                │  Client 2   │
└─────────────┘                └─────────────┘                └─────────────┘
       │                              │                              │
       │─────── connect ──────────────>│                              │
       │<────── initial_inventory ─────│                              │
       │                              │                              │
       │─── POST /api/update_stock ───>│                              │
       │                              │                              │
       │<────── HTTP Response ─────────│                              │
       │                              │                              │
       │                              │────── inventory_update ──────>│
       │<────── inventory_update ──────│                              │
       │                              │                              │
```

**Key Flow:**
1. Client connects → receives `initial_inventory`
2. Client calls `POST /api/update_stock` (HTTP)
3. Server updates `inventory.csv` (thread-safe with lock)
4. Server broadcasts `inventory_update` via WebSocket to **all connected clients**
5. All clients receive real-time update and refresh UI

---

## 🧪 Testing the System

### 1. Test Backend (using curl or Postman)

**Health check:**
```powershell
curl http://localhost:5000/health
```

**Get inventory:**
```powershell
curl http://localhost:5000/api/inventory
```

**Add stock:**
```powershell
curl -X POST http://localhost:5000/api/update_stock `
  -H "Content-Type: application/json" `
  -d '{\"product_id\": \"P001\", \"quantity\": 50, \"action\": \"add\"}'
```

**Sell stock:**
```powershell
curl -X POST http://localhost:5000/api/update_stock `
  -H "Content-Type: application/json" `
  -d '{\"product_id\": \"P001\", \"quantity\": 20, \"action\": \"sell\"}'
```

### 2. Test Frontend

1. Open **http://localhost:3000** in your browser
2. Enter a Product ID (e.g., `P001`)
3. Enter quantity (e.g., `100`)
4. Click **Add Stock** or **Sell Stock**
5. Watch the dashboard update in **real-time**

### 3. Test Real-Time Broadcasting

1. Open **http://localhost:3000** in **TWO browser tabs**
2. In Tab 1: Add stock to `P001`
3. **Observe**: Tab 2 updates **instantly** without refresh

---

## 🔧 Configuration

### Backend Environment Variables (`.env`)

```env
FLASK_PORT=5000                  # Backend port
FLASK_DEBUG=True                 # Enable debug mode
INVENTORY_CSV_PATH=inventory.csv # CSV file path
SECRET_KEY=your-secret-key       # Flask secret key
CORS_ORIGINS=http://localhost:3000  # Allowed origins (comma-separated)
```

### Frontend Environment Variables (optional `.env`)

```env
REACT_APP_BACKEND_URL=http://localhost:5000  # Backend URL
```

---

## 📊 Sample CSV Format (`inventory.csv`)

```csv
ProductID,Quantity
P001,600
P002,450
P003,300
P004,250
P005,180
```

---

## 🧩 Architecture Highlights

### Thread-Safe CSV Operations
```python
class InventoryHandler:
    def __init__(self, csv_path: str):
        self.lock = threading.Lock()  # Thread-safe lock
    
    def update_stock(self, product_id, quantity, action):
        with self.lock:  # Acquire lock before file operations
            df = pd.read_csv(self.csv_path)
            # ... update logic ...
            df.to_csv(self.csv_path, index=False)
```

### WebSocket Broadcasting
```python
# In main.py
result = inventory_handler.update_stock(product_id, quantity, action)
if result['success']:
    broadcast_inventory_update(socketio, update_data)  # Broadcast to all clients
```

### React Real-Time Hook
```javascript
// In App.js
useEffect(() => {
    const socket = io('http://localhost:5000');
    
    socket.on('inventory_update', (data) => {
        setInventory(data.inventory);  // Update state
        showNotification(data.message);  // Show toast
    });
    
    return () => socket.close();
}, []);
```

---

## 🚧 Future Enhancements

- [ ] **ML Forecast Integration** - Replace stub `/api/forecast/<product_id>` with Prophet/LSTM model
- [ ] **Actual QR Code Scanner** - Integrate QR camera library
- [ ] **User Authentication** - Add login/JWT tokens
- [ ] **Database Migration** - Move from CSV to PostgreSQL/MongoDB
- [ ] **Product Details** - Add name, price, category fields
- [ ] **Barcode Support** - Support both QR and barcode formats
- [ ] **Export Reports** - Generate PDF/Excel inventory reports
- [ ] **Docker Deployment** - Containerize with Docker Compose

---

## 🐛 Troubleshooting

### Backend Issues

**Error: "Port 5000 already in use"**
```powershell
# Kill process on port 5000
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force
```

**Error: "pandas not found"**
```powershell
pip install -r requirements.txt
```

### Frontend Issues

**Error: "Module not found: Can't resolve 'socket.io-client'"**
```powershell
npm install socket.io-client axios
```

**Error: "Tailwind styles not loading"**
```powershell
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init
```

### WebSocket Connection Issues

**Error: "WebSocket connection failed"**
- Ensure backend is running on `http://localhost:5000`
- Check CORS settings in `.env`
- Verify firewall isn't blocking port 5000

---

## 📝 License

MIT License - Feel free to use and modify for your projects.

---

## 👨‍💻 Contributors

Built with ❤️ for real-time inventory management.

---

## 📞 Support

For issues or questions:
1. Check the **Troubleshooting** section
2. Review backend/frontend logs
3. Ensure all dependencies are installed
4. Verify `.env` configuration

---

## 🎯 Quick Start Summary

```powershell
# Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm start

# Open http://localhost:3000 and test!
```

---

**Happy Coding! 🚀**
