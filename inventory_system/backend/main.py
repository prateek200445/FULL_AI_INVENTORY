"""
Flask-SocketIO Main Application
Real-time inventory management system with WebSocket support
"""
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import os
from dotenv import load_dotenv
from pathlib import Path

from inventory_handler import InventoryHandler
from socket_events import register_socket_events, broadcast_inventory_update

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    }
})

# Initialize SocketIO with CORS
socketio = SocketIO(app, cors_allowed_origins=os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','))

# Initialize inventory handler
INVENTORY_CSV_PATH = os.getenv('INVENTORY_CSV_PATH', 'inventory.csv')
inventory_handler = InventoryHandler(INVENTORY_CSV_PATH)

# Register WebSocket event handlers
register_socket_events(socketio)

# ==================== HTTP Routes ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'inventory-management'})

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    """Get all inventory data"""
    try:
        inventory = inventory_handler.get_inventory()
        return jsonify({
            'success': True,
            'inventory': inventory,
            'count': len(inventory)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error fetching inventory: {str(e)}"
        }), 500

@app.route('/api/inventory/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get specific product quantity"""
    try:
        quantity = inventory_handler.get_product_quantity(product_id)
        if quantity is not None:
            return jsonify({
                'success': True,
                'product_id': product_id,
                'quantity': quantity
            })
        else:
            return jsonify({
                'success': False,
                'message': f"Product {product_id} not found"
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error fetching product: {str(e)}"
        }), 500

@app.route('/api/update_stock', methods=['POST'])
def update_stock():
    """
    Update inventory stock
    Expected JSON body:
    {
        "product_id": "P001",
        "quantity": 10,
        "action": "add" or "sell"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['product_id', 'quantity', 'action']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        product_id = data['product_id'].strip().upper()
        quantity = int(data['quantity'])
        action = data['action'].lower()
        
        # Validate action
        if action not in ['add', 'sell']:
            return jsonify({
                'success': False,
                'message': "Invalid action. Use 'add' or 'sell'"
            }), 400
        
        # Validate quantity
        if quantity <= 0:
            return jsonify({
                'success': False,
                'message': "Quantity must be greater than 0"
            }), 400
        
        # Update stock
        result = inventory_handler.update_stock(product_id, quantity, action)
        
        # Broadcast update via WebSocket if successful
        if result['success']:
            update_data = {
                'product_id': product_id,
                'action': action,
                'quantity': quantity,
                'new_quantity': result['new_quantity'],
                'message': result['message'],
                'inventory': result['inventory']
            }
            broadcast_inventory_update(socketio, update_data)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f"Invalid data format: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error updating stock: {str(e)}"
        }), 500

@app.route('/api/add_product', methods=['POST'])
def add_product():
    """
    Add a new product to inventory
    Expected JSON body:
    {
        "product_id": "P001",
        "initial_quantity": 100
    }
    """
    try:
        data = request.get_json()
        
        if 'product_id' not in data:
            return jsonify({
                'success': False,
                'message': "Missing required field: product_id"
            }), 400
        
        product_id = data['product_id'].strip().upper()
        initial_quantity = int(data.get('initial_quantity', 0))
        
        result = inventory_handler.add_product(product_id, initial_quantity)
        
        if result['success']:
            update_data = {
                'product_id': product_id,
                'action': 'add',
                'quantity': initial_quantity,
                'new_quantity': result['new_quantity'],
                'message': result['message'],
                'inventory': result['inventory']
            }
            broadcast_inventory_update(socketio, update_data)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error adding product: {str(e)}"
        }), 500

@app.route('/api/remove_product/<product_id>', methods=['DELETE'])
def remove_product(product_id):
    """Remove a product from inventory"""
    try:
        product_id = product_id.strip().upper()
        result = inventory_handler.remove_product(product_id)
        
        if result['success']:
            update_data = {
                'product_id': product_id,
                'action': 'remove',
                'quantity': 0,
                'new_quantity': 0,
                'message': result['message'],
                'inventory': result['inventory']
            }
            broadcast_inventory_update(socketio, update_data)
        
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error removing product: {str(e)}"
        }), 500

@app.route('/api/forecast/<product_id>', methods=['GET'])
def forecast_demand(product_id):
    """
    Stub endpoint for future ML integration
    Returns dummy forecast data
    """
    try:
        product_id = product_id.strip().upper()
        
        # Check if product exists
        quantity = inventory_handler.get_product_quantity(product_id)
        if quantity is None:
            return jsonify({
                'success': False,
                'message': f"Product {product_id} not found"
            }), 404
        
        # Dummy forecast data (replace with actual ML model later)
        forecast_data = {
            'success': True,
            'product_id': product_id,
            'current_quantity': quantity,
            'forecast': {
                'next_7_days': 45,  # Dummy value
                'next_30_days': 180,  # Dummy value
                'recommendation': 'Restock recommended' if quantity < 200 else 'Stock level sufficient'
            },
            'note': 'This is a stub endpoint. Integrate ML model for actual forecasting.'
        }
        
        return jsonify(forecast_data)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error forecasting demand: {str(e)}"
        }), 500

# ==================== WebSocket Event (broadcast on connect) ====================

@socketio.on('connect')
def handle_initial_connection():
    """Send current inventory to newly connected client"""
    try:
        inventory = inventory_handler.get_inventory()
        socketio.emit('initial_inventory', {
            'inventory': inventory,
            'timestamp': None
        }, room=request.sid)
    except Exception as e:
        print(f"Error sending initial inventory: {e}")

# ==================== Run Server ====================

if __name__ == '__main__':
    PORT = int(os.getenv('FLASK_PORT', 5000))
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Flask-SocketIO server on port {PORT}")
    print(f"CORS enabled for: {os.getenv('CORS_ORIGINS', 'http://localhost:3000')}")
    print(f"Inventory CSV: {INVENTORY_CSV_PATH}")
    
    socketio.run(app, host='0.0.0.0', port=PORT, debug=DEBUG)
