
import os
import sys
import pandas as pd

# Set environment variables for DEV environment
os.environ["DATABASE_TYPE"] = "dynamodb"
os.environ["DYNAMODB_TABLE_SETTINGS"] = "backlog_settings_dev"
os.environ["DYNAMODB_TABLE_CONVERSATIONS"] = "backlog_conversations_dev"
os.environ["LLM_PROVIDER"] = "bedrock"
os.environ["DYNAMODB_TABLE_ITEMS"] = "backlog_items_dev"
os.environ["DYNAMODB_TABLE_ROADMAPS"] = "backlog_roadmaps_dev"
os.environ["DYNAMODB_TABLE_USERS"] = "backlog_users_dev"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import get_repository

print("🚀 Analyzing Desprioritized Items...\n")

repo = get_repository()
settings = repo.get_settings()
items = repo.list_items()

print(f"Total Items in DB: {len(items)}")

df = pd.DataFrame([item.model_dump() for item in items])

if "status" not in df.columns:
    print("No status column found!")
    sys.exit(1)

# Filter Despriorizado
despriorizados = df[df["status"] == "Despriorizado"].copy()
print(f"Total Despriorizados: {len(despriorizados)}")

if despriorizados.empty:
    print("No desprioritized items found.")
    sys.exit(0)

# Ensure numeric hours
despriorizados["esforco_estimado"] = pd.to_numeric(despriorizados["esforco_estimado"], errors="coerce").fillna(0)

print("\n📊 Breakdown by Workflow Stage:")
if "workflow_stage" in despriorizados.columns:
    summary = despriorizados.groupby("workflow_stage")["esforco_estimado"].agg(['count', 'sum', 'mean']).reset_index()
    summary.columns = ["Stage", "Count", "Total Hours", "Avg Hours"]
    print(summary.to_string(index=False))
else:
    print("Column 'workflow_stage' missing in data!")

print("\n🔍 Detailed List of Desprioritized Items:")
cols = ["titulo", "workflow_stage", "esforco_estimado"] 
if "workflow_stage" not in despriorizados.columns: 
    cols.remove("workflow_stage")

for idx, row in despriorizados.iterrows():
    stage = row.get('workflow_stage', 'N/A')
    print(f"- [{stage}] {row['titulo']} ({row['esforco_estimado']}h)")

# Check allocation settings
total = settings.capacidade_total
down_percent = settings.capacity_downstream_percent
down_limit = total * (down_percent / 100)
print(f"\n⚙️  Settings: Total={total}h, Downstream={down_percent}% ({down_limit}h)")
