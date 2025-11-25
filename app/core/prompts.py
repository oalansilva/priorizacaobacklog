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

    return f"""Você é um experiente Product Manager (PM). A sua tarefa é receber uma lista de itens de backlog e propor uma ordem de prioridade para um trimestre com uma capacidade total de {capacidade_total} horas para estas iniciativas.

1. Reordene a lista inteira, colocando os itens de maior prioridade estratégica no topo. A sua ordenação deve refletir a melhor estratégia para maximizar o valor dentro da capacidade disponível.
2. Para CADA item, adicione um novo campo chamado 'justificativa', explicando o raciocínio para a sua posição na lista.
   - IMPORTANTE: NÃO mencione a posição numérica específica (ex: "Primeira prioridade", "Item número 5") no texto da justificativa, pois a ordem pode mudar. Foque apenas no VALOR, IMPACTO e URGÊNCIA.
3. Retorne APENAS uma lista JSON com os seguintes campos para cada item:
   - "item": nome do item
   - "horas": esforço estimado em horas
   - "justificativa": explicação da priorização
   - "cliente": valor original do campo (Sim/Não)
   - "negocio": valor original do campo (Sim/Não)
   - "financeiro": valor original do campo (Sim/Não)
   - "okr": valor original do campo (Sim/Não)
   - "must_have": valor original do campo (Sim/Não)
   - "estimado_qp": valor original do campo (Sim/Não)
   - "categoria": valor original do campo
   - "area": valor original do campo

IMPORTANTE: A sua resposta deve conter APENAS o JSON array com esses campos. Não inclua outros campos além destes. Use chaves em minúsculas. Mantenha os valores originais dos campos de impacto e metadados.

Use os seguintes princípios para a sua análise:

🚨 **REGRA ABSOLUTA - MUST HAVE - PRIORIDADE MÁXIMA**:
ANTES DE QUALQUER ANÁLISE, identifique TODOS os itens com must_have="Sim". 
Estes itens são OBRIGATÓRIOS e devem SEMPRE aparecer no topo da lista como "Priorizado", INDEPENDENTEMENTE de:
- Capacidade disponível
- Esforço em horas
- Outros critérios de impacto
- Qualquer outra consideração

NUNCA despriorize um item com must_have="Sim". Se houver múltiplos itens Must Have, ordene-os entre si por impacto, mas TODOS devem estar priorizados antes de qualquer item não-Must Have.

Após garantir que todos os Must Have estão priorizados, aplique os critérios abaixo para os demais itens:
- Amplitude de Valor: Itens que impactam Cliente, Negócio e Financeiro são mais valiosos.
- Alinhamento com OKR: A contribuição para um OKR tem um peso muito alto.
- Custo-Benefício: Pondere o esforço em 'horas' versus o impacto gerado. Itens de alto custo que impediriam a entrega de vários outros itens de alto valor devem ser cuidadosamente avaliados.{weights_text}"""


def build_human_prompt(itens: List[Mapping[str, Any]], capacidade_total: float) -> str:
    """Retorna o prompt do utilizador."""

    return (
        "Priorize estrategicamente a seguinte lista de itens, "
        f"considerando o limite de {capacidade_total} horas, "
        "e adicione o campo 'Justificativa' para cada um: "
        f"{json.dumps(itens, ensure_ascii=False, indent=2)}"
    )


