# Tarefas de Implementação: Remover Sustentação como Workflow Stage

## Fase 1: Backend - Modelo de Dados
- [ ] 1.1 Atualizar modelo BacklogItem para permitir apenas "upstream" ou "downstream"
- [ ] 1.2 Adicionar validação para rejeitar "sustentacao" como workflow_stage
- [ ] 1.3 Manter capacity_sustentacao_percent no SystemSettings (sem mudanças)
- [ ] 1.4 Atualizar testes do modelo

## Fase 2: Backend - Lógica Central
- [ ] 2.1 Remover contexto de sustentação dos prompts LLM
- [ ] 2.2 Atualizar cálculos de capacidade (se necessário)
- [ ] 2.3 Verificar que lógica de priorização funciona com apenas 2 estágios

## Fase 3: Frontend - Componentes UI
- [ ] 3.1 Remover opção "sustentacao" do dropdown do EditItemModal
- [ ] 3.2 Remover renderização do badge sustentação do BacklogBoard
- [ ] 3.3 Manter slider capacity_sustentacao_percent no SetupPanel
- [ ] 3.4 Atualizar UI para mostrar apenas badges upstream/downstream

## Fase 4: Migração de Dados
- [ ] 4.1 Criar script de migração para converter items sustentação existentes
- [ ] 4.2 Estratégia padrão: Converter para "downstream"
- [ ] 4.3 Testar migração no ambiente dev
- [ ] 4.4 Documentar processo de migração

## Fase 5: Testes
- [ ] 5.1 Atualizar testes unitários para rejeitar sustentação
- [ ] 5.2 Testar cálculos de capacidade com 2 estágios
- [ ] 5.3 Testar UI com apenas 2 opções de estágio
- [ ] 5.4 Testar script de migração

## Fase 6: Documentação
- [ ] 6.1 Atualizar README com explicação correta de workflow stages
- [ ] 6.2 Documentar conceito de reserva de capacidade
- [ ] 6.3 Atualizar guia do usuário (se existir)

## Fase 7: Deploy
- [ ] 7.1 Executar script de migração no dev
- [ ] 7.2 Fazer deploy das mudanças backend
- [ ] 7.3 Fazer deploy das mudanças frontend
- [ ] 7.4 Verificar que nenhum item tem estágio sustentação

## Esforço Estimado
- Backend: 2 horas
- Frontend: 1 hora
- Migração: 1 hora
- Testes: 1 hora
- **Total**: ~5 horas
