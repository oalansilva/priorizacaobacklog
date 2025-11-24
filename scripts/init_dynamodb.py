import boto3
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.config import get_settings

def init_dynamodb():
    settings = get_settings()
    print(f"Initializing DynamoDB tables in region {settings.aws_region}...")
    
    dynamodb = boto3.resource('dynamodb', region_name=settings.aws_region)
    
    tables = [
        {
            'name': settings.dynamodb_table_items,
            'key_schema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
            'attribute_definitions': [{'AttributeName': 'id', 'AttributeType': 'S'}]
        },
        {
            'name': settings.dynamodb_table_conversations,
            'key_schema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
            'attribute_definitions': [{'AttributeName': 'id', 'AttributeType': 'S'}]
        },
        {
            'name': settings.dynamodb_table_settings,
            'key_schema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
            'attribute_definitions': [{'AttributeName': 'id', 'AttributeType': 'N'}]
        }
    ]
    
    for table_config in tables:
        table_name = table_config['name']
        try:
            table = dynamodb.Table(table_name)
            table.load()
            print(f"Table {table_name} already exists. Status: {table.table_status}")
        except Exception:
            print(f"Creating table {table_name}...")
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=table_config['key_schema'],
                AttributeDefinitions=table_config['attribute_definitions'],
                BillingMode='PAY_PER_REQUEST'
            )
            print(f"Table {table_name} creating...")
            table.wait_until_exists()
            print(f"Table {table_name} created successfully.")

if __name__ == "__main__":
    init_dynamodb()
