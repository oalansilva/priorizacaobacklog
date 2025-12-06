import boto3
import os
import sys
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import get_settings

def reset_status():
    settings = get_settings()
    print(f"Connecting to DynamoDB table: {settings.dynamodb_table_settings} in {settings.aws_region}")
    
    dynamodb = boto3.resource('dynamodb', region_name=settings.aws_region)
    table = dynamodb.Table(settings.dynamodb_table_settings)
    
    # Update the item to set status to 'idle' (or 'completed' or 'error')
    # We'll set it to 'error' with a message explaining it was reset manually, so the UI stops polling.
    # Or 'idle' if that's the default. Let's check what the app uses.
    # Usually 'idle' or just not 'running'.
    
    try:
        response = table.update_item(
            Key={'id': 1},
            UpdateExpression="set last_prioritization_status = :s, last_prioritization_message = :m",
            ExpressionAttributeValues={
                ':s': 'error',
                ':m': 'Status reset manually: Previous run stuck since 13:21'
            },
            ReturnValues="UPDATED_NEW"
        )
        print("Update succeeded:")
        print(response['Attributes'])
    except Exception as e:
        print(f"Error updating item: {e}")

if __name__ == "__main__":
    reset_status()
