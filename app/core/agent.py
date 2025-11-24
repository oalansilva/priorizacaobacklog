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
    
    settings = get_settings()
    llm = ChatOpenAI(
        model="gpt-4-turbo-preview", 
        temperature=0,
        api_key=settings.openai_api_key
    )

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
def prioritize_backlog(capacidade_total: int = 100, percentual_sustentacao: int = 20) -> str:
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
        capacidade_total: Total de horas disponíveis para o trimestre (padrão: 100)
        percentual_sustentacao: Percentual da capacidade reservado para sustentação (padrão: 20)
    
    Returns:
        Resumo da priorização executada com itens priorizados e despriorizados
    """
    if _repository is None:
        return "Erro: Repositório não inicializado."
    
    items = _repository.list_items()
    if not items:
        return "Não há itens para priorizar."

    try:
        # Converter itens do banco para DataFrame
        items_data = []
        for item in items:
            items_data.append({
                'item': item.titulo,
                'horas': item.esforco_estimado,
                'negocio': None,
                'cliente': None,
                'financeiro': None,
                'okr': None,
                'area': item.area,
                'descricao': item.descricao
            })
        
        df = pd.DataFrame(items_data)
        
        # Executar priorização usando o serviço existente
        settings = get_settings()
        prioritization_service = PrioritizationService(settings=settings)
        
        result = prioritization_service.process_dataframe(
            df,
            capacidade_total=capacidade_total,
            percentual_sustentacao=percentual_sustentacao
        )
        
        # Atualizar status dos itens no banco de dados
        for prioritized_item in result.itens:
            # Encontrar o item original pelo título
            original_item = next((i for i in items if i.titulo == prioritized_item.item), None)
            if original_item:
                original_item.status = prioritized_item.status
                _repository.update_item(original_item)
        
        # Montar resposta formatada
        priorizados = [i for i in result.itens if i.status == "Priorizado"]
        despriorizados = [i for i in result.itens if i.status == "Despriorizado"]
        
        response = f"""✅ Priorização concluída com sucesso!

📊 **Resumo:**
- Capacidade total: {capacidade_total}h
- Sustentação ({percentual_sustentacao}%): {capacidade_total * percentual_sustentacao / 100}h
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
                response += f"\n- {item.item} ({item.horas}h)"
            if len(despriorizados) > 3:
                response += f"\n... e mais {len(despriorizados) - 3} itens"
        
        response += "\n\nVocê pode visualizar todos os itens atualizados na aba 'Backlog'."
        
        return response
        
    except Exception as e:
        error_details = traceback.format_exc()
        return f"Erro ao executar priorização: {str(e)}\n\nDetalhes técnicos:\n{error_details}"
