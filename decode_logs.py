import json
import base64
import sys

try:
    with open('response_logs.json', 'r') as f:
        response = json.load(f)
        
    log_result = response.get('LogResult', '')
    if log_result:
        decoded_logs = base64.b64decode(log_result).decode('utf-8')
        print(decoded_logs)
    else:
        print("No LogResult found in response.")
        
except Exception as e:
    print(f"Error decoding logs: {e}")
