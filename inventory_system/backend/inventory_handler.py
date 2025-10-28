"""
Inventory Handler Module
Handles reading/writing to inventory.csv with thread-safe operations
"""
import pandas as pd
import threading
import os
from pathlib import Path
from typing import Dict, List, Optional

class InventoryHandler:
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.lock = threading.Lock()
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Create inventory CSV if it doesn't exist"""
        if not self.csv_path.exists():
            df = pd.DataFrame(columns=['ProductID', 'Quantity'])
            df.to_csv(self.csv_path, index=False)
    
    def get_inventory(self) -> List[Dict]:
        """
        Get all inventory data as list of dictionaries
        Thread-safe read operation
        """
        with self.lock:
            try:
                df = pd.read_csv(self.csv_path)
                return df.to_dict('records')
            except Exception as e:
                print(f"Error reading inventory: {e}")
                return []
    
    def get_product_quantity(self, product_id: str) -> Optional[int]:
        """
        Get quantity for a specific product
        Returns None if product not found
        """
        with self.lock:
            try:
                df = pd.read_csv(self.csv_path)
                product = df[df['ProductID'] == product_id]
                if not product.empty:
                    return int(product.iloc[0]['Quantity'])
                return None
            except Exception as e:
                print(f"Error getting product quantity: {e}")
                return None
    
    def update_stock(self, product_id: str, quantity: int, action: str) -> Dict:
        """
        Update stock for a product
        action: 'add' or 'sell'
        Returns: {'success': bool, 'message': str, 'new_quantity': int, 'inventory': list}
        """
        with self.lock:
            try:
                # Read current inventory
                df = pd.read_csv(self.csv_path)
                
                # Check if product exists
                product_exists = product_id in df['ProductID'].values
                
                if action == 'add':
                    if product_exists:
                        # Update existing product
                        df.loc[df['ProductID'] == product_id, 'Quantity'] += quantity
                    else:
                        # Add new product
                        new_row = pd.DataFrame({'ProductID': [product_id], 'Quantity': [quantity]})
                        df = pd.concat([df, new_row], ignore_index=True)
                    
                    new_quantity = int(df[df['ProductID'] == product_id].iloc[0]['Quantity'])
                    message = f"Added {quantity} units to {product_id}"
                
                elif action == 'sell':
                    if not product_exists:
                        return {
                            'success': False,
                            'message': f"Product {product_id} not found in inventory",
                            'new_quantity': 0,
                            'inventory': []
                        }
                    
                    current_qty = int(df[df['ProductID'] == product_id].iloc[0]['Quantity'])
                    
                    if current_qty < quantity:
                        return {
                            'success': False,
                            'message': f"Insufficient stock. Available: {current_qty}, Requested: {quantity}",
                            'new_quantity': current_qty,
                            'inventory': []
                        }
                    
                    df.loc[df['ProductID'] == product_id, 'Quantity'] -= quantity
                    new_quantity = int(df[df['ProductID'] == product_id].iloc[0]['Quantity'])
                    message = f"Sold {quantity} units of {product_id}"
                
                else:
                    return {
                        'success': False,
                        'message': f"Invalid action: {action}. Use 'add' or 'sell'",
                        'new_quantity': 0,
                        'inventory': []
                    }
                
                # Save updated inventory
                df.to_csv(self.csv_path, index=False)
                
                # Return success with updated inventory
                return {
                    'success': True,
                    'message': message,
                    'new_quantity': new_quantity,
                    'product_id': product_id,
                    'inventory': df.to_dict('records')
                }
            
            except Exception as e:
                return {
                    'success': False,
                    'message': f"Error updating stock: {str(e)}",
                    'new_quantity': 0,
                    'inventory': []
                }
    
    def add_product(self, product_id: str, initial_quantity: int = 0) -> Dict:
        """Add a new product to inventory"""
        return self.update_stock(product_id, initial_quantity, 'add')
    
    def remove_product(self, product_id: str) -> Dict:
        """Remove a product from inventory completely"""
        with self.lock:
            try:
                df = pd.read_csv(self.csv_path)
                
                if product_id not in df['ProductID'].values:
                    return {
                        'success': False,
                        'message': f"Product {product_id} not found",
                        'inventory': []
                    }
                
                df = df[df['ProductID'] != product_id]
                df.to_csv(self.csv_path, index=False)
                
                return {
                    'success': True,
                    'message': f"Product {product_id} removed from inventory",
                    'inventory': df.to_dict('records')
                }
            except Exception as e:
                return {
                    'success': False,
                    'message': f"Error removing product: {str(e)}",
                    'inventory': []
                }
