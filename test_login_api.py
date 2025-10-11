"""
Test the actual login API endpoint
"""
import requests
import json

def test_login_api():
    base_url = "http://localhost:8000"

    # Test data
    login_data = {
        "email": "customer@test.com",
        "password": "test123"
    }

    print("=== Testing Login API ===")
    print(f"Attempting login with: {login_data['email']}")

    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            print(f"Success! Token received: {result.get('access_token', 'No token')[:20]}...")
        else:
            print(f"Error Response: {response.text}")

    except Exception as e:
        print(f"Request failed: {e}")

    # Also test admin login
    admin_data = {
        "email": "admin@vendorr.com",
        "password": "admin123"
    }

    print(f"\n=== Testing Admin Login ===")
    print(f"Attempting login with: {admin_data['email']}")

    try:
        response = requests.post(f"{base_url}/api/auth/login", json=admin_data)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Success! Token received: {result.get('access_token', 'No token')[:20]}...")
        else:
            print(f"Error Response: {response.text}")

    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_login_api()
