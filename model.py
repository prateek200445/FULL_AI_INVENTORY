# model.py
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

# Configure logging
logging.getLogger('prophet').setLevel(logging.ERROR)  # Reduce Prophet debugging output

# Configure logging only
logging.getLogger('prophet').setLevel(logging.ERROR)  # Reduce Prophet debugging output

# Load your dataset
df = pd.read_csv("large_dataset.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')  # Ensure data is sorted by date

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
    
    def train(self, data):
        # Scale the data
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))
        
        # Create sequences
        X, y = self.create_sequences(scaled_data)
        
        # Build and train model
        self.model = self.build_model((self.sequence_length, 1))
        self.model.fit(X, y, epochs=50, batch_size=32, verbose=0)
        
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
        
    def train(self, data):
        # Train Prophet model
        self.prophet_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True,
            seasonality_mode='multiplicative',
            interval_width=0.95,  # 95% confidence interval
            changepoint_prior_scale=0.05  # Makes trend more flexible
        )
        self.prophet_model.fit(data)
        
        # Train LSTM model
        sales_data = data['y'].values
        self.lstm_model.train(sales_data)
        
        self.last_training_date = data['ds'].max()

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
    
    # Initialize and train Prophet model
    model = InventoryForecastModel()
    prophet_data = filtered_df.groupby('date')['sales'].sum().reset_index()
    prophet_data.columns = ['ds', 'y']
    
    model.train(prophet_data)
    # Get Prophet forecast
    prophet_forecast = model.prophet_model.predict(model.prophet_model.make_future_dataframe(periods=int(days), freq='D'))
    
    # Get LSTM forecast
    sales_data = prophet_data['y'].values
    lstm_forecast = model.lstm_model.predict(sales_data, days)
    
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
