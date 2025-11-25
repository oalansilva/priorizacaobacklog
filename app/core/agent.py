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

    tools = [add_backlog_item, list_backlog_items, prioritize_backlog]

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
        # Usar a função compartilhada de priorização
        from app.main import execute_prioritization
        
        result = execute_prioritization(
            capacidade_total=cap_total,
            percentual_sustentacao=perc_sust
        )
        
        # Montar resposta formatada para o chat
        priorizados = [i for i in result.itens if i.status == "Priorizado"]
        despriorizados = [i for i in result.itens if i.status == "Despriorizado"]
        
        response = f"""✅ Priorização concluída com sucesso!

📊 **Resumo:**
- Capacidade total: {cap_total}h
- Sustentação ({perc_sust}%): {cap_total * perc_sust / 100}h
- Capacidade para iniciativas: {result.capacidade_iniciativas}h
- Horas alocadas: {result.horas_alocadas}h

✅ **Itens Priorizados ({len(priorizados)}):**
"""
        for item in priorizados[:5]:  # Mostrar top 5
            response += f"\n{item.prioridade}. {item.item} ({item.horas}h)"
        
        if len(priorizados) > 5:
            response += f"\n... e mais {len(priorizados) - 5} itens"
        
        if despriorizados:
            response += f"\n\n❌ **Itens Despriorizados ({len(despriorizados)}):**"
            for item in despriorizados[:3]:
                response += f"\n- {item.item} ({item.horas}h)\n  *Justificativa: {item.justificativa}*"
            if len(despriorizados) > 3:
                response += f"\n... e mais {len(despriorizados) - 3} itens"
        
        response += "\n\nVocê pode visualizar todos os itens atualizados na aba 'Backlog'."
        
        return response
        
    except Exception as e:
        error_details = traceback.format_exc()
        return f"Erro ao executar priorização: {str(e)}\n\nDetalhes técnicos:\n{error_details}"
