# Exemplo de Uso: Sistema de Workflow Correto

Este documento mostra exemplos práticos de como o sistema deve funcionar após a remoção de sustentação como workflow stage.

## Cenário 1: Configuração Inicial

### Settings (SystemSettings)
```json
{
  "capacidade_total": 1000,
  "percentual_sustentacao": 20,
  "capacity_upstream_percent": 50.0,
  "capacity_downstream_percent": 50.0
}
```

### Cálculo de Capacidade
```python
# 1. Calcular reserva de sustentação
sustentacao_reserva = 1000 × 20% = 200h

# 2. Calcular capacidade disponível para PBIs
capacidade_disponivel = 1000 - 200 = 800h

# 3. Alocar por stage
upstream_capacity = 800 × 50% = 400h
downstream_capacity = 800 × 50% = 400h
```

### Resultado Visual
```
Total: 1000h
├─ 🔧 Sustentação (buffer): 200h ← Não planejado
└─ 📋🔨 PBIs planejados: 800h
   ├─ 📋 Upstream: 400h
   └─ 🔨 Downstream: 400h
```

## Cenário 2: Criação de PBI

### Interface do Usuário
```jsx
// EditItemModal - Dropdown de Workflow Stage
<select name="workflow_stage">
  <option value="upstream">📋 Upstream - Descoberta e Design</option>
  <option value="downstream">🔨 Downstream - Implementação</option>
  // ❌ NÃO TEM: <option value="sustentacao">
</select>
```

### Validação Backend
```python
# BacklogItem - Validação
@field_validator('workflow_stage')
def validate_workflow_stage(cls, v):
    if v not in ["upstream", "downstream"]:
        raise ValueError(
            "workflow_stage deve ser 'upstream' ou 'downstream'. "
            "Sustentação não é um workflow stage válido."
        )
    return v
```

## Cenário 3: Priorização com LLM

### Input para LLM
```python
# Items para priorizar
items_upstream = [
  {"id": "1", "titulo": "Pesquisa de UX", "esforco": 40, "workflow_stage": "upstream"},
  {"id": "2", "titulo": "Design de API", "esforco": 80, "workflow_stage": "upstream"},
  # ... mais items upstream
]

items_downstream = [
  {"id": "10", "titulo": "Implementar login", "esforco": 120, "workflow_stage": "downstream"},
  {"id": "11", "titulo": "API de pagamento", "esforco": 160, "workflow_stage": "downstream"},
  # ... mais items downstream
]

# Capacidade informada ao LLM
capacidade_upstream = 400h  # Já descontou sustentação
capacidade_downstream = 400h  # Já descontou sustentação
```

### Prompt para LLM (Upstream)
```
Você é um experiente Product Manager (PM). 
Sua tarefa é priorizar itens de backlog para um trimestre com 
**400 horas** disponíveis para iniciativas.

⚠️ IMPORTANTE: Esta capacidade JÁ DESCONTOU a reserva de sustentação 
(bugs, hotfixes, suporte). Você deve priorizar APENAS itens planejados 
dentro desta capacidade.

📋 **CONTEXTO: ESTÁGIO UPSTREAM**
Você está priorizando itens de Upstream (descoberta, pesquisa, design).
Estes itens focam em:
- Descoberta e validação de problemas
- Pesquisa de mercado e usuários
- Design de soluções e protótipos
- Análise técnica e viabilidade

Itens Upstream geralmente precedem a implementação (Downstream).
```

### Output do LLM
```json
[
  {
    "id": "1",
    "item": "Pesquisa de UX",
    "horas": 40,
    "status": "Priorizado",
    "justificativa": "Essencial para validar hipóteses antes do desenvolvimento"
  },
  {
    "id": "2",
    "item": "Design de API",
    "horas": 80,
    "status": "Priorizado",
    "justificativa": "Define contratos para o time de desenvolvimento"
  }
  // ... até atingir ~400h
]
```

## Cenário 4: Visualização no Backlog

### BacklogBoard - Cards
```jsx
// Item Upstream
<div className="backlog-card">
  <h3>#1 Pesquisa de UX</h3>
  <span className="badge badge-upstream">📋 Upstream</span>
  <span className="badge badge-status">✅ Priorizado</span>
  <p>40h</p>
</div>

// Item Downstream
<div className="backlog-card">
  <h3>#10 Implementar login</h3>
  <span className="badge badge-downstream">🔨 Downstream</span>
  <span className="badge badge-status">✅ Priorizado</span>
  <p>120h</p>
</div>

// ❌ NÃO EXISTE MAIS:
// <span className="badge badge-sustentacao">🔧 Sustentação</span>
```

## Cenário 5: Configuração de Capacidade

### SetupPanel - Sliders
```jsx
<div className="capacity-allocation">
  <h3>Alocação de Capacidade por Workflow Stage</h3>
  
  {/* Upstream */}
  <div>
    <label>📋 Upstream (%)</label>
    <input type="number" value={50} step={0.1} />
    <p className="help">Descoberta, pesquisa, design</p>
  </div>
  
  {/* Downstream */}
  <div>
    <label>🔨 Downstream (%)</label>
    <input type="number" value={50} step={0.1} />
    <p className="help">Implementação, entrega</p>
  </div>
  
  {/* Validação */}
  <p className="validation">
    Soma: {upstream + downstream}% 
    {upstream + downstream === 100 ? '✅' : '⚠️ Deve somar 100%'}
  </p>
</div>

<div className="sustentacao-reserve">
  <h3>Reserva de Capacidade (Buffer)</h3>
  
  <div>
    <label>🔧 Sustentação (%)</label>
    <input type="number" value={20} />
    <p className="help">
      Reservado para trabalho NÃO PLANEJADO (bugs, hotfixes, suporte).
      Esta capacidade NÃO é alocada para PBIs.
    </p>
  </div>
</div>
```

## Cenário 6: Relatório de Capacidade

### Capacity Summary
```python
{
  "total_capacity": 1000,
  "sustentacao_reserve": 200,  # Buffer para não planejado
  "available_for_pbis": 800,   # Para trabalho planejado
  
  "upstream": {
    "allocated": 400,
    "used": 360,
    "remaining": 40,
    "usage_percent": 90.0
  },
  
  "downstream": {
    "allocated": 400,
    "used": 380,
    "remaining": 20,
    "usage_percent": 95.0
  },
  
  # ❌ NÃO TEM MAIS:
  # "sustentacao": { ... }
}
```

## Cenário 7: Migração de Dados

### Antes da Migração
```json
[
  {"id": "1", "titulo": "Pesquisa UX", "workflow_stage": "upstream"},
  {"id": "2", "titulo": "Corrigir bug X", "workflow_stage": "sustentacao"},  // ❌
  {"id": "3", "titulo": "Implementar API", "workflow_stage": "downstream"}
]
```

### Script de Migração
```python
def migrate_sustentacao_items():
    items = repo.list_items()
    
    for item in items:
        if item.workflow_stage == "sustentacao":
            # Converter para downstream (trabalho reativo é implementação)
            item.workflow_stage = "downstream"
            repo.update_item(item)
            print(f"✅ Migrado: {item.titulo}")
```

### Depois da Migração
```json
[
  {"id": "1", "titulo": "Pesquisa UX", "workflow_stage": "upstream"},
  {"id": "2", "titulo": "Corrigir bug X", "workflow_stage": "downstream"},  // ✅
  {"id": "3", "titulo": "Implementar API", "workflow_stage": "downstream"}
]
```

## Resumo das Regras

### ✅ Permitido
- PBIs com `workflow_stage = "upstream"`
- PBIs com `workflow_stage = "downstream"`
- Configurar `capacity_sustentacao_percent` (reserva de buffer)
- Alocar % entre upstream/downstream (deve somar 100%)

### ❌ NÃO Permitido
- PBIs com `workflow_stage = "sustentacao"`
- Selecionar "sustentação" no dropdown da UI
- Priorizar items de sustentação via LLM
- Alocar capacidade planejada para sustentação

### 🎯 Conceito Chave
**Sustentação é RESERVA, não STAGE**
- 20% da capacidade fica reservada (buffer)
- Trabalho não planejado usa esse buffer
- PBIs planejados usam os outros 80%
- LLM prioriza apenas os 80% disponíveis
