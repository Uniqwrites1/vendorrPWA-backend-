"""
Test to debug what exactly is being sent from frontend vs working requests
"""
import requests
import json

def test_different_request_formats():
    base_url = "http://localhost:8000"

    print("=== Testing Different Login Request Formats ===")

    # Test 1: Simple JSON (what our working test uses)
    print("\n1. Testing simple JSON format:")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"email": "customer@test.com", "password": "test123"},
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

    # Test 2: With additional headers (simulating frontend)
    print("\n2. Testing with additional headers:")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"email": "customer@test.com", "password": "test123"},
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Origin": "http://localhost:3000",
                "Referer": "http://localhost:3000/login"
            }
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

    # Test 3: With empty or invalid token header
    print("\n3. Testing with Authorization header:")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"email": "customer@test.com", "password": "test123"},
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer "
            }
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

    # Test 4: Wrong credentials
    print("\n4. Testing with wrong credentials:")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"email": "customer@test.com", "password": "wrongpassword"},
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Expected 401 for wrong credentials: {response.text[:100]}")
    except Exception as e:
        print(f"   Exception: {e}")

    # Test 5: Missing email
    print("\n5. Testing with missing email:")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"password": "test123"},
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_different_request_formats()
