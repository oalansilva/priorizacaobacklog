# Design: Remover Sustentação como Workflow Stage

## Contexto

A implementação atual permite três workflow stages: upstream, downstream e sustentação. No entanto, isso é conceitualmente incorreto:

- **Upstream & Downstream** = Trabalho planejado que passa por descoberta → implementação
- **Sustentação** = Trabalho não planejado e reativo (bugs, hotfixes) que surge organicamente

Misturar trabalho planejado e não planejado no mesmo sistema de workflow stages cria confusão.

## Objetivos

1. Remover "sustentacao" como opção válida de workflow_stage
2. Manter capacity_sustentacao_percent para reserva de capacidade
3. Garantir que todos os PBIs sejam upstream ou downstream
4. Migrar items sustentação existentes de forma graciosa

## Não-Objetivos

- Rastrear trabalho não planejado separadamente (melhoria futura)
- Mudar lógica de cálculo de capacidade
- Remover reserva de capacidade para sustentação

## Decisões Técnicas

### Decisão 1: Workflow de Dois Estágios

**Escolha**: Permitir apenas `workflow_stage ∈ {"upstream", "downstream"}`

**Justificativa**:
- Alinha com o conceito de trabalho planejado
- Simplifica UI e modelo mental do usuário
- Prompts LLM podem focar em descoberta vs. implementação

**Alternativas Consideradas**:
- Manter 3 estágios: Rejeitado - conceitualmente incorreto
- Adicionar estágio "não planejado": Rejeitado - adiciona complexidade sem valor

### Decisão 2: Reserva de Capacidade Permanece

**Escolha**: Manter `capacity_sustentacao_percent` no SystemSettings

**Justificativa**:
- Times ainda precisam reservar capacidade para trabalho não planejado
- Isso é uma preocupação de planejamento de capacidade, não de workflow
- Fórmula: `capacidade_disponivel = capacidade_total * (1 - sustentacao_percent / 100)`

**Exemplo**:
- Capacidade total: 1000h
- **Sustentação (buffer)**: 20% = 200h ← Reservado para trabalho não planejado
- **Disponível para PBIs planejados**: 80% = 800h
  - Upstream: 50% de 800h = 400h
  - Downstream: 50% de 800h = 400h

**Nota**: A sustentação (20%) **É** o buffer. Não há buffer adicional além da sustentação.

### Decisão 3: Estratégia de Migração

**Escolha**: Converter items existentes com `workflow_stage = "sustentacao"` para `"downstream"`

**Justificativa**:
- A maioria do trabalho de sustentação é implementação reativa (bugs, correções)
- Downstream é a correspondência semântica mais próxima
- Migração simples e automatizada

**Alternativas Consideradas**:
- Converter para upstream: Rejeitado - sustentação raramente é trabalho de descoberta
- Revisão manual: Rejeitado - muito demorado, baixo valor
- Deletar items: Rejeitado - perda de dados

## Mudanças no Modelo de Dados

### Antes
```python
workflow_stage: str = "upstream"  # "upstream" | "downstream" | "sustentacao"
```

### Depois
```python
workflow_stage: str = "upstream"  # "upstream" | "downstream"

@field_validator('workflow_stage')
def validate_workflow_stage(cls, v):
    if v not in ["upstream", "downstream"]:
        raise ValueError("workflow_stage deve ser 'upstream' ou 'downstream'")
    return v
```

## Mudanças na UI

### EditItemModal - Antes
```jsx
<select name="workflow_stage">
    <option value="upstream">📋 Upstream</option>
    <option value="downstream">🔨 Downstream</option>
    <option value="sustentacao">🔧 Sustentação</option>  // REMOVER
</select>
```

### EditItemModal - Depois
```jsx
<select name="workflow_stage">
    <option value="upstream">📋 Upstream</option>
    <option value="downstream">🔨 Downstream</option>
</select>
```

## Script de Migração

```python
# scripts/migrate_sustentacao_items.py

from app.core.database import get_repository

def migrate_sustentacao_to_downstream():
    """Converte todos os items com workflow_stage='sustentacao' para 'downstream'."""
    repo = get_repository()
    items = repo.list_items()
    
    migrated_count = 0
    for item in items:
        if item.workflow_stage == "sustentacao":
            item.workflow_stage = "downstream"
            repo.update_item(item)
            migrated_count += 1
            print(f"Migrado: {item.id} - {item.titulo}")
    
    print(f"\nTotal migrado: {migrated_count} items")
    return migrated_count
```

## Riscos e Mitigação

### Risco 1: Confusão do Usuário
**Risco**: Usuários que usaram o estágio sustentação podem ficar confusos

**Mitigação**:
- Comunicação clara sobre a mudança
- Atualizar documentação
- UI mostra apenas 2 opções (sem possibilidade de confusão)

### Risco 2: Perda de Dados
**Risco**: Migração pode falhar ou corromper dados

**Mitigação**:
- Testar migração no ambiente dev primeiro
- Backup das tabelas DynamoDB antes da migração
- Script de migração é idempotente (pode executar múltiplas vezes)

### Risco 3: Compatibilidade Retroativa
**Risco**: Código/clientes antigos podem enviar sustentação

**Mitigação**:
- Adicionar validação para rejeitar workflow_stage inválido
- Retornar mensagem de erro clara
- Frontend previne seleção (defesa primária)

## Plano de Rollback

Se surgirem problemas:

1. **Reverter mudanças de código**: Deploy da versão anterior
2. **Restaurar dados**: Recuperação point-in-time do DynamoDB
3. **Re-executar migração**: Script é idempotente

## Métricas de Sucesso

- ✅ Zero items com `workflow_stage = "sustentacao"`
- ✅ Todos os testes passando
- ✅ UI mostra apenas 2 opções de estágio
- ✅ Cálculos de capacidade funcionam corretamente
- ✅ Nenhuma confusão reportada por usuários

## Cronograma

- **Fase 1-3** (Backend + Frontend): 3 horas
- **Fase 4** (Migração): 1 hora
- **Fase 5** (Testes): 1 hora
- **Fase 6-7** (Docs + Deploy): 1 hora
- **Total**: ~6 horas (1 dia)
