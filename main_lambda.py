"""Handler para deploy em AWS Lambda + API Gateway."""

from __future__ import annotations

from mangum import Mangum
from app.main import app, execute_prioritization

# Handler para API Gateway
mangum_handler = Mangum(app)

def handle_async_prioritization(event):
    """Executa a priorização de forma síncrona (mas em invocação assíncrona)."""
    print("🚀 Handling Async Prioritization Task")
    try:
        cap_total = event.get("capacidade_total")
        perc_sust = event.get("percentual_sustentacao")
        
        # Executar a lógica pesada
        result = execute_prioritization(
            capacidade_total=cap_total,
            percentual_sustentacao=perc_sust
        )
        
        # Atualizar status no DynamoDB
        from app.core.database import get_repository
        from datetime import datetime
        
        repo = get_repository()
        # É importante pegar settings atualizadas caso algo tenha mudado (embora improvável em poucos segundos)
        settings = repo.get_settings()
        
        priorizados = [i for i in result.itens if i.status == "Priorizado"]
        completion_message = f"""✅ **Priorização concluída!**

📊 **Resultados:**
- {len(priorizados)} itens priorizados de {len(result.itens)} total
- Capacidade: {result.capacidade_iniciativas}h
- Alocado: {result.horas_alocadas}h

Veja todos os detalhes na aba 'Backlog'!"""

        settings.last_prioritization_status = "completed"
        settings.last_prioritization_message = completion_message
        settings.last_prioritization_time = datetime.utcnow().isoformat()
        repo.update_settings(settings)
        print("✅ Async Prioritization Completed Successfully")
        return {"status": "success", "message": "Prioritization completed"}
        
    except Exception as e:
        import traceback
        print(f"❌ Async Prioritization Error: {e}")
        print(traceback.format_exc())
        
        try:
             from app.core.database import get_repository
             repo = get_repository()
             settings = repo.get_settings()
             settings.last_prioritization_status = "error"
             settings.last_prioritization_message = f"Erro: {str(e)}"
             repo.update_settings(settings)
        except Exception as inner_e:
             print(f"Error updating status to error: {inner_e}")
        
        # Não levantar exceção para evitar retries infinitos do Lambda (se configurado)
        return {"status": "error", "message": str(e)}


def handler(event, context):
    """Wrapper handler to separate Async Tasks from API Gateway events."""
    # Verificar se é um evento customizado de tarefa assíncrona
    if isinstance(event, dict) and event.get("type") == "async_task":
        return handle_async_prioritization(event)
    
    # Caso contrário, passar para o Mangum (API Gateway)
    return mangum_handler(event, context)

# Alias para compatibilidade
lambda_handler = handler
