"""
Test what the server API is actually seeing in the database
"""
import requests
import json

def test_api():
    base_url = "http://localhost:8000"

    print("=== Testing Menu API ===")

    # Test menu items
    try:
        response = requests.get(f"{base_url}/api/menu/items")
        if response.status_code == 200:
            items = response.json()
            print(f"Menu API returned {len(items)} items:")
            for item in items:
                print(f"  - ID: {item['id']}, Name: {item['name']}, Price: ${item['price']}")
        else:
            print(f"Menu API error: {response.status_code}")
    except Exception as e:
        print(f"Error calling menu API: {e}")

    # Test categories
    try:
        response = requests.get(f"{base_url}/api/menu/categories")
        if response.status_code == 200:
            categories = response.json()
            print(f"\nMenu API returned {len(categories)} categories:")
            for cat in categories:
                print(f"  - ID: {cat['id']}, Name: {cat['name']}")
        else:
            print(f"Categories API error: {response.status_code}")
    except Exception as e:
        print(f"Error calling categories API: {e}")

if __name__ == "__main__":
    test_api()
