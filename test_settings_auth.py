import requests
import sys
import json

# Configuration
BASE_URL = "https://4tgupu7jynssz7q4ivevmdmsau0hyxjd.lambda-url.us-east-1.on.aws"

def get_token():
    url = f"{BASE_URL}/auth/token"
    data = {
        "username": "test@example.com",
        "password": "abc" 
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} {response.text}")
        sys.exit(1)
    return response.json()["access_token"]

def test_settings(token):
    # Note: No trailing slash
    url = f"{BASE_URL}/settings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Testing Settings URL: {url}")
    try:
        response = requests.get(url, headers=headers, allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            settings = response.json()
            print(f"Success! Settings: {json.dumps(settings, indent=2)}\n")
        else:
             print(f"Error: {response.text}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    print("Getting token...")
    token = get_token()
    test_settings(token)
