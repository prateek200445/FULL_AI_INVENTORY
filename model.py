# model.py
import os
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
from prophet import Prophet
import logging
import json
from pathlib import Path
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import threading
import queue as _queue

# Configure logging
logging.getLogger('prophet').setLevel(logging.ERROR)  # Reduce Prophet debugging output

# Configure logging only
logging.getLogger('prophet').setLevel(logging.ERROR)  # Reduce Prophet debugging output

# Constants and storage paths
DATA_PATH = Path("large_dataset.csv")
UPLOADS_DIR = Path("uploads")
LSTM_WEIGHTS_PATH = Path("lstm_model_retrained.h5")
LSTM_SCALER_PATH = Path("lstm_scaler.pkl")
PROPHET_MODEL_PATH = Path("prophet_model.pkl")
MODEL_META = Path("model_meta.json")

# Ensure uploads dir exists
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Load your dataset (existence assumed)
if DATA_PATH.exists():
    df = pd.read_csv(DATA_PATH)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')  # Ensure data is sorted by date
else:
    # Start empty DataFrame with expected columns if dataset doesn't exist
    df = pd.DataFrame(columns=['date','sales','product_id','category','region','rating','price','discount'])

# Global cached model (set after retraining)
GLOBAL_MODEL = None

class LSTMModel:
    def __init__(self, sequence_length=10):
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.sequence_length = sequence_length
        
    def create_sequences(self, data):
        X = []
        y = []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:(i + self.sequence_length)])
            y.append(data[i + self.sequence_length])
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        model = Sequential([
            LSTM(50, activation='relu', input_shape=input_shape, return_sequences=True),
            Dropout(0.2),
            LSTM(50, activation='relu'),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model
    
    def train(self, data, progress_callback=None):
        """Train LSTM model. If progress_callback is provided, delegate to train_with_progress."""
        if progress_callback is not None:
            # Use progress-enabled training
            self.train_with_progress(data, progress_callback=progress_callback, epochs=50, batch_size=32)
        else:
            # Scale the data
            scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))

            # Create sequences
            X, y = self.create_sequences(scaled_data)

            # Build and train model
            self.model = self.build_model((self.sequence_length, 1))
            # Default train without progress (kept for backward compatibility)
            self.model.fit(X, y, epochs=50, batch_size=32, verbose=0)

    def train_with_progress(self, data, progress_callback=None, epochs=50, batch_size=32, fine_tune=False):
        """Train with a Keras callback that reports progress via progress_callback(message).

        progress_callback receives strings describing progress.
        fine_tune: if True, reuse existing model weights; if False, rebuild model from scratch.
        """
        # Validate minimum data size for LSTM
        if len(data) < self.sequence_length + 1:
            error_msg = f"⚠️ Insufficient data for LSTM training. Need at least {self.sequence_length + 1} data points, got {len(data)}."
            if progress_callback:
                progress_callback(error_msg)
                progress_callback("⚠️ Skipping LSTM training, will use Prophet only.")
            # Don't train LSTM if insufficient data
            return
        
        # Scale data and create sequences (reuse same scaler)
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))
        X, y = self.create_sequences(scaled_data)
        
        # Validate we have enough sequences
        if len(X) == 0:
            if progress_callback:
                progress_callback("⚠️ No sequences created, skipping LSTM training.")
            return

        # Build or load model
        if fine_tune:
            # Try to load existing model weights for fine-tuning
            if self.model is None:
                # Attempt to load from disk if not already in memory
                if LSTM_WEIGHTS_PATH.exists():
                    try:
                        if progress_callback:
                            progress_callback("Loading existing LSTM model for fine-tuning...")
                        self.load(LSTM_WEIGHTS_PATH, LSTM_SCALER_PATH)
                        if progress_callback:
                            progress_callback("✅ Existing model loaded, continuing training...")
                    except Exception as e:
                        if progress_callback:
                            progress_callback(f"⚠️ Could not load existing model ({e}), building new model...")
                        self.model = self.build_model((self.sequence_length, 1))
                else:
                    if progress_callback:
                        progress_callback("⚠️ No existing model found, building new model...")
                    self.model = self.build_model((self.sequence_length, 1))
            else:
                # Model already exists in memory - fine-tune it
                if progress_callback:
                    progress_callback("Fine-tuning existing model in memory...")
        else:
            # Full retrain - rebuild model from scratch
            if progress_callback:
                progress_callback("Building new LSTM model from scratch...")
            self.model = self.build_model((self.sequence_length, 1))

        # Create Keras callback to report epoch progress
        callbacks = []
        if progress_callback:
            def on_epoch_end(epoch, logs):
                try:
                    progress_callback(f"LSTM epoch {epoch+1}/{epochs} - loss={logs.get('loss'):.4f}")
                except Exception:
                    # ignore any callback exceptions
                    pass

            callbacks.append(tf.keras.callbacks.LambdaCallback(on_epoch_end=on_epoch_end))

        # Fit model with callbacks
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0, callbacks=callbacks)
        
        # Save the updated model after training
        if fine_tune:
            try:
                self.save(LSTM_WEIGHTS_PATH, LSTM_SCALER_PATH)
                if progress_callback:
                    progress_callback("✅ Fine-tuned model saved successfully")
            except Exception as e:
                if progress_callback:
                    progress_callback(f"⚠️ Failed to save fine-tuned model: {e}")
        
    def predict(self, data, future_steps):
        # Scale the data
        scaled_data = self.scaler.transform(data.reshape(-1, 1))
        
        # Get the last sequence
        last_sequence = scaled_data[-self.sequence_length:]
        
        # Make predictions
        predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(future_steps):
            # Reshape for prediction
            current_input = current_sequence.reshape(1, self.sequence_length, 1)
            # Get prediction
            next_pred = self.model.predict(current_input, verbose=0)
            # Add to predictions
            predictions.append(next_pred[0, 0])
            # Update sequence
            current_sequence = np.roll(current_sequence, -1)
            current_sequence[-1] = next_pred
            
        # Inverse transform predictions
        predictions = np.array(predictions).reshape(-1, 1)
        predictions = self.scaler.inverse_transform(predictions)
        
        return predictions.flatten()

    def save(self, weights_path: Path, scaler_path: Path):
        """Save LSTM weights and scaler to disk."""
        if self.model is not None:
            # Save Keras model weights
            self.model.save(str(weights_path))
        # Save scaler
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)

    def load(self, weights_path: Path, scaler_path: Path):
        """Load LSTM weights and scaler from disk (rebuilds model architecture)."""
        # Rebuild model architecture
        self.model = self.build_model((self.sequence_length, 1))
        # Load weights if available
        if weights_path.exists():
            try:
                self.model.load_weights(str(weights_path))
            except Exception:
                # fallback: try loading as entire model
                try:
                    self.model = tf.keras.models.load_model(str(weights_path))
                except Exception:
                    pass
        # Load scaler
        if scaler_path.exists():
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)

class InventoryForecastModel:
    def __init__(self):
        self.prophet_model = None
        self.lstm_model = LSTMModel()
        self.last_training_date = None
        
    def prepare_data(self, filtered_df):
        # Prophet requires columns named 'ds' and 'y'
        prophet_df = filtered_df.groupby('date')['sales'].sum().reset_index()
        prophet_df.columns = ['ds', 'y']
        return prophet_df
        
    def train(self, data, progress_callback=None, fine_tune=False):
        # Train Prophet model
        if progress_callback:
            progress_callback('Starting Prophet training...')

        self.prophet_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True,
            seasonality_mode='multiplicative',
            interval_width=0.95,  # 95% confidence interval
            changepoint_prior_scale=0.05  # Makes trend more flexible
        )
        self.prophet_model.fit(data)

        if progress_callback:
            progress_callback('Prophet training complete')

        # Train LSTM model with fine-tuning option
        sales_data = data['y'].values
        if progress_callback:
            mode = "Fine-tuning" if fine_tune else "Training"
            progress_callback(f'Starting LSTM {mode.lower()}...')
        
        # Use train_with_progress with fine_tune parameter
        self.lstm_model.train_with_progress(
            sales_data, 
            progress_callback=progress_callback,
            epochs=50,
            batch_size=32,
            fine_tune=fine_tune
        )

        if progress_callback:
            mode = "fine-tuning" if fine_tune else "training"
            progress_callback(f'LSTM {mode} complete')

        self.last_training_date = data['ds'].max()

    def save(self, prophet_path: Path, lstm_weights_path: Path, lstm_scaler_path: Path):
        """Save Prophet model, LSTM weights and scaler to disk."""
        # Save Prophet model using pickle
        if self.prophet_model is not None:
            with open(prophet_path, 'wb') as f:
                pickle.dump(self.prophet_model, f)
        
        # Save LSTM artifacts
        self.lstm_model.save(lstm_weights_path, lstm_scaler_path)

    def load(self, prophet_path: Path, lstm_weights_path: Path, lstm_scaler_path: Path):
        """Load Prophet model, LSTM weights and scaler from disk."""
        # Load Prophet model
        if prophet_path.exists():
            with open(prophet_path, 'rb') as f:
                self.prophet_model = pickle.load(f)
                # Extract last training date from Prophet model's history
                if hasattr(self.prophet_model, 'history') and self.prophet_model.history is not None:
                    self.last_training_date = self.prophet_model.history['ds'].max()
        
        # Load LSTM artifacts
        self.lstm_model.load(lstm_weights_path, lstm_scaler_path)

# Main forecasting function
def forecast(days=7, product_id=None, category=None, region=None, 
            min_rating=None, max_price=None, min_discount=None):
    # Apply filters to get relevant data
    filtered_df = df.copy()
    
    if product_id:
        filtered_df = filtered_df[filtered_df['product_id'] == product_id]
    if category:
        filtered_df = filtered_df[filtered_df['category'] == category]
    if region:
        filtered_df = filtered_df[filtered_df['region'] == region]
    if min_rating is not None:
        filtered_df = filtered_df[filtered_df['rating'] >= min_rating]
    if max_price is not None:
        filtered_df = filtered_df[filtered_df['price'] <= max_price]
    if min_discount is not None:
        filtered_df = filtered_df[filtered_df['discount'] >= min_discount]
        
    # Check if we have data after filtering
    if filtered_df.empty:
        return {
            "error": "No data found matching the specified criteria",
            "Reorder Point": 0,
            "Safety Stock": 0,
            "Minimum Level": 0,
            "Maximum Level": 0,
            "Forecast": {},
            "Warnings": ["⚠️ No historical data available for the specified filters"]
        }
    # If there are no filters and a global retrained model exists, use it directly
    filters_present = any([product_id, category, region, min_rating is not None, max_price is not None, min_discount is not None])

    if not filters_present and GLOBAL_MODEL is not None:
        # Use the global model trained on the combined dataset
        prophet_forecast = GLOBAL_MODEL.prophet_model.predict(GLOBAL_MODEL.prophet_model.make_future_dataframe(periods=int(days), freq='D'))
        # Aggregate sales from the full dataframe for LSTM input
        agg = df.groupby('date')['sales'].sum().reset_index()
        sales_data = agg['sales'].values
        
        # Check if LSTM model was trained (might be skipped if insufficient data)
        if GLOBAL_MODEL.lstm_model.model is not None and len(sales_data) >= GLOBAL_MODEL.lstm_model.sequence_length:
            lstm_forecast = GLOBAL_MODEL.lstm_model.predict(sales_data, days)
        else:
            # Use Prophet only if LSTM wasn't trained
            lstm_forecast = prophet_forecast['yhat'].tail(days).values
    else:
        # Initialize and train Prophet model on the filtered data
        model = InventoryForecastModel()
        prophet_data = filtered_df.groupby('date')['sales'].sum().reset_index()
        prophet_data.columns = ['ds', 'y']

        model.train(prophet_data)
        # Get Prophet forecast
        prophet_forecast = model.prophet_model.predict(model.prophet_model.make_future_dataframe(periods=int(days), freq='D'))

        # Get LSTM forecast (check if model was trained)
        sales_data = prophet_data['y'].values
        if model.lstm_model.model is not None and len(sales_data) >= model.lstm_model.sequence_length:
            lstm_forecast = model.lstm_model.predict(sales_data, days)
        else:
            # Use Prophet only if LSTM wasn't trained
            lstm_forecast = prophet_forecast['yhat'].tail(days).values
    
    # Combine forecasts (simple average)
    future_dates = prophet_forecast['ds'].tail(days)
    prophet_values = prophet_forecast['yhat'].tail(days).values
    
    # Combine predictions (weighted average: 0.6 Prophet, 0.4 LSTM)
    forecast_values = 0.6 * prophet_values + 0.4 * lstm_forecast
    
    # Use Prophet's uncertainty intervals
    forecast_lower = prophet_forecast['yhat_lower'].tail(days)
    forecast_upper = prophet_forecast['yhat_upper'].tail(days)

    # Calculate inventory parameters using Prophet's predictions
    avg_daily_demand = forecast_values.mean()
    std_daily_demand = forecast_values.std()
    
    lead_time = 5  # assumed lead time in days
    service_level = 0.95  # 95% service level
    z_score = 1.645  # z-score for 95% service level
    
    safety_stock = int(z_score * std_daily_demand * np.sqrt(lead_time))
    reorder_point = int(avg_daily_demand * lead_time + safety_stock)
    min_level = safety_stock
    max_level = reorder_point + int(avg_daily_demand * 2)

    # Create forecast dictionary with confidence intervals
    forecast_dict = {
        str(date.date()): {
            'forecast': round(forecast, 2),
            'lower_bound': round(lower, 2),
            'upper_bound': round(upper, 2)
        }
        for date, forecast, lower, upper 
        in zip(future_dates, forecast_values, forecast_lower, forecast_upper)
    }

    # Generate context-aware warnings
    context = []
    
    # Build context description based on filters
    if product_id:
        context.append(f"Product {product_id}")
    if category:
        context.append(f"Category {category}")
    if region:
        context.append(f"{region} region")
    if min_rating:
        context.append(f"products rated {min_rating}+ stars")
    if max_price:
        context.append(f"products under ${max_price}")
    if min_discount:
        context.append(f"products with {min_discount}%+ discount")
    
    # Create context string
    context_str = " | ".join(context) if context else "all products"
    
    # Calculate deviations
    max_deviation = max(forecast_values) - max_level
    min_deviation = min_level - min(forecast_values)
    
    # Generate order recommendations with simple explanations
    warnings = []
    
    # Calculate current stock based on recent historical data
    latest_date = filtered_df['date'].max()
    last_30_days = filtered_df[filtered_df['date'] >= latest_date - pd.Timedelta(days=30)]
    daily_demand = last_30_days['sales'].mean()
    
    # Get the most recent stock level - calculate based on last week's average
    last_week = filtered_df[filtered_df['date'] >= latest_date - pd.Timedelta(days=7)]
    current_stock = last_week['sales'].mean() * 7  # Estimate current stock from last week's data
    
    # Calculate days of stock remaining
    days_stock_left = int(current_stock / daily_demand) if daily_demand > 0 else 30
    # Ensure days_stock_left is reasonable
    days_stock_left = min(max(days_stock_left, 0), 90)  # Cap between 0 and 90 days
    
    # Project future stock
    projected_stock = current_stock - (daily_demand * days)
    
    if product_id:
        # Calculate reorder threshold based on lead time and daily demand
        safety_days = 7  # Keep 7 days of safety stock
        
        if projected_stock <= reorder_point:
            # Calculate optimal order quantity
            order_quantity = max_level - projected_stock
            stock_duration = max(0, days_stock_left)
            
            warnings.append(f"🚨 Important Notice for Product {product_id}:")
            warnings.append(f"We need to order {int(order_quantity)} units because:")
            warnings.append(f"• Current stock level: {int(current_stock)} units")
            warnings.append(f"• This will last approximately {stock_duration} days")
            warnings.append(f"• Your daily sales average: {int(daily_demand)} units")
            warnings.append(f"• Delivery takes {lead_time} days + {safety_days} days safety stock needed")
            
            if stock_duration <= lead_time:
                warnings.append(f"⚡ URGENT: Order immediately to avoid stockout!")
            else:
                warnings.append(f"📦 Place order soon to maintain optimal stock levels")
        else:
            safe_days = int((projected_stock - reorder_point) / daily_demand) if daily_demand > 0 else 30
            warnings.append(f"✅ Product {product_id} stock is healthy:")
            warnings.append(f"• Current stock level: {int(current_stock)} units")
            warnings.append(f"• Stock will last for {safe_days} more days")
            warnings.append(f"• Daily sales average: {int(daily_demand)} units")
            warnings.append(f"• No immediate order needed")
    else:
        warnings.append("Please specify a product_id to get ordering recommendations")
    
    # warnings list is already created above

    # Plot forecast
    plt.figure(figsize=(12,6))
    
    # Plot historical data from filtered dataset
    plt.plot(filtered_df.groupby('date')['sales'].sum(), 
             label=f"Historical Data ({context_str})", 
             alpha=0.6)
    
    # Plot forecast
    plt.plot(future_dates, forecast_values, 
             label="Forecast", 
             linestyle="dashed", 
             color='green', 
             linewidth=2)
    
    # Plot inventory levels
    plt.axhline(y=reorder_point, color="red", linestyle="--", label="Reorder Point")
    plt.axhline(y=safety_stock, color="orange", linestyle="--", label="Safety Stock")
    plt.axhline(y=max_level, color="purple", linestyle=":", label="Maximum Level")
    plt.axhline(y=min_level, color="yellow", linestyle=":", label="Minimum Level")
    
    # Enhance the plot
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.title(f"Demand Forecast for {context_str}")
    plt.xlabel("Date")
    plt.ylabel("Units")
    plt.xticks(rotation=45)
    plt.tight_layout()
    # Save the plot to a file
    plt.savefig("forecast_plot.png")
    
    # For direct script execution, show the plot
    if __name__ == "__main__":
        plt.show()
    else:
        plt.close()

    # Return everything as dictionary (for API)
    return {
        "Reorder Point": reorder_point,
        "Safety Stock": safety_stock,
        "Minimum Level": min_level,
        "Maximum Level": max_level,
        "Forecast": forecast_dict,
        "Plot File": "forecast_plot.png",  # Add plot file path to response
        "Warnings": warnings if warnings else ["✅ Inventory levels are healthy."]
    }
    # Plot forecast
    plt.figure(figsize=(12,6))
    
    # Plot historical data from filtered dataset
    plt.plot(filtered_df.groupby('date')['sales'].sum(), 
             label=f"Historical Data ({context_str})", 
             alpha=0.6)
    
    # Plot forecast
    plt.plot(future_dates, forecast_values, 
             label="Forecast", 
             linestyle="dashed", 
             color='green', 
             linewidth=2)
    
    # Plot inventory levels
    plt.axhline(y=reorder_point, color="red", linestyle="--", label="Reorder Point")
    plt.axhline(y=safety_stock, color="orange", linestyle="--", label="Safety Stock")
    plt.axhline(y=max_level, color="purple", linestyle=":", label="Maximum Level")
    plt.axhline(y=min_level, color="yellow", linestyle=":", label="Minimum Level")
    
    # Enhance the plot
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.title(f"Demand Forecast for {context_str}")
    plt.xlabel("Date")
    plt.ylabel("Units")
    plt.xticks(rotation=45)
    plt.tight_layout()
    # Save the plot to a file
    plt.savefig("forecast_plot.png")
    
    # For direct script execution, show the plot
    if __name__ == "__main__":
        plt.show()
    else:
        plt.close()

    # Return everything as dictionary (for API)
    return {
        "Reorder Point": reorder_point,
        "Safety Stock": safety_stock,
        "Minimum Level": min_level,
        "Maximum Level": max_level,
        "Forecast": forecast_dict,
        "Plot File": "forecast_plot.png",  # Add plot file path to response
        "Warnings": warnings if warnings else ["✅ Inventory levels are healthy."]
    }

# If you run model.py directly, it will show results in console and display the plot
if __name__ == "__main__":
    print("\n=== Forecast Results ===")
    results = forecast(7)
    for k, v in results.items():
        if k != "Plot File":  # Skip printing the plot file path in console mode
            print(f"\n{k}:")
            print(v if isinstance(v, list) else f"{v}")


def _validate_required_columns(new_df: pd.DataFrame):
    required = {'date', 'sales'}
    missing = required - set(new_df.columns)
    if missing:
        raise ValueError(f"Uploaded CSV is missing required columns: {missing}")


def retrain_model(new_data_path: str, fine_tune: bool = True):
    """Read uploaded CSV, merge with existing dataset, retrain models, save artifacts and update global model.

    new_data_path: path to uploaded CSV file
    fine_tune: if True, use incremental fine-tuning on LSTM; if False, full retrain.
    """
    global df, GLOBAL_MODEL

    # Read uploaded CSV
    new_df = pd.read_csv(new_data_path)
    _validate_required_columns(new_df)
    if 'date' in new_df.columns:
        new_df['date'] = pd.to_datetime(new_df['date'])

    # Merge with existing dataset
    combined = pd.concat([df, new_df], ignore_index=True)

    # Deduplicate - prefer unique by (date, product_id) when available, else drop full-rows duplicates
    if 'product_id' in combined.columns:
        combined = combined.drop_duplicates(subset=['date', 'product_id'], keep='last')
    else:
        combined = combined.drop_duplicates(keep='last')

    combined = combined.sort_values('date')

    # Save combined dataset
    combined.to_csv(DATA_PATH, index=False)
    df = combined

    # Prepare data for Prophet (aggregate by date)
    prophet_df = df.groupby('date')['sales'].sum().reset_index()
    prophet_df.columns = ['ds', 'y']

    # Train models on combined data with fine-tuning option
    inv_model = InventoryForecastModel()
    # Use training with fine-tune parameter
    inv_model.train(prophet_df, fine_tune=fine_tune)

    # Save all model artifacts (Prophet + LSTM weights and scaler)
    try:
        inv_model.save(PROPHET_MODEL_PATH, LSTM_WEIGHTS_PATH, LSTM_SCALER_PATH)
    except Exception as e:
        # Fallback: try to save LSTM only
        try:
            inv_model.lstm_model.save(LSTM_WEIGHTS_PATH, LSTM_SCALER_PATH)
        except Exception:
            pass

    # Save metadata
    meta = {
        'last_training_date': str(inv_model.last_training_date),
        'trained_on_rows': int(len(df))
    }
    with open(MODEL_META, 'w') as f:
        json.dump(meta, f)

    # Update global cached model
    GLOBAL_MODEL = inv_model

    return {
        'status': 'success',
        'message': 'Model retrained on combined dataset',
        'meta': meta
    }


def retrain_model_with_queue(new_data_path: str, q: _queue.Queue, epochs: int = 50, batch_size: int = 32, fine_tune: bool = True):
    """Like retrain_model but sends progress messages to a queue (strings) and a final dict.

    q: queue.Queue instance where items are pushed. Strings are progress messages; a dict at the end is the result.
    fine_tune: if True, use incremental fine-tuning on LSTM; if False, full retrain.
    """
    global df, GLOBAL_MODEL
    
    try:
        q.put('Reading uploaded CSV...')
        new_df = pd.read_csv(new_data_path)
        _validate_required_columns(new_df)
        if 'date' in new_df.columns:
            new_df['date'] = pd.to_datetime(new_df['date'])

        q.put('Merging datasets...')
        combined = pd.concat([df, new_df], ignore_index=True)
        if 'product_id' in combined.columns:
            combined = combined.drop_duplicates(subset=['date', 'product_id'], keep='last')
        else:
            combined = combined.drop_duplicates(keep='last')
        combined = combined.sort_values('date')

        q.put('Saving combined dataset...')
        combined.to_csv(DATA_PATH, index=False)

        q.put('Preparing data for training...')
        prophet_df = combined.groupby('date')['sales'].sum().reset_index()
        prophet_df.columns = ['ds', 'y']

        # Train with progress callbacks and fine-tuning
        if fine_tune:
            q.put('🔄 Initializing fine-tuning mode...')
        else:
            q.put('Initializing model...')
        
        inv_model = InventoryForecastModel()

        def progress_cb(msg):
            q.put(msg)

        # Start Prophet and LSTM training with progress reporting and fine-tuning
        inv_model.train(prophet_df, progress_callback=progress_cb, fine_tune=fine_tune)

        q.put('Saving model artifacts...')
        try:
            inv_model.save(PROPHET_MODEL_PATH, LSTM_WEIGHTS_PATH, LSTM_SCALER_PATH)
        except Exception:
            try:
                inv_model.lstm_model.save(LSTM_WEIGHTS_PATH, LSTM_SCALER_PATH)
            except Exception:
                q.put('Warning: failed to save model weights')

        meta = {
            'last_training_date': str(inv_model.last_training_date),
            'trained_on_rows': int(len(combined))
        }
        with open(MODEL_META, 'w') as f:
            json.dump(meta, f)

        # update global model (already declared global at top of function)
        df = combined
        GLOBAL_MODEL = inv_model

        q.put({'status': 'success', 'message': 'Model retrained on combined dataset', 'meta': meta})
    except Exception as e:
        q.put({'status': 'error', 'message': str(e)})


# Attempt to initialize a global model on module import if data exists
try:
    if not df.empty:
        try:
            init_model = InventoryForecastModel()
            
            # Try to load saved model artifacts if they exist (FAST - no training)
            if PROPHET_MODEL_PATH.exists() and LSTM_WEIGHTS_PATH.exists() and LSTM_SCALER_PATH.exists():
                try:
                    logging.info("Loading saved model artifacts...")
                    init_model.load(PROPHET_MODEL_PATH, LSTM_WEIGHTS_PATH, LSTM_SCALER_PATH)
                    GLOBAL_MODEL = init_model
                    logging.info("Model loaded successfully from disk")
                except Exception as e:
                    # If loading fails, skip initial training (will train on first forecast or retrain)
                    logging.warning(f"Failed to load saved models: {e}")
                    GLOBAL_MODEL = None
            else:
                # No saved models exist - skip training on startup for faster start
                # Model will be trained on first forecast request or when retrain is called
                logging.info("No saved models found. Model will be trained on first use.")
                GLOBAL_MODEL = None
        except Exception as e:
            logging.warning(f"Error during model initialization: {e}")
            GLOBAL_MODEL = None
except Exception as e:
    logging.warning(f"Error during startup: {e}")
    GLOBAL_MODEL = None
