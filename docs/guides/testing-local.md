# Guia de Teste Local

## 1. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis (mínimas para teste):

```env
# AWS Bedrock (obrigatório se usar bedrock)
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
LLM_PROVIDER=bedrock

# Ou use OpenAI para teste (alternativa)
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sua-chave-aqui

# Configurações padrão
DEFAULT_CAPACIDADE_TOTAL=1000
DEFAULT_PERCENTUAL_SUSTENTACAO=20

# Deixe vazio para desabilitar (opcional)
API_KEY_VALUE=
REDIS_URL=
STORAGE_BUCKET=
```

**Importante:** Configure suas credenciais AWS (via `aws configure` ou variáveis `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY`).

## 2. Rodar a API

Com o ambiente virtual ativo (`.venv`), execute:

```bash
uvicorn app.main:app --reload
```

A API estará disponível em: `http://localhost:8000`

## 3. Testar os Endpoints

### 3.1 Health Check

```bash
curl http://localhost:8000/healthz
```

### 3.2 Documentação Interativa

Acesse no navegador:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 3.3 Priorizar via CSV (Upload)

```bash
curl -X POST "http://localhost:8000/priorizacoes" \
  -F "file=@demandas.csv" \
  -F "capacidade_total=1000" \
  -F "percentual_sustentacao=20"
```

### 3.4 Priorizar via JSON

```bash
curl -X POST "http://localhost:8000/priorizacoes" \
  -H "Content-Type: application/json" \
  -d '{
    "itens": [
      {
        "item": "Projeto A",
        "horas": 100,
        "cliente": "Sim",
        "negocio": "Sim",
        "financeiro": "Sim",
        "okr": "Sim"
      },
      {
        "item": "Projeto B",
        "horas": 200,
        "cliente": "Não",
        "negocio": "Sim",
        "financeiro": "Não",
        "okr": "Sim"
      }
    ],
    "capacidade_total": 1000,
    "percentual_sustentacao": 20
  }'
```

## 4. Testar via CLI (Script Original)

O script `agente.py` ainda funciona:

```bash
python agente.py
```

Ele pedirá os valores interativamente e usará o mesmo serviço modularizado.

## 5. Verificar Logs

Os logs estruturados aparecerão no console, mostrando:
- Início/fim do processamento
- Chamadas ao LLM
- Uploads para S3 (se configurado)
- Erros (se houver)


