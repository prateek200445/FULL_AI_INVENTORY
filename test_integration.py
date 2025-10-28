"""
Quick test script to verify the retraining flow works end-to-end.
Run this after starting the Flask server with: python app.py
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"
TEST_CSV = "test_upload.csv"

def test_health():
    """Test server is running."""
    print("\n=== Testing Server Health ===")
    try:
        resp = requests.get(f"{BASE_URL}/")
        print(f"✓ Server is running: {resp.json()}")
        return True
    except Exception as e:
        print(f"✗ Server not reachable: {e}")
        print("  Make sure to run: python app.py")
        return False

def test_retrain():
    """Test file upload and retraining with streaming progress."""
    print("\n=== Testing Retrain Endpoint ===")
    try:
        with open(TEST_CSV, 'rb') as f:
            files = {'file': (TEST_CSV, f, 'text/csv')}
            resp = requests.post(f"{BASE_URL}/retrain", files=files, stream=True)
            
            print(f"Status: {resp.status_code}")
            print("Progress:")
            
            for line in resp.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if data['type'] == 'progress':
                            print(f"  [PROGRESS] {data['data']}")
                        elif data['type'] == 'result':
                            print(f"  [RESULT] {json.dumps(data['data'], indent=2)}")
                            if data['data'].get('status') == 'success':
                                print("✓ Retraining completed successfully!")
                                return True
                            else:
                                print("✗ Retraining failed!")
                                return False
                    except json.JSONDecodeError:
                        print(f"  [RAW] {line.decode('utf-8')}")
            
        return False
    except Exception as e:
        print(f"✗ Retrain test failed: {e}")
        return False

def test_forecast():
    """Test forecast endpoint."""
    print("\n=== Testing Forecast Endpoint ===")
    try:
        payload = {
            "days": 5,
            "product_id": "P001"
        }
        resp = requests.post(f"{BASE_URL}/forecast", json=payload)
        result = resp.json()
        
        print(f"Status: {resp.status_code}")
        if 'error' not in result:
            print(f"✓ Forecast generated successfully!")
            print(f"  Reorder Point: {result.get('Reorder Point')}")
            print(f"  Safety Stock: {result.get('Safety Stock')}")
            print(f"  Forecast days: {len(result.get('Forecast', {}))}")
            return True
        else:
            print(f"✗ Forecast error: {result.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Forecast test failed: {e}")
        return False

def test_static_page():
    """Test static retrain page is accessible."""
    print("\n=== Testing Static HTML Page ===")
    try:
        resp = requests.get(f"{BASE_URL}/static/retrain.html")
        if resp.status_code == 200 and 'Retrain Model' in resp.text:
            print("✓ Static HTML page is accessible")
            print(f"  Open in browser: {BASE_URL}/static/retrain.html")
            return True
        else:
            print("✗ Static page not found or incomplete")
            return False
    except Exception as e:
        print(f"✗ Static page test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("RETRAINABLE MODEL SYSTEM - INTEGRATION TEST")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Server health
    results['health'] = test_health()
    if not results['health']:
        print("\n❌ Server is not running. Please start with: python app.py")
        return
    
    # Give server a moment
    time.sleep(1)
    
    # Test 2: Static page
    results['static'] = test_static_page()
    
    # Test 3: Retraining
    results['retrain'] = test_retrain()
    
    # Test 4: Forecast
    results['forecast'] = test_forecast()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results.values())
    total = len(results)
    
    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The retrainable model system is working.")
        print("\nNext steps:")
        print("1. Open http://localhost:8000/static/retrain.html in your browser")
        print("2. Upload test_upload.csv or your own CSV file")
        print("3. Watch the progress stream in real-time")
        print("4. Use the retrained model for forecasts immediately")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
