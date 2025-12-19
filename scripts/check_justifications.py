
import os
import sys
import boto3
import pandas as pd
from app.core.database import get_repository

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_justifications():
    repo = get_repository()
    items = repo.list_items()
    
    df = pd.DataFrame([item.model_dump() for item in items])
    
    # Filter for Priorizado and Upstream
    if "workflow_stage" in df.columns:
        upstream_prioritized = df[
            (df["status"] == "Priorizado") & 
            (df["workflow_stage"].str.lower() == "upstream")
        ]
        
        print(f"Found {len(upstream_prioritized)} prioritized Upstream items.")
        
        for _, row in upstream_prioritized.iterrows():
            print(f"- [{row['item']}] ({row['horas']}h) Score: {row.get('outros_dados', {}).get('score')}%")
            print(f"  Justificativa: {row['justificativa']}")
            print("-" * 50)
            
    else:
        print("Column 'workflow_stage' missing.")

if __name__ == "__main__":
    check_justifications()
