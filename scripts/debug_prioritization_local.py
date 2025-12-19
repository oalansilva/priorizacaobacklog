
import os
import sys
import logging

# Configure logging to show everything
logging.basicConfig(level=logging.DEBUG)

# Set environment variables for DEV environment (matching deploy_dev.ps1)
os.environ["DATABASE_TYPE"] = "dynamodb"
os.environ["DYNAMODB_TABLE_SETTINGS"] = "backlog_settings_dev"
os.environ["DYNAMODB_TABLE_CONVERSATIONS"] = "backlog_conversations_dev"
os.environ["LLM_PROVIDER"] = "bedrock"
os.environ["DYNAMODB_TABLE_ITEMS"] = "backlog_items_dev"
os.environ["DYNAMODB_TABLE_ROADMAPS"] = "backlog_roadmaps_dev"
os.environ["DYNAMODB_TABLE_USERS"] = "backlog_users_dev"
os.environ["RESULTADO_SHEET_NAME"] = "Roadmap"
os.environ["BEDROCK_MODEL_ID"] = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
os.environ["BEDROCK_GUARDRAIL_ID"] = "" # Disable guardrail explicitly regarding .env

# Set AWS Region if not set
if "AWS_DEFAULT_REGION" not in os.environ:
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import execute_prioritization

print("🚀 Starting Local Prioritization Debug...\n")

try:
    # Execute prioritization with default settings (None -> pull from DB)
    # Using a dummy user_id for testing if needed, or None
    result = execute_prioritization(
        capacidade_total=None,
        percentual_sustentacao=None,
        user_id=None # Get all items for debugging
    )
    
    print("\n✅ Prioritization Completed Successfully!")
    print(f"Total Items: {len(result.itens)}")
    print(f"Prioritized: {len([i for i in result.itens if i.status == 'Priorizado'])}")
    
    print("\n📝 Prioritized Items Details:")
    for item in result.itens:
        if item.status == "Priorizado":
            print(f"- [{item.outros_dados.get('workflow_stage', 'N/A')}] {item.item} ({item.horas}h) [Score: {item.outros_dados.get('score')}%]")
            print(f"  Justificativa: {item.justificativa}")
            
    print("\n❌ Desprioritized Upstream Items (Sample):")
    for item in result.itens:
        if item.status == "Despriorizado" and str(item.outros_dados.get('workflow_stage', '')).lower() == 'upstream':
             print(f"- {item.item} ({item.horas}h) [Score: {item.outros_dados.get('score')}%]")
             print(f"  Justificativa: {item.justificativa}")

except Exception as e:
    print(f"\n❌ Prioritization Failed: {e}")
    import traceback
    traceback.print_exc()
