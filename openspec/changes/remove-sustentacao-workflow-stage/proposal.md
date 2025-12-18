# Remover Sustentação como Workflow Stage

## Declaração do Problema

Atualmente, o sistema permite que PBIs (Product Backlog Items) sejam marcados com `workflow_stage = "sustentacao"`. Isso é conceitualmente incorreto porque:

1. **Sustentação não é trabalho planejado** - Representa trabalho orgânico e reativo (bugs, hotfixes, tickets de suporte) que surge durante o quarter
2. **PBIs são trabalho planejado** - Eles passam pelos estágios Upstream (descoberta/design) e Downstream (implementação)
3. **Reserva de capacidade vs. planejamento de trabalho** - Sustentação deve ser apenas uma reserva de capacidade (ex: 20% da capacidade do time), não um estágio de workflow para itens planejados

## Comportamento Atual (Incorreto)

- Usuários podem selecionar "sustentacao" como workflow stage ao criar/editar PBIs
- Items podem ser marcados como `workflow_stage = "sustentacao"`
- O sistema trata sustentação como equivalente a upstream/downstream

## Comportamento Desejado (Correto)

- **Apenas dois workflow stages válidos**: `upstream` e `downstream`
- **Sustentação permanece como reserva de capacidade**: `capacity_sustentacao_percent` (ex: 20%)
- **Nenhum PBI marcado como sustentação**: Itens planejados devem ser upstream ou downstream
- **Cálculo de capacidade**: Capacidade total - reserva de sustentação = disponível para trabalho planejado (upstream + downstream)

## Impacto

### Componentes Afetados

**Backend**:
- `app/models/db.py` - Validação do BacklogItem
- `app/core/capacity.py` - Cálculos de capacidade (sem mudanças necessárias)
- `app/core/prompts.py` - Remover descrição do estágio sustentação

**Frontend**:
- `app/static/components/EditItemModal.jsx` - Remover opção sustentação do dropdown
- `app/static/components/BacklogBoard.jsx` - Remover renderização do badge sustentação

**Banco de Dados**:
- Items existentes com `workflow_stage = "sustentacao"` precisam de migração
- DynamoDB: Sem mudança de schema necessária (schemaless)

### Estratégia de Migração

**Para items existentes com `workflow_stage = "sustentacao"`**:
- Opção A: Converter para `"downstream"` (padrão)
- Opção B: Converter para `"upstream"` se ainda não implementado
- Opção C: Revisão manual e atribuição

## Benefícios

1. **Clareza conceitual**: Workflow stages representam apenas trabalho planejado
2. **Planejamento de capacidade correto**: Sustentação é um buffer, não um estágio
3. **Melhor priorização**: LLM foca no contexto upstream/downstream
4. **UI mais simples**: Apenas dois estágios para escolher

## Riscos

- **Migração de dados**: Necessário lidar com items existentes marcados como sustentação
- **Confusão do usuário**: Usuários que já usaram o estágio sustentação precisam de explicação
- **Compatibilidade retroativa**: Necessário lidar com dados antigos graciosamente

## Alternativas Consideradas

1. **Manter sustentação como estágio**: Rejeitado - conceitualmente incorreto
2. **Adicionar rastreamento separado de "trabalho não planejado"**: Melhoria futura, não necessário agora
3. **Remover capacity_sustentacao_percent**: Rejeitado - reserva de capacidade ainda é necessária

## Recomendação

**Prosseguir com a remoção** - A implementação atual está conceitualmente errada. Sustentação deve ser apenas uma reserva de capacidade, não um workflow stage para PBIs planejados.
