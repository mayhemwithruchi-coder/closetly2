"""
Test script to verify the Closetly application works correctly
"""
import requests
import json

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:10000/health')
        if response.status_code == 200:
            print("✅ Health endpoint test passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health endpoint test failed with status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint test failed with error: {e}")

def test_predict_endpoint():
    """Test the predict endpoint"""
    try:
        data = {
            "brand": "Levi's",
            "category": "Jeans",
            "retailer": "Myntra",
            "discount_percent": 10
        }
        response = requests.post('http://localhost:10000/predict', json=data)
        if response.status_code == 200:
            print("✅ Predict endpoint test passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Predict endpoint test failed with status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Predict endpoint test failed with error: {e}")

def test_compare_endpoint():
    """Test the compare endpoint"""
    try:
        data = {
            "product_name": "Blue Jeans",
            "brand": "Levi's",
            "category": "Jeans"
        }
        response = requests.post('http://localhost:10000/compare', json=data)
        if response.status_code == 200:
            print("✅ Compare endpoint test passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Compare endpoint test failed with status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Compare endpoint test failed with error: {e}")

if __name__ == "__main__":
    print("Testing Closetly Application Endpoints...")
    print("=" * 50)
    
    test_health_endpoint()
    print()
    test_predict_endpoint()
    print()
    test_compare_endpoint()
    
    print("\n" + "=" * 50)
    print("Testing complete!")