"""
Socket Events Module
Handles WebSocket event handlers for real-time inventory updates
"""
from flask_socketio import emit, join_room, leave_room
from flask import request

def register_socket_events(socketio):
    """Register all socket event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print(f"Client connected: {request.sid}")
        emit('connection_response', {'status': 'connected', 'sid': request.sid})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print(f"Client disconnected: {request.sid}")
    
    @socketio.on('join_inventory_room')
    def handle_join_inventory():
        """Join the inventory updates room"""
        join_room('inventory')
        print(f"Client {request.sid} joined inventory room")
        emit('joined_room', {'room': 'inventory'})
    
    @socketio.on('leave_inventory_room')
    def handle_leave_inventory():
        """Leave the inventory updates room"""
        leave_room('inventory')
        print(f"Client {request.sid} left inventory room")
        emit('left_room', {'room': 'inventory'})
    
    @socketio.on('request_inventory')
    def handle_request_inventory(data):
        """Client requests current inventory data"""
        # This will be handled by the main app to send current inventory
        print(f"Client {request.sid} requested inventory")
        emit('inventory_request', {'timestamp': data.get('timestamp', None)})

def broadcast_inventory_update(socketio, update_data):
    """
    Broadcast inventory update to all connected clients
    
    Args:
        socketio: SocketIO instance
        update_data: Dict with update information
            {
                'product_id': str,
                'action': str ('add' or 'sell'),
                'quantity': int,
                'new_quantity': int,
                'message': str,
                'inventory': list (full inventory data)
            }
    """
    socketio.emit('inventory_update', update_data, room='inventory', broadcast=True)
    print(f"Broadcasted inventory update: {update_data.get('message', 'Update')}")
