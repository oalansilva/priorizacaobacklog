
import os
import sys
import uuid
from datetime import datetime

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
from app.models.db import BacklogItem

print("🚀 Adding Debug Items...")

repo = get_repository()

items = [
    BacklogItem(
        id=str(uuid.uuid4()),
        titulo="Implementar Login Social",
        descricao="Permitir login com Google e GitHub",
        esforco_estimado=20,
        area="Autenticação",
        dependencias="Nenhuma",
        status="Novo",
        prioridade=999,
        created_at=datetime.now().isoformat(),
        categoria="Feature",
        impacto_financeiro="Sim",
        impacto_negocios="Sim",
        impacto_cliente="Sim",
        okr="Sim",
        must_have="Não",
        estimado_qp="Q1",
        justificativa="",
        user_id="debug-user"
    ),
    BacklogItem(
        id=str(uuid.uuid4()),
        titulo="Refatorar Banco de Dados",
        descricao="Migrar de SQLite para DynamoDB",
        esforco_estimado=40,
        area="Backend",
        dependencias="Nenhuma",
        status="Novo",
        prioridade=999,
        created_at=datetime.now().isoformat(),
        categoria="Técnico",
        impacto_financeiro="Não",
        impacto_negocios="Sim",
        impacto_cliente="Não",
        okr="Não",
        must_have="Sim",
        estimado_qp="Q1",
        justificativa="",
        user_id="debug-user"
    )
]

for item in items:
    repo.add_item(item)
    print(f"Added item: {item.titulo}")

print("✅ Items added successfully.")
