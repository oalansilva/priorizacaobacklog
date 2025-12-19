# Remover Campo Legado `percentual_sustentacao`

## Declaração do Problema

Atualmente, o sistema tem **dois mecanismos diferentes** para configurar a reserva de sustentação:

1. **Campo legado**: `percentual_sustentacao` (ex: 20%)
2. **Campo novo**: `capacity_sustentacao_percent` (ex: 20%)

Isso cria **confusão e redundância**:
- Qual campo usar?
- O que acontece se os valores forem diferentes?
- Como o sistema calcula a capacidade disponível?

## Comportamento Atual (Confuso)

### SystemSettings tem ambos os campos:
```python
class SystemSettings:
    capacidade_total: int = 1000
    percentual_sustentacao: int = 20  # ❌ LEGADO - usado no cálculo antigo
    
    capacity_upstream_percent: float = 40.0
    capacity_downstream_percent: float = 40.0
    capacity_sustentacao_percent: float = 20.0  # ✅ NOVO - parte do sistema de 3 stages
```

### Cálculo de capacidade usa o campo legado:
```python
def _calcular_capacidade_iniciativas(capacidade_total, percentual_sustentacao):
    sustentacao = (capacidade_total * percentual_sustentacao) / 100  # ❌ Usa campo legado
    return capacidade_total - sustentacao
```

### Frontend mostra ambos:
- **SetupPanel** tem "Reserva para Sustentação (%)" - campo legado
- **SetupPanel** tem "Alocação de Capacidade" com 3 sliders - sistema novo

## Comportamento Desejado (Correto)

### Apenas um sistema de alocação:
```python
class SystemSettings:
    capacidade_total: int = 1000
    
    # Sistema unificado - soma = 100%
    capacity_upstream_percent: float = 40.0
    capacity_downstream_percent: float = 40.0
    capacity_sustentacao_percent: float = 20.0
    
    # ❌ REMOVER: percentual_sustentacao
```

### Cálculo simplificado:
```python
# Capacidade por stage (direto da capacidade total)
upstream_capacity = capacidade_total * (capacity_upstream_percent / 100)
downstream_capacity = capacidade_total * (capacity_downstream_percent / 100)
sustentacao_capacity = capacidade_total * (capacity_sustentacao_percent / 100)

# Disponível para PBIs planejados
available_for_pbis = upstream_capacity + downstream_capacity
```

### Frontend unificado:
- **Apenas** "Alocação de Capacidade por Workflow Stage"
- 3 sliders que somam 100%
- Sem campo separado de "Reserva para Sustentação"

## Impacto

### Componentes Afetados

**Backend**:
- `app/models/db.py` - Remover `percentual_sustentacao` do SystemSettings
- `app/core/prioritization.py` - Atualizar `_calcular_capacidade_iniciativas`
- `app/core/capacity.py` - Já usa o sistema novo (sem mudanças)

**Frontend**:
- `app/static/components/SetupPanel.jsx` - Remover campo legado

**Database**:
- Campo `percentual_sustentacao` pode permanecer no DB (backward compatibility)
- Não será mais usado pelo código

### Migração

**Não é necessária migração de dados!**
- Campo antigo pode permanecer no banco
- Código simplesmente ignora ele
- Se alguém tiver valores diferentes, o novo sistema prevalece

## Benefícios

1. **Clareza conceitual**: Um único sistema de alocação
2. **UI mais simples**: Apenas um conjunto de sliders
3. **Cálculo mais direto**: Sem conversões entre sistemas
4. **Menos confusão**: Não há dois campos para a mesma coisa

## Riscos

- **Baixo risco**: Campo legado não será removido do DB, apenas ignorado
- **Backward compatibility**: Código antigo pode ter usado `percentual_sustentacao`
- **Migração suave**: Usuários verão apenas o sistema novo

## Alternativas Consideradas

1. **Manter ambos os campos**: Rejeitado - confuso e redundante
2. **Migrar valores automaticamente**: Não necessário - sistema novo já funciona
3. **Remover do DB também**: Rejeitado - pode quebrar código legado

## Recomendação

**Prosseguir com a remoção do código que usa `percentual_sustentacao`** - O sistema novo (`capacity_*_percent`) é mais claro e completo. O campo legado pode permanecer no DB para compatibilidade, mas o código deve usar apenas o sistema novo.
