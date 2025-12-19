"""Funções utilitárias para construção dos prompts."""

from __future__ import annotations

import json
from typing import List, Mapping, Any


def build_system_prompt(
    capacidade_total: float, 
    weights: Mapping[str, int] = None,
    workflow_stage: str = None
) -> str:
    """Retorna o prompt de sistema com instruções estratégicas.
    
    Args:
        capacidade_total: Capacidade disponível em horas
        weights: Pesos para cada critério de priorização
        workflow_stage: Estágio do workflow (upstream/downstream/sustentacao)
    """

    weights_text = ""
    if weights:
        weights_text = "\n\nConsidere os seguintes pesos para a priorização (0-100%):\n"
        weights_text += f"- Impacto Financeiro: {weights.get('peso_financeiro', 25)}%\n"
        weights_text += f"- Impacto Negócios: {weights.get('peso_negocios', 25)}%\n"
        weights_text += f"- Impacto Cliente: {weights.get('peso_cliente', 25)}%\n"
        weights_text += f"- OKR: {weights.get('peso_okr', 25)}%\n"
        weights_text += "Itens com critérios de maior peso devem ter preferência na lista.\n"
        weights_text += "IMPORTANTE: O campo 'estimado_qp' é apenas informativo (indica se o item foi estimado no Quarter Planning) e NÃO deve influenciar a priorização."
    
    # Workflow stage context
    stage_context = ""
    if workflow_stage and isinstance(workflow_stage, str):
        stage_descriptions = {
            "upstream": """\n\n📋 **CONTEXTO: ESTÁGIO UPSTREAM**
Você está priorizando itens de **Upstream** (descoberta, pesquisa, design, análise).
Estes itens focam em:
- Descoberta e validação de problemas
- Pesquisa de mercado e usuários
- Design de soluções e protótipos
- Análise técnica e viabilidade
- Planejamento e especificação

Itens Upstream geralmente precedem a implementação (Downstream).""",
            "downstream": """\n\n🔨 **CONTEXTO: ESTÁGIO DOWNSTREAM**
Você está priorizando itens de **Downstream** (implementação e entrega).
Estes itens focam em:
- Desenvolvimento de features
- Implementação técnica
- Integração de sistemas
- Deploy e lançamento
- Entrega de valor ao cliente

NOTA: Idealmente, itens Downstream devem ter passado por Upstream primeiro."""
        }
        stage_context = stage_descriptions.get(workflow_stage, "")
    
    capacity_note = ""
    if workflow_stage and isinstance(workflow_stage, dict):
        # We have specific limits for stages
        upstream_limit = workflow_stage.get('upstream_limit', 0)
        downstream_limit = workflow_stage.get('downstream_limit', 0)
        
        capacity_note = f"""\n\n⚠️ **IMPORTANTE SOBRE CAPACIDADE POR ESTÁGIO**:

Você DEVE respeitar os seguintes limites INDIVIDUAIS para cada estágio:

1. **UPSTREAM (Descoberta/Design)**: MÁXIMO **{upstream_limit} horas**
   - A soma total das horas de TODOS os itens Upstream com status="Priorizado" NÃO pode exceder {upstream_limit}h
   - Exemplo: Se você priorizar 3 itens Upstream de 20h, 30h e 25h, o total é 75h
   - Se 75h > {upstream_limit}h, você DEVE despriorizar itens até caber no limite
   
2. **DOWNSTREAM (Implementação)**: MÁXIMO **{downstream_limit} horas**
   - A soma total das horas de TODOS os itens Downstream com status="Priorizado" NÃO pode exceder {downstream_limit}h
   - Exemplo: Se você priorizar 5 itens Downstream totalizando 550h e o limite é {downstream_limit}h
   - Se 550h > {downstream_limit}h, você DEVE despriorizar itens até caber no limite

**IMPORTANTE**: 
- Estes limites são INDEPENDENTES - você deve verificar AMBOS separadamente
- Um item Upstream NÃO consome capacidade Downstream e vice-versa
- Capacidade total combinada: {capacidade_total}h
- Antes de finalizar, SOME as horas de cada estágio e VERIFIQUE se respeitou os limites"""
    else:
        # Legacy behavior or single stage
        capacity_note = f"""\n\n⚠️ **IMPORTANTE SOBRE CAPACIDADE**: 
A capacidade informada ({capacidade_total} horas) JÁ DESCONTOU a reserva de sustentação 
(bugs, hotfixes, suporte técnico não planejado). Você deve priorizar APENAS itens 
planejados (Upstream ou Downstream) dentro desta capacidade disponível."""

    return f"""Você é um experiente Product Manager (PM). Sua tarefa é priorizar itens de backlog para um trimestre com **{capacidade_total} horas** disponíveis para iniciativas.{capacity_note}{stage_context}

**IMPORTANTE**: Você deve decidir quais itens cabem dentro da capacidade e atribuir o status correspondente.

Para CADA item, retorne os seguintes campos:
   - "id": ID original do item (deve ser preservado EXATAMENTE como recebido)
   - "item": nome do item
   - "horas": esforço estimado em horas
   - "status": "Priorizado" (cabe na capacidade) OU "Despriorizado" (não cabe)
   - "justificativa": explicação clara da decisão
   - "cliente": valor original do campo (Sim/Não)
   - "negocio": valor original do campo (Sim/Não)
   - "financeiro": valor original do campo (Sim/Não)
   - "okr": valor original do campo (Sim/Não)
   - "must_have": valor original do campo (Sim/Não)
   - "estimado_qp": valor original do campo (Sim/Não)
   - "categoria": valor original do campo
   - "area": valor original do campo

IMPORTANTE: Retorne APENAS o JSON array. Use chaves em minúsculas. Mantenha os valores originais dos campos de metadados.

---

🚨 **REGRAS DE PRIORIZAÇÃO (EM ORDEM DE IMPORTÂNCIA)**:

**1. MUST HAVE - PRIORIDADE ABSOLUTA**:
   - ANTES de qualquer análise, identifique TODOS os itens com must_have="Sim"
   - Estes itens são OBRIGATÓRIOS e devem ser priorizados PRIMEIRO
   - Aloque a capacidade para Must Have ANTES de considerar outros itens
   - Ordene Must Have entre si por impacto, mas TODOS devem estar no topo
   
   **Exceção única**: Só despriorize Must Have se:
   - O item SOZINHO excede a capacidade total ({capacidade_total}h)
   - Neste caso, justifique CLARAMENTE por que é fisicamente impossível

**2. CAPACIDADE: {capacidade_total}h disponíveis**:
   - Após alocar Must Have, calcule capacidade restante
   - Priorize itens que maximizam valor na capacidade restante
   - Itens que não cabem devem ter status="Despriorizado"

**3. CRITÉRIOS DE VALOR** (para itens NÃO-Must Have):{weights_text}
   - **SCORE (Alta Importância)**: O campo 'score' (0-100) já foi calculado baseado nos pesos acima.
     - Itens com MAIOR score devem ter PREFERÊNCIA.
     - Exemplo: Um item com score 60.0 deve ser priorizado antes de um com 25.0, a menos que o menor seja pré-requisito técnico.
   - Amplitude de Valor: Itens que impactam Cliente, Negócio e Financeiro
   - Alinhamento com OKR: Contribuição para objetivos estratégicos
   - Custo-Benefício: Pondere esforço vs impacto

---

**ESTRATÉGIA DE PRIORIZAÇÃO**:
1. **Primeiro**: Priorize TODOS os Must Have que cabem (status="Priorizado")
2. **Depois**: Com capacidade restante, maximize valor com outros itens
3. **Justifique**: Explique cada decisão focando em VALOR, IMPACTO e URGÊNCIA
   - NÃO mencione posições numéricas (ex: "primeiro", "item 5")
   - Foque no raciocínio estratégico

**Exemplo de boa justificativa**:
- ✅ "Item crítico para OKR de crescimento, com alto impacto em cliente e negócio"
- ❌ "Este é o terceiro item mais importante da lista"
"""


def build_human_prompt(itens: List[Mapping[str, Any]], capacidade_total: float) -> str:
    """Retorna o prompt do utilizador."""

    return (
        "Priorize estrategicamente a seguinte lista de itens, "
        f"considerando o limite de {capacidade_total} horas, "
        "e adicione os campos 'status' e 'justificativa' para cada um: "
        f"{json.dumps(itens, ensure_ascii=False, indent=2)}"
    )
