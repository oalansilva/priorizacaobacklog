import requests
import sys
import json

# Configuration
BASE_URL = "https://4tgupu7jynssz7q4ivevmdmsau0hyxjd.lambda-url.us-east-1.on.aws"

def get_token():
    url = f"{BASE_URL}/auth/token"
    # Use the test user
    data = {
        "username": "test@example.com",
        "password": "abc" 
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} {response.text}")
        sys.exit(1)
    return response.json()["access_token"]

def test_list_items(token):
    # Note: No trailing slash
    url = f"{BASE_URL}/items"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Testing List Items URL: {url}")
    try:
        response = requests.get(url, headers=headers, allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        
        if response.is_redirect:
            print(f"Redirect Location: {response.headers.get('Location')}")
            
        if response.status_code == 200:
            print(f"Success! Found {len(items)} items:")
            print(json.dumps(items, indent=2))
        else:
             print(f"Error: {response.text}")

    except Exception as e:
        print(f"Exception: {e}")

def test_add_item(token):
    url = f"{BASE_URL}/items" 
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "titulo": "Test Item from Script",
        "descricao": "Description",
        "esforco_estimado": 5,
        "area": "Dev",
        "status": "Novo"
    }
    print(f"Adding item...")
    try:
        response = requests.post(url, json=payload, headers=headers, allow_redirects=False)
        print(f"Add Status: {response.status_code}")
        if response.status_code == 200:
            print("Item added:", response.json())
        else:
            print("Error adding:", response.text)
    except Exception as e:
        print(f"Exception adding: {e}")

if __name__ == "__main__":
    print("Getting token...")
    token = get_token()
    print("Token obtained.")
    test_add_item(token)
    print("Listing items...")
    test_list_items(token)
