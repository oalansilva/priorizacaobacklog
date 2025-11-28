import boto3
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import get_settings

def check_status():
    settings = get_settings()
    print(f"Connecting to DynamoDB table: {settings.dynamodb_table_settings} in {settings.aws_region}")
    
    dynamodb = boto3.resource('dynamodb', region_name=settings.aws_region)
    table = dynamodb.Table(settings.dynamodb_table_settings)
    
    response = table.get_item(Key={'id': 1})
    item = response.get('Item')
    
    if item:
        print("\n--- Current Status ---")
        print(f"Status: {item.get('last_prioritization_status')}")
        print(f"Message: {item.get('last_prioritization_message')}")
        print(f"Time: {item.get('last_prioritization_time')}")
    else:
        print("Settings not found.")

if __name__ == "__main__":
    check_status()
