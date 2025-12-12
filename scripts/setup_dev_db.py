import boto3
import os

# Configuration matches deploy_dev.ps1
TABLE_SUFFIX = "_dev"
TABLES = {
    f"backlog_items{TABLE_SUFFIX}": "id",
    f"backlog_conversations{TABLE_SUFFIX}": "id",
    f"backlog_settings{TABLE_SUFFIX}": "id",
    f"backlog_roadmaps{TABLE_SUFFIX}": "id",
    f"backlog_users{TABLE_SUFFIX}": "id",
}

def create_tables():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    existing_tables = [t.name for t in dynamodb.tables.all()]
    
    print(f"Existing tables: {existing_tables}")
    
    for table_name, pk in TABLES.items():
        if table_name in existing_tables:
            print(f"Table {table_name} already exists. Skipping.")
            continue
            
        print(f"Creating table {table_name}...")
        try:
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': pk,
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': pk,
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            print(f"Table {table_name} creation initiated.")
            table.wait_until_exists()
            print(f"Table {table_name} created successfully.")
        except Exception as e:
            print(f"Error creating table {table_name}: {e}")

if __name__ == "__main__":
    create_tables()
