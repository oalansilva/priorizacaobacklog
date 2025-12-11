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

    tools = [add_backlog_item, find_backlog_item_by_title, update_backlog_item, list_backlog_items, check_prioritization_status, prioritize_backlog]

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
    import logging
    logger = logging.getLogger(__name__)
    
    if _repository is None:
        return "Erro: Repositório não inicializado."
    
    try:
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
        
        logger.info(f"Tentando adicionar item: {titulo} (área: {area}, esforço: {esforco_estimado}h)")
        _repository.add_item(item)
        logger.info(f"Item '{titulo}' adicionado com sucesso (ID: {item.id})")
        return f"Item '{titulo}' adicionado com sucesso ao backlog (ID: {item.id})."
        
    except Exception as e:
        error_msg = f"Erro ao adicionar item '{titulo}': {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return f"❌ {error_msg}. Por favor, verifique os logs para mais detalhes."

@tool
def find_backlog_item_by_title(titulo_busca: str) -> str:
    """Busca itens do backlog por título (busca aproximada).
    
    Use esta ferramenta quando o usuário quiser atualizar/editar um item mas não souber o ID.
    A ferramenta busca por títulos que contenham o texto fornecido (case-insensitive).
    
    IMPORTANTE: Após encontrar o(s) item(ns), você DEVE:
    1. Mostrar os resultados ao usuário
    2. Pedir confirmação de qual item ele quer atualizar
    3. Usar o ID confirmado para chamar update_backlog_item
    
    Args:
        titulo_busca: Texto para buscar no título (pode ser parte do título)
    
    Returns:
        Lista de itens encontrados com ID, título e outras informações
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if _repository is None:
        return "Erro: Repositório não inicializado."
    
    try:
        logger.info(f"Buscando itens com título contendo: '{titulo_busca}'")
        items = _repository.list_items()
        
        if not items:
            return "O backlog está vazio."
        
        # Busca case-insensitive
        titulo_lower = titulo_busca.lower()
        matches = [item for item in items if titulo_lower in item.titulo.lower()]
        
        if not matches:
            return f"❌ Nenhum item encontrado com título contendo '{titulo_busca}'.\n\nTente usar palavras-chave diferentes ou liste todos os itens."
        
        if len(matches) == 1:
            item = matches[0]
            return f"""✅ **Encontrei 1 item:**

📋 **Título:** {item.titulo}
🆔 **ID:** `{item.id}`
⏱️ **Esforço:** {item.esforco_estimado}h
📂 **Área:** {item.area}
📊 **Status:** {item.status}

**Este é o item que você quer atualizar?** Se sim, me diga quais campos você quer alterar."""
        
        # Múltiplos resultados
        result = f"✅ **Encontrei {len(matches)} itens:**\n\n"
        for i, item in enumerate(matches, 1):
            result += f"""**{i}. {item.titulo}**
   🆔 ID: `{item.id}`
   ⏱️ Esforço: {item.esforco_estimado}h | 📂 Área: {item.area} | 📊 Status: {item.status}

"""
        
        result += "**Qual desses itens você quer atualizar?** Me diga o número ou o título completo."
        return result
        
    except Exception as e:
        error_msg = f"Erro ao buscar item: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return f"❌ {error_msg}"

@tool
def update_backlog_item(
    item_id: str,
    titulo: Optional[str] = None,
    descricao: Optional[str] = None,
    esforco_estimado: Optional[int] = None,
    area: Optional[str] = None,
    categoria: Optional[str] = None,
    impacto_financeiro: Optional[str] = None,
    impacto_negocios: Optional[str] = None,
    impacto_cliente: Optional[str] = None,
    okr: Optional[str] = None,
    must_have: Optional[str] = None,
    estimado_qp: Optional[str] = None
) -> str:
    """Atualiza um item existente do backlog.
    
    Use esta ferramenta quando o usuário pedir para:
    - "atualizar item"
    - "editar item"
    - "alterar item"
    - "modificar item"
    
    Args:
        item_id: ID do item a ser atualizado (obrigatório)
        titulo: Novo título (opcional)
        descricao: Nova descrição (opcional)
        esforco_estimado: Novo esforço em horas (opcional)
        area: Nova área (opcional)
        categoria: Nova categoria (opcional)
        impacto_financeiro: 'Sim' ou 'Não' (opcional)
        impacto_negocios: 'Sim' ou 'Não' (opcional)
        impacto_cliente: 'Sim' ou 'Não' (opcional)
        okr: 'Sim' ou 'Não' (opcional)
        must_have: 'Sim' ou 'Não' (opcional)
        estimado_qp: 'Sim' ou 'Não' (opcional)
    
    Returns:
        Mensagem de sucesso ou erro
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if _repository is None:
        return "Erro: Repositório não inicializado."
    
    try:
        # Buscar item existente
        logger.info(f"Buscando item com ID: {item_id}")
        items = _repository.list_items()
        item = next((i for i in items if i.id == item_id), None)
        
        if not item:
            logger.warning(f"Item não encontrado: {item_id}")
            return f"❌ Item com ID '{item_id}' não foi encontrado no backlog."
        
        # Guardar valores originais para logging
        original_values = {}
        updated_fields = []
        
        # Atualizar apenas os campos fornecidos (não None)
        if titulo is not None:
            original_values['titulo'] = item.titulo
            item.titulo = titulo
            updated_fields.append(f"título: '{original_values['titulo']}' → '{titulo}'")
        
        if descricao is not None:
            original_values['descricao'] = item.descricao[:50] + "..." if len(item.descricao) > 50 else item.descricao
            item.descricao = descricao
            updated_fields.append("descrição")
        
        if esforco_estimado is not None:
            original_values['esforco_estimado'] = item.esforco_estimado
            item.esforco_estimado = esforco_estimado
            updated_fields.append(f"esforço: {original_values['esforco_estimado']}h → {esforco_estimado}h")
        
        if area is not None:
            original_values['area'] = item.area
            item.area = area
            updated_fields.append(f"área: '{original_values['area']}' → '{area}'")
        
        if categoria is not None:
            original_values['categoria'] = item.categoria
            item.categoria = categoria
            updated_fields.append(f"categoria: '{original_values['categoria']}' → '{categoria}'")
        
        if impacto_financeiro is not None:
            original_values['impacto_financeiro'] = item.impacto_financeiro
            item.impacto_financeiro = impacto_financeiro
            updated_fields.append(f"impacto financeiro: {original_values['impacto_financeiro']} → {impacto_financeiro}")
        
        if impacto_negocios is not None:
            original_values['impacto_negocios'] = item.impacto_negocios
            item.impacto_negocios = impacto_negocios
            updated_fields.append(f"impacto negócios: {original_values['impacto_negocios']} → {impacto_negocios}")
        
        if impacto_cliente is not None:
            original_values['impacto_cliente'] = item.impacto_cliente
            item.impacto_cliente = impacto_cliente
            updated_fields.append(f"impacto cliente: {original_values['impacto_cliente']} → {impacto_cliente}")
        
        if okr is not None:
            original_values['okr'] = item.okr
            item.okr = okr
            updated_fields.append(f"OKR: {original_values['okr']} → {okr}")
        
        if must_have is not None:
            original_values['must_have'] = item.must_have
            item.must_have = must_have
            updated_fields.append(f"must have: {original_values['must_have']} → {must_have}")
        
        if estimado_qp is not None:
            original_values['estimado_qp'] = item.estimado_qp
            item.estimado_qp = estimado_qp
            updated_fields.append(f"estimado QP: {original_values['estimado_qp']} → {estimado_qp}")
        
        if not updated_fields:
            return "⚠️ Nenhum campo foi especificado para atualização. Por favor, forneça pelo menos um campo para atualizar."
        
        # Atualizar no repositório
        logger.info(f"Atualizando item '{item.titulo}' (ID: {item_id}). Campos alterados: {', '.join(updated_fields)}")
        _repository.update_item(item)
        logger.info(f"Item '{item.titulo}' atualizado com sucesso")
        
        # Mensagem de sucesso detalhada
        changes_summary = "\n".join([f"  • {field}" for field in updated_fields])
        return f"""✅ Item '{item.titulo}' atualizado com sucesso!

📝 **Alterações realizadas:**
{changes_summary}"""
        
    except Exception as e:
        error_msg = f"Erro ao atualizar item '{item_id}': {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return f"❌ {error_msg}. Por favor, verifique os logs para mais detalhes."

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
        # Limpar status anterior e marcar como running
        settings_db.last_prioritization_status = "running"
        settings_db.last_prioritization_message = None
        _repository.update_settings(settings_db)
        
        # Verificar se estamos em ambiente Lambda
        import os
        import json
        import boto3
        import threading
        
        is_lambda = os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None
        
        if is_lambda:
            # Invocar a própria função Lambda assincronamente
            lambda_client = boto3.client('lambda')
            function_name = os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
            
            payload = {
                "type": "async_task",
                "action": "prioritize",
                "capacidade_total": cap_total,
                "percentual_sustentacao": perc_sust
            }
            
            lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='Event',  # Asynchronous invocation
                Payload=json.dumps(payload)
            )
            print("Invoked Async Lambda for prioritization")
            
        else:
            # Ambiente local: usar Thread
            def run_prioritization_async_local():
                try:
                    from app.main import execute_prioritization
                    from datetime import datetime
                    
                    result = execute_prioritization(
                        capacidade_total=cap_total,
                        percentual_sustentacao=perc_sust
                    )
                    
                    priorizados = [i for i in result.itens if i.status == "Priorizado"]
                    completion_message = f"""✅ **Priorização concluída!**

📊 **Resultados:**
- {len(priorizados)} itens priorizados de {len(result.itens)} total
- Capacidade: {result.capacidade_iniciativas}h
- Alocado: {result.horas_alocadas}h

Veja todos os detalhes na aba 'Backlog'!"""
                    
                    # Recarregar settings para garantir freshness
                    current_settings = _repository.get_settings()
                    current_settings.last_prioritization_status = "completed"
                    current_settings.last_prioritization_message = completion_message
                    from datetime import datetime, timezone, timedelta
                    
                    # São Paulo timezone (UTC-3)
                    sao_paulo_tz = timezone(timedelta(hours=-3))
                    current_settings.last_prioritization_time = datetime.now(sao_paulo_tz).isoformat()
                    _repository.update_settings(current_settings)
                    
                except Exception as e:
                    import traceback
                    print(f"Background prioritization error: {e}")
                    print(traceback.format_exc())
                    
                    try:
                        current_settings = _repository.get_settings()
                        current_settings.last_prioritization_status = "error"
                        current_settings.last_prioritization_message = f"Erro: {str(e)}"
                        _repository.update_settings(current_settings)
                    except:
                        pass

            thread = threading.Thread(target=run_prioritization_async_local, daemon=True)
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
