import requests
import sys

# Configuration
BASE_URL = "https://4tgupu7jynssz7q4ivevmdmsau0hyxjd.lambda-url.us-east-1.on.aws"

def get_token():
    # Login to get valid token
    url = f"{BASE_URL}/auth/token"
    # Use the test user created/verified earlier
    data = {
        "username": "test@example.com",
        "password": "abc" 
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} {response.text}")
        sys.exit(1)
    return response.json()["access_token"]

def test_chat(token):
    # Try WITHOUT trailing slash
    url = f"{BASE_URL}/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": "oi",
        "conversation_id": None
    }
    
    print(f"Testing Chat URL: {url}")
    try:
        response = requests.post(url, json=payload, headers=headers, allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        if response.is_redirect:
            print(f"Redirect Location: {response.headers.get('Location')}")
        
        if response.status_code != 200 and not response.is_redirect:
            print(f"Error Response: {response.text}")
            return

        if response.status_code == 200:
             print("Response Stream:")
             # ...
        for line in response.iter_lines():
            if line:
                print(line.decode('utf-8'))
                
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    print("Getting token...")
    token = get_token()
    print("Token obtained. Testing chat...")
    test_chat(token)
