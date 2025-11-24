# Massa de Dados de Teste - Backlog

## Resumo

✅ **10 itens diversos** foram criados e adicionados ao banco de dados com sucesso!

## Itens Criados

### 1. **Implementar sistema de cache distribuído**
- **Categoria**: Iniciativa
- **Área**: Backend
- **Esforço**: 80 horas
- **Impactos**: Financeiro ✅ | Negócios ✅ | Cliente ✅ | OKR ✅

### 2. **Corrigir vazamento de memória no módulo de relatórios** 🐛
- **Categoria**: Bug
- **Área**: Backend
- **Esforço**: 40 horas
- **Impactos**: Financeiro ✅ | Negócios ✅ | Cliente ✅

### 3. **Adicionar dark mode na interface**
- **Categoria**: Melhoria
- **Área**: Frontend
- **Esforço**: 60 horas
- **Impactos**: Cliente ✅

### 4. **Pesquisa de viabilidade - Migração para Kubernetes** 🔍
- **Categoria**: Discovery
- **Área**: DevOps
- **Esforço**: 120 horas
- **Impactos**: Financeiro ✅ | Negócios ✅ | OKR ✅

### 5. **Integração com API de pagamento Stripe**
- **Categoria**: Iniciativa
- **Área**: Backend
- **Esforço**: 160 horas
- **Impactos**: Financeiro ✅ | Negócios ✅ | Cliente ✅ | OKR ✅

### 6. **Resolver problema de timeout em exportação de dados** 🐛
- **Categoria**: Bug
- **Área**: Backend
- **Esforço**: 32 horas
- **Impactos**: Negócios ✅ | Cliente ✅

### 7. **Otimizar queries do dashboard principal**
- **Categoria**: Melhoria
- **Área**: Backend
- **Esforço**: 48 horas
- **Impactos**: Negócios ✅ | Cliente ✅ | OKR ✅

### 8. **Implementar autenticação via SSO**
- **Categoria**: Iniciativa
- **Área**: Backend
- **Esforço**: 200 horas
- **Impactos**: Financeiro ✅ | Negócios ✅ | Cliente ✅ | OKR ✅

### 9. **Estudo de IA para recomendação de produtos** 🔍
- **Categoria**: Discovery
- **Área**: Data Science
- **Esforço**: 96 horas
- **Impactos**: Financeiro ✅ | Negócios ✅ | Cliente ✅ | OKR ✅

### 10. **Adicionar testes E2E com Playwright**
- **Categoria**: Melhoria
- **Área**: QA
- **Esforço**: 72 horas
- **Impactos**: Negócios ✅ | OKR ✅

## Estatísticas

- **Total de itens**: 12 (2 anteriores + 10 novos)
- **Esforço total**: 868 horas
- **Categorias**:
  - 3 Iniciativas
  - 2 Bugs
  - 3 Melhorias
  - 2 Discoveries
- **Áreas**:
  - 6 Backend
  - 1 Frontend
  - 1 DevOps
  - 1 Data Science
  - 1 QA

## Arquivos Salvos

📄 **massa_teste_10_itens.json** - Arquivo JSON com todos os itens para reutilização futura

📄 **adicionar_itens_teste.py** - Script Python para adicionar itens ao banco

## Como Usar

### Testar Priorização
```powershell
# Priorizar com configurações padrão
Invoke-WebRequest -Method POST -Uri http://localhost:8000/priorizacoes

# Priorizar com capacidade customizada
Invoke-WebRequest -Method POST -Uri "http://localhost:8000/priorizacoes?capacidade_total=500"
```

### Visualizar Itens
```powershell
# Listar todos os itens
curl http://localhost:8000/items
```

### Adicionar Mais Itens
```powershell
# Executar script novamente (irá adicionar duplicatas)
python adicionar_itens_teste.py
```
