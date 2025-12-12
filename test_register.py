import requests
import json

# Test registration with a short password
url = "https://4tgupu7jynssz7q4ivevmdmsau0hyxjd.lambda-url.us-east-1.on.aws/auth/register"

payload = {
    "email": "test@example.com",
    "password": "abc",  # Very short password to test
    "full_name": "Test User"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
