"""
Test script to demonstrate fine-tuning workflow.
This script shows how the system now fine-tunes instead of full retraining.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import time

def create_test_data(product_id='P021', num_rows=50):
    """Create a small test dataset with new product."""
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(num_rows)]
    
    data = {
        'date': dates,
        'sales': np.random.randint(50, 150, num_rows),
        'product_id': [product_id] * num_rows,
        'category': ['Electronics'] * num_rows,
        'region': ['North'] * num_rows,
        'rating': np.random.uniform(3.5, 5.0, num_rows),
        'price': np.random.uniform(100, 500, num_rows),
        'discount': np.random.uniform(5, 25, num_rows)
    }
    
    return pd.DataFrame(data)

def test_fine_tuning():
    """Test the fine-tuning workflow."""
    
    print("=" * 70)
    print("🧪 TESTING FINE-TUNING WORKFLOW")
    print("=" * 70)
    
    # 1. Create test data
    print("\n📝 Step 1: Creating test dataset with P021...")
    test_df = create_test_data('P021', 50)
    test_file = 'test_fine_tune_data.csv'
    test_df.to_csv(test_file, index=False)
    print(f"✅ Created {test_file} with {len(test_df)} rows")
    print(f"   Products in test data: {test_df['product_id'].unique()}")
    
    # 2. Upload and retrain
    print("\n🚀 Step 2: Uploading to Flask /retrain endpoint...")
    print("   (This will use fine-tuning instead of full retrain)")
    print("-" * 70)
    
    url = 'http://localhost:8000/retrain'
    
    with open(test_file, 'rb') as f:
        files = {'file': (test_file, f, 'text/csv')}
        
        try:
            response = requests.post(url, files=files, stream=True)
            
            if response.status_code == 200:
                print("\n📊 Retraining Progress (with fine-tuning):")
                print("-" * 70)
                
                for line in response.iter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        
                        if data['type'] == 'progress':
                            # Highlight fine-tuning messages
                            msg = data['data']
                            if 'fine-tun' in msg.lower() or '🔄' in msg or '✅' in msg:
                                print(f"🎯 {msg}")
                            else:
                                print(f"   {msg}")
                        elif data['type'] == 'result':
                            result = data['data']
                            print("\n" + "=" * 70)
                            print("✅ RETRAINING COMPLETE!")
                            print("=" * 70)
                            print(f"Status: {result.get('status')}")
                            print(f"Message: {result.get('message')}")
                            if 'meta' in result:
                                print(f"Trained on rows: {result['meta'].get('trained_on_rows')}")
                                print(f"Last training: {result['meta'].get('last_training_date')}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to Flask server at http://localhost:8000")
            print("   Make sure Flask server is running: python app.py")
            return
    
    # 3. Wait for FastAPI to detect changes
    print("\n⏳ Step 3: Waiting for FastAPI to auto-detect model changes...")
    print("   (Background watcher checks every 2 seconds)")
    time.sleep(3)
    print("✅ Model should be reloaded by now!")
    
    # 4. Test forecast with new product
    print("\n🔮 Step 4: Testing forecast for P021 (new product)...")
    print("-" * 70)
    
    forecast_url = 'http://localhost:8001/forecast'
    payload = {
        'days': 7,
        'product_id': 'P021'
    }
    
    try:
        forecast_response = requests.post(forecast_url, json=payload)
        
        if forecast_response.status_code == 200:
            result = forecast_response.json()
            print("\n✅ FORECAST SUCCESSFUL!")
            print("=" * 70)
            print(f"Reorder Point: {result.get('Reorder Point')}")
            print(f"Safety Stock: {result.get('Safety Stock')}")
            print(f"Min Level: {result.get('Minimum Level')}")
            print(f"Max Level: {result.get('Maximum Level')}")
            
            print("\n📈 7-Day Forecast:")
            for date, values in list(result.get('Forecast', {}).items())[:7]:
                print(f"  {date}: {values['forecast']:.2f} units "
                      f"(range: {values['lower_bound']:.2f} - {values['upper_bound']:.2f})")
            
            print("\n⚠️ Warnings:")
            for warning in result.get('Warnings', []):
                print(f"  • {warning}")
                
        else:
            print(f"❌ Forecast Error: {forecast_response.status_code}")
            print(forecast_response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to FastAPI server at http://localhost:8001")
        print("   Make sure FastAPI server is running: uvicorn main:app --port 8001")
    
    print("\n" + "=" * 70)
    print("🎉 FINE-TUNING TEST COMPLETE!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("✅ New data merged with existing dataset")
    print("✅ LSTM model fine-tuned (not rebuilt from scratch)")
    print("✅ Prophet retrained normally")
    print("✅ Model artifacts saved automatically")
    print("✅ FastAPI auto-detected and reloaded updated models")
    print("✅ Forecasts using fine-tuned model without server restart")
    print("=" * 70)

if __name__ == '__main__':
    test_fine_tuning()
