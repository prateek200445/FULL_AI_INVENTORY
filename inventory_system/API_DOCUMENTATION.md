# 📡 Inventory Management API Documentation

**Base URL:** `http://localhost:5000`

---

## 🟢 HTTP REST API Endpoints

### 1. Health Check
**GET** `/health`

**Description:** Check if the server is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "inventory-management"
}
```

**Example:**
```powershell
curl http://localhost:5000/health
```

---

### 2. Get All Inventory
**GET** `/api/inventory`

**Description:** Retrieve all products in inventory.

**Response:**
```json
{
  "success": true,
  "inventory": [
    {"ProductID": "P001", "Quantity": 600},
    {"ProductID": "P002", "Quantity": 450}
  ],
  "count": 2
}
```

**Example:**
```powershell
curl http://localhost:5000/api/inventory
```

---

### 3. Get Specific Product
**GET** `/api/inventory/<product_id>`

**Description:** Get quantity for a specific product.

**Parameters:**
- `product_id` (path): Product identifier (e.g., P001)

**Response (Success):**
```json
{
  "success": true,
  "product_id": "P001",
  "quantity": 600
}
```

**Response (Not Found):**
```json
{
  "success": false,
  "message": "Product P999 not found"
}
```

**Example:**
```powershell
curl http://localhost:5000/api/inventory/P001
```

---

### 4. Update Stock (Add or Sell)
**POST** `/api/update_stock`

**Description:** Add or sell inventory for a product.

**Request Body:**
```json
{
  "product_id": "P001",
  "quantity": 50,
  "action": "add"  // "add" or "sell"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Added 50 units to P001",
  "new_quantity": 650,
  "product_id": "P001",
  "inventory": [
    {"ProductID": "P001", "Quantity": 650},
    {"ProductID": "P002", "Quantity": 450}
  ]
}
```

**Response (Insufficient Stock):**
```json
{
  "success": false,
  "message": "Insufficient stock. Available: 10, Requested: 50",
  "new_quantity": 10,
  "inventory": []
}
```

**Response (Product Not Found - Sell):**
```json
{
  "success": false,
  "message": "Product P999 not found in inventory",
  "new_quantity": 0,
  "inventory": []
}
```

**Validation Errors:**
- Missing fields: `{"success": false, "message": "Missing required fields: quantity"}`
- Invalid action: `{"success": false, "message": "Invalid action. Use 'add' or 'sell'"}`
- Invalid quantity: `{"success": false, "message": "Quantity must be greater than 0"}`

**Examples:**

**Add Stock:**
```powershell
curl -X POST http://localhost:5000/api/update_stock `
  -H "Content-Type: application/json" `
  -d '{\"product_id\": \"P001\", \"quantity\": 50, \"action\": \"add\"}'
```

**Sell Stock:**
```powershell
curl -X POST http://localhost:5000/api/update_stock `
  -H "Content-Type: application/json" `
  -d '{\"product_id\": \"P001\", \"quantity\": 20, \"action\": \"sell\"}'
```

**JavaScript (Axios):**
```javascript
import axios from 'axios';

axios.post('http://localhost:5000/api/update_stock', {
  product_id: 'P001',
  quantity: 50,
  action: 'add'
})
.then(response => console.log(response.data))
.catch(error => console.error(error.response.data));
```

---

### 5. Add New Product
**POST** `/api/add_product`

**Description:** Add a new product to inventory.

**Request Body:**
```json
{
  "product_id": "P010",
  "initial_quantity": 100
}
```

**Response:**
```json
{
  "success": true,
  "message": "Added 100 units to P010",
  "new_quantity": 100,
  "product_id": "P010",
  "inventory": [...]
}
```

**Example:**
```powershell
curl -X POST http://localhost:5000/api/add_product `
  -H "Content-Type: application/json" `
  -d '{\"product_id\": \"P010\", \"initial_quantity\": 100}'
```

---

### 6. Remove Product
**DELETE** `/api/remove_product/<product_id>`

**Description:** Completely remove a product from inventory.

**Parameters:**
- `product_id` (path): Product identifier

**Response (Success):**
```json
{
  "success": true,
  "message": "Product P010 removed from inventory",
  "inventory": [...]
}
```

**Response (Not Found):**
```json
{
  "success": false,
  "message": "Product P999 not found",
  "inventory": []
}
```

**Example:**
```powershell
curl -X DELETE http://localhost:5000/api/remove_product/P010
```

---

### 7. Forecast Demand (Stub)
**GET** `/api/forecast/<product_id>`

**Description:** Get demand forecast for a product (stub endpoint for future ML integration).

**Parameters:**
- `product_id` (path): Product identifier

**Response:**
```json
{
  "success": true,
  "product_id": "P001",
  "current_quantity": 600,
  "forecast": {
    "next_7_days": 45,
    "next_30_days": 180,
    "recommendation": "Stock level sufficient"
  },
  "note": "This is a stub endpoint. Integrate ML model for actual forecasting."
}
```

**Example:**
```powershell
curl http://localhost:5000/api/forecast/P001
```

---

## 🔵 WebSocket Events

### Connection Events

#### `connect`
**Direction:** Client → Server

**Description:** Fired when a client connects.

**Server Response:** Sends `initial_inventory` with current inventory data.

**JavaScript Example:**
```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected to server');
  socket.emit('join_inventory_room');
});
```

---

#### `disconnect`
**Direction:** Client → Server

**Description:** Fired when a client disconnects.

**JavaScript Example:**
```javascript
socket.on('disconnect', () => {
  console.log('Disconnected from server');
});
```

---

#### `join_inventory_room`
**Direction:** Client → Server

**Description:** Join the inventory updates room to receive broadcasts.

**JavaScript Example:**
```javascript
socket.emit('join_inventory_room');

socket.on('joined_room', (data) => {
  console.log('Joined room:', data.room);
});
```

---

### Data Events

#### `initial_inventory`
**Direction:** Server → Client

**Description:** Sent to a client when they first connect.

**Payload:**
```json
{
  "inventory": [
    {"ProductID": "P001", "Quantity": 600},
    {"ProductID": "P002", "Quantity": 450}
  ],
  "timestamp": null
}
```

**JavaScript Example:**
```javascript
socket.on('initial_inventory', (data) => {
  console.log('Received initial inventory:', data.inventory);
  setInventory(data.inventory);
});
```

---

#### `inventory_update`
**Direction:** Server → All Clients (Broadcast)

**Description:** Broadcasted to all clients when inventory changes.

**Payload:**
```json
{
  "product_id": "P001",
  "action": "add",
  "quantity": 50,
  "new_quantity": 650,
  "message": "Added 50 units to P001",
  "inventory": [
    {"ProductID": "P001", "Quantity": 650},
    {"ProductID": "P002", "Quantity": 450}
  ]
}
```

**Fields:**
- `product_id`: Product that was updated
- `action`: "add", "sell", or "remove"
- `quantity`: Amount added/sold
- `new_quantity`: Updated quantity for the product
- `message`: Human-readable description
- `inventory`: Full updated inventory array

**JavaScript Example:**
```javascript
socket.on('inventory_update', (data) => {
  console.log('Inventory updated:', data.message);
  setInventory(data.inventory);
  showNotification(data.message);
});
```

---

## 📋 Complete React Integration Example

```javascript
import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import axios from 'axios';

const BACKEND_URL = 'http://localhost:5000';

function InventoryApp() {
  const [socket, setSocket] = useState(null);
  const [inventory, setInventory] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  // Initialize WebSocket
  useEffect(() => {
    const newSocket = io(BACKEND_URL);
    setSocket(newSocket);

    // Connection handlers
    newSocket.on('connect', () => {
      setIsConnected(true);
      newSocket.emit('join_inventory_room');
    });

    newSocket.on('disconnect', () => {
      setIsConnected(false);
    });

    // Receive initial inventory
    newSocket.on('initial_inventory', (data) => {
      setInventory(data.inventory);
    });

    // Listen for real-time updates
    newSocket.on('inventory_update', (data) => {
      setInventory(data.inventory);
      alert(data.message);
    });

    return () => newSocket.close();
  }, []);

  // Add stock via HTTP
  const addStock = async (productId, quantity) => {
    try {
      const response = await axios.post(`${BACKEND_URL}/api/update_stock`, {
        product_id: productId,
        quantity: quantity,
        action: 'add'
      });
      console.log(response.data);
    } catch (error) {
      console.error(error.response.data);
    }
  };

  return (
    <div>
      <h1>Inventory: {isConnected ? 'Connected' : 'Disconnected'}</h1>
      <ul>
        {inventory.map(item => (
          <li key={item.ProductID}>
            {item.ProductID}: {item.Quantity}
          </li>
        ))}
      </ul>
      <button onClick={() => addStock('P001', 10)}>Add 10 to P001</button>
    </div>
  );
}
```

---

## 🔒 Error Codes

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad Request (validation error, insufficient stock) |
| 404 | Product Not Found |
| 500 | Internal Server Error |

---

## 🧪 Testing with PowerShell

### Get Inventory
```powershell
Invoke-RestMethod -Uri http://localhost:5000/api/inventory -Method GET
```

### Add Stock
```powershell
$body = @{
    product_id = "P001"
    quantity = 50
    action = "add"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5000/api/update_stock `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

### Sell Stock
```powershell
$body = @{
    product_id = "P001"
    quantity = 20
    action = "sell"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5000/api/update_stock `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

---

## 📊 Rate Limiting & Performance

- **No rate limiting implemented** (add if needed for production)
- **Thread-safe CSV operations** via `threading.Lock()`
- **WebSocket broadcast** to all connected clients (~5-10ms latency)
- **Concurrent requests supported** (Flask-SocketIO with eventlet)

---

## 🔐 Security Notes

⚠️ **This is a development system. For production:**
- Add JWT authentication for API endpoints
- Validate and sanitize all inputs
- Add rate limiting
- Use HTTPS (TLS/SSL)
- Implement proper CORS policies
- Use a real database (PostgreSQL, MongoDB) instead of CSV
- Add request logging and monitoring

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Health Check | `GET /health` |
| Get All Products | `GET /api/inventory` |
| Get One Product | `GET /api/inventory/<id>` |
| Add Stock | `POST /api/update_stock` (action: "add") |
| Sell Stock | `POST /api/update_stock` (action: "sell") |
| Add Product | `POST /api/add_product` |
| Remove Product | `DELETE /api/remove_product/<id>` |
| Forecast (Stub) | `GET /api/forecast/<id>` |

---

**For more details, see the main README.md**
