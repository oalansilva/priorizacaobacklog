from typing import List, Optional
import pandas as pd
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from app.core.database import DatabaseRepository
from app.models.db import BacklogItem
from app.config import get_settings
from app.core.prioritization import PrioritizationService
import traceback

# Global repository instance for tools to access
_repository: Optional[DatabaseRepository] = None
_agent_graph = None

def get_agent_executor(repository: DatabaseRepository):
    global _repository, _agent_graph
    _repository = repository
    
    # Return cached agent if already initialized
    if _agent_graph is not None:
        return _agent_graph
    
    from app.services.llm import get_llm
    
    settings = get_settings()
    llm = get_llm(settings)

    tools = [add_backlog_item, list_backlog_items, check_prioritization_status, prioritize_backlog]

    # LangGraph's create_react_agent returns a CompiledGraph
    _agent_graph = create_react_agent(llm, tools=tools)
    return _agent_graph

@tool
def add_backlog_item(
    titulo: str, 
    descricao: str, 
    esforco_estimado: int, 
    area: str, 
    categoria: str = None,
    impacto_financeiro: str = "Não",
    impacto_negocios: str = "Não",
    impacto_cliente: str = "Não",
    okr: str = "Não",
    estimado_qp: str = "Não"
) -> str:
    """Adiciona um novo item ao backlog. 
    esforco_estimado deve ser um inteiro (horas).
    Os campos impacto_financeiro, impacto_negocios, impacto_cliente, okr e estimado_qp devem ser 'Sim' ou 'Não'.
    """
    if _repository is None:
        return "Erro: Repositório não inicializado."
    
    item = BacklogItem(
        titulo=titulo,
        descricao=descricao,
        esforco_estimado=esforco_estimado,
        area=area,
        categoria=categoria,
        impacto_financeiro=impacto_financeiro,
        impacto_negocios=impacto_negocios,
        impacto_cliente=impacto_cliente,
        okr=okr,
        estimado_qp=estimado_qp
    )
    _repository.add_item(item)
    return f"Item '{titulo}' adicionado com sucesso ao backlog (ID: {item.id})."

@tool
def list_backlog_items() -> str:
    """APENAS LISTA os itens do backlog sem fazer priorização.
    
    Use esta ferramenta quando o usuário pedir para:
    - "listar itens"
    - "mostrar itens"
    - "quais itens temos"
    - "ver o backlog"
    
    NÃO use esta ferramenta para priorizar. Para priorização, use prioritize_backlog.
    """
    if _repository is None:
        return "Erro: Repositório não inicializado."
    
    items = _repository.list_items()
    if not items:
        return "O backlog está vazio."
    
    result = "Itens no Backlog:\n"
    for item in items:
        result += f"- [{item.status}] {item.titulo} (Esforço: {item.esforco_estimado}h)\n"
    return result

@tool
def check_prioritization_status() -> str:
    """Verifica se uma priorização em andamento foi concluída.
    
    Use esta ferramenta quando:
    - O usuário perguntar se a priorização terminou
    - O usuário pedir para verificar o status
    - Após iniciar uma priorização, para avisar o usuário quando concluir
    
    Returns:
        Status da priorização: "running", "completed", ou "none"
    """
    if _repository is None:
        return "Erro: Repositório não inicializado."
    
    settings = _repository.get_settings()
    
    if not settings.last_prioritization_status:
        return "Nenhuma priorização em andamento."
    
    
    if settings.last_prioritization_status == "running":
        return "A priorização ainda está em andamento. Aguarde alguns momentos..."
    
    if settings.last_prioritization_status == "completed":
        # Manter o status para exibição persistente na UI
        return settings.last_prioritization_message or "Priorização concluída!"
    
    if settings.last_prioritization_status == "error":
        # Manter o status para exibição persistente na UI
        return settings.last_prioritization_message or "Erro na priorização."
    
    return "Status desconhecido."

@tool
def prioritize_backlog(capacidade_total: Optional[int] = None, percentual_sustentacao: Optional[int] = None) -> str:
    """EXECUTE A PRIORIZAÇÃO COMPLETA DO BACKLOG usando IA para analisar e ordenar itens.
    
    Use esta ferramenta quando o usuário pedir para:
    - "priorizar o backlog"
    - "fazer a priorização"
    - "organizar por prioridade"
    - "executar priorização"
    
    Esta ferramenta irá:
    1. Buscar todos os itens do backlog
    2. Executar análise com IA para determinar prioridades
    3. Atualizar o status dos itens (Priorizado/Despriorizado)
    4. Retornar um resumo detalhado
    
    Args:
        capacidade_total: Total de horas disponíveis (opcional, usa configuração do sistema se omitido)
        percentual_sustentacao: Percentual de sustentação (opcional, usa configuração do sistema se omitido)
    
    Returns:
        Resumo da priorização executada com itens priorizados e despriorizados
    """
    if _repository is None:
        return "Erro: Repositório não inicializado."
    
    # Carregar configurações se não forem fornecidas
    settings_db = _repository.get_settings()
    cap_total = capacidade_total if capacidade_total is not None else settings_db.capacidade_total
    perc_sust = percentual_sustentacao if percentual_sustentacao is not None else settings_db.percentual_sustentacao
    
    try:
        # Executar priorização em thread separada para retornar imediatamente
        import threading
        
        def run_prioritization_async():
            """Executa priorização em background"""
            try:
                from app.main import execute_prioritization
                result = execute_prioritization(
                    capacidade_total=cap_total,
                    percentual_sustentacao=perc_sust
                )
                
                # Salvar status de conclusão no DynamoDB
                priorizados = [i for i in result.itens if i.status == "Priorizado"]
                completion_message = f"""✅ **Priorização concluída!**

📊 **Resultados:**
- {len(priorizados)} itens priorizados de {len(result.itens)} total
- Capacidade: {result.capacidade_iniciativas}h
- Alocado: {result.horas_alocadas}h

Veja todos os detalhes na aba 'Backlog'!"""
                
                # Salvar nas settings com timestamp
                from datetime import datetime
                settings_db.last_prioritization_status = "completed"
                settings_db.last_prioritization_message = completion_message
                settings_db.last_prioritization_time = datetime.utcnow().isoformat()
                _repository.update_settings(settings_db)
                
            except Exception as e:
                # Log error but don't fail the user-facing response
                import traceback
                print(f"Background prioritization error: {e}")
                print(traceback.format_exc())
                
                # Salvar status de erro
                try:
                    settings_db.last_prioritization_status = "error"
                    settings_db.last_prioritization_message = f"Erro: {str(e)}"
                    _repository.update_settings(settings_db)
                except:
                    pass
        
        # Limpar status anterior
        settings_db.last_prioritization_status = "running"
        settings_db.last_prioritization_message = None
        _repository.update_settings(settings_db)
        
        # Iniciar thread de background
        thread = threading.Thread(target=run_prioritization_async, daemon=True)
        thread.start()
        
        # Retornar imediatamente com mensagem de confirmação
        response = """✅ **Priorização iniciada com sucesso!**

A análise está sendo processada em segundo plano. Isso pode levar alguns momentos.

📊 **Configuração:**
- Capacidade total: {cap_total}h
- Sustentação: {perc_sust}%

Você pode visualizar os resultados atualizados na aba 'Backlog' em breve.

💡 *Dica: Não é necessário esperar - você pode continuar usando o sistema normalmente.*""".format(
            cap_total=cap_total,
            perc_sust=perc_sust
        )
        
        return response
        
    except Exception as e:
        error_details = traceback.format_exc()
        return f"Erro ao executar priorização: {str(e)}\n\nDetalhes técnicos:\n{error_details}"
