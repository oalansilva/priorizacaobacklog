"""Funções utilitárias para construção dos prompts."""

from __future__ import annotations

import json
from typing import List, Mapping, Any


def build_system_prompt(capacidade_total: float, weights: Mapping[str, int] = None) -> str:
    """Retorna o prompt de sistema com instruções estratégicas."""

    weights_text = ""
    if weights:
        weights_text = "\n\nConsidere os seguintes pesos para a priorização (0-100%):\n"
        weights_text += f"- Impacto Financeiro: {weights.get('peso_financeiro', 25)}%\n"
        weights_text += f"- Impacto Negócios: {weights.get('peso_negocios', 25)}%\n"
        weights_text += f"- Impacto Cliente: {weights.get('peso_cliente', 25)}%\n"
        weights_text += f"- OKR: {weights.get('peso_okr', 25)}%\n"
        weights_text += "Itens com critérios de maior peso devem ter preferência na lista.\n"
        weights_text += "IMPORTANTE: O campo 'estimado_qp' é apenas informativo (indica se o item foi estimado no Quarter Planning) e NÃO deve influenciar a priorização."

    return f"""Você é um experiente Product Manager (PM). Sua tarefa é priorizar itens de backlog para um trimestre com **{capacidade_total} horas** disponíveis para iniciativas.

**IMPORTANTE**: Você deve decidir quais itens cabem dentro da capacidade e atribuir o status correspondente.

Para CADA item, retorne os seguintes campos:
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
