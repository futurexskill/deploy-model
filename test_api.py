import requests
import json

# API base URL
BASE_URL = "http://127.0.0.1:5001"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def print_response(response):
    """Pretty print JSON response"""
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print(f"\nStatus Code: {response.status_code}")

def test_home():
    """Test home endpoint"""
    print_section("Test 1: Home Endpoint")
    response = requests.get(f"{BASE_URL}/")
    print_response(response)

def test_health():
    """Test health check endpoint"""
    print_section("Test 2: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)

def test_single_prediction_not_purchase():
    """Test single prediction - will not purchase"""
    print_section("Test 3: Single Prediction - Will NOT Purchase")
    data = {
        "age": 25,
        "salary": 30000
    }
    print(f"Input: {json.dumps(data, indent=2)}")
    response = requests.post(f"{BASE_URL}/predict", json=data)
    print_response(response)

def test_single_prediction_will_purchase():
    """Test single prediction - will purchase"""
    print_section("Test 4: Single Prediction - WILL Purchase")
    data = {
        "age": 45,
        "salary": 75000
    }
    print(f"Input: {json.dumps(data, indent=2)}")
    response = requests.post(f"{BASE_URL}/predict", json=data)
    print_response(response)

def test_single_prediction_edge_case():
    """Test single prediction - edge case"""
    print_section("Test 5: Single Prediction - Edge Case")
    data = {
        "age": 35,
        "salary": 50000
    }
    print(f"Input: {json.dumps(data, indent=2)}")
    response = requests.post(f"{BASE_URL}/predict", json=data)
    print_response(response)

def test_batch_prediction():
    """Test batch prediction"""
    print_section("Test 6: Batch Prediction - Multiple Customers")
    data = {
        "customers": [
            {"age": 25, "salary": 30000},
            {"age": 35, "salary": 50000},
            {"age": 45, "salary": 75000},
            {"age": 60, "salary": 90000},
            {"age": 28, "salary": 70000}
        ]
    }
    print(f"Input: {len(data['customers'])} customers")
    response = requests.post(f"{BASE_URL}/predict/batch", json=data)
    print_response(response)

def test_error_missing_fields():
    """Test error handling - missing fields"""
    print_section("Test 7: Error Handling - Missing Required Fields")
    data = {
        "age": 25
        # Missing salary
    }
    print(f"Input: {json.dumps(data, indent=2)}")
    response = requests.post(f"{BASE_URL}/predict", json=data)
    print_response(response)

def test_error_invalid_data():
    """Test error handling - invalid data"""
    print_section("Test 8: Error Handling - Invalid Age")
    data = {
        "age": -5,
        "salary": 50000
    }
    print(f"Input: {json.dumps(data, indent=2)}")
    response = requests.post(f"{BASE_URL}/predict", json=data)
    print_response(response)

def test_error_invalid_endpoint():
    """Test error handling - invalid endpoint"""
    print_section("Test 9: Error Handling - Invalid Endpoint")
    response = requests.get(f"{BASE_URL}/invalid")
    print_response(response)

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("CUSTOMER PURCHASE PREDICTION API - PYTHON TEST SUITE")
    print("=" * 70)
    print(f"\nAPI URL: {BASE_URL}")
    print("Make sure the API server is running before running tests!")
    print("\nStarting tests...\n")
    
    try:
        # Run all tests
        test_home()
        test_health()
        test_single_prediction_not_purchase()
        test_single_prediction_will_purchase()
        test_single_prediction_edge_case()
        test_batch_prediction()
        test_error_missing_fields()
        test_error_invalid_data()
        test_error_invalid_endpoint()
        
        print_section("✓ ALL TESTS COMPLETED SUCCESSFULLY!")
        
    except requests.exceptions.ConnectionError:
        print("\n" + "=" * 70)
        print("✗ ERROR: Cannot connect to API server")
        print("=" * 70)
        print("\nPlease make sure the API server is running:")
        print("  python app.py")
        print("\nOr:")
        print("  ./venv/bin/python app.py")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")

if __name__ == "__main__":
    main()
