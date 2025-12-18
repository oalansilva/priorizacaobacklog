# Tarefas: Remover Campo Legado percentual_sustentacao

## Fase 1: Backend - Cálculo de Capacidade
- [ ] 1.1 Atualizar `_calcular_capacidade_iniciativas` em `prioritization.py`
- [ ] 1.2 Usar `capacity_sustentacao_percent` em vez de `percentual_sustentacao`
- [ ] 1.3 Calcular capacidade disponível corretamente
- [ ] 1.4 Testar cálculos

## Fase 2: Frontend - SetupPanel
- [ ] 2.1 Remover campo "Reserva para Sustentação (%)"
- [ ] 2.2 Manter apenas "Alocação de Capacidade por Workflow Stage"
- [ ] 2.3 Atualizar validação (soma = 100%)

## Fase 3: Testes
- [ ] 3.1 Testar cálculo de capacidade
- [ ] 3.2 Verificar que sustentação é calculada corretamente
- [ ] 3.3 Testar UI

## Fase 4: Deploy
- [ ] 4.1 Deploy backend
- [ ] 4.2 Deploy frontend
- [ ] 4.3 Verificar funcionamento

## Esforço Estimado
- Backend: 30 minutos
- Frontend: 15 minutos
- Testes: 15 minutos
- **Total**: ~1 hora
