# Prioriza Backlog

Agente de priorização de backlog construído em Python + LangChain, agora exposto via FastAPI com integração nativa ao AWS Bedrock.

## Estrutura

- `app/core`: regras de negócio e prompts.
- `app/services`: integrações (LLM, storage).
- `app/main.py`: aplicação FastAPI.
- `agente.py`: CLI interativo para uso local.
- `main_lambda.py`: handler para AWS Lambda.

## Requisitos

- Python 3.11+
- AWS credentials com acesso ao Bedrock e S3.
- Redis (para rate limiting) – use `docker-compose` para subir rapidamente.

Instalação:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Variáveis de ambiente principais

| Nome | Descrição |
| --- | --- |
| `AWS_REGION` | Região usada para Bedrock/S3 (ex.: `us-east-1`). |
| `BEDROCK_MODEL_ID` | Modelo Bedrock (ex.: `anthropic.claude-3-sonnet-20240229-v1:0`). |
| `LLM_PROVIDER` | `bedrock` (default) ou `openai`. |
| `API_KEY_VALUE` | Valor esperado no header `X-API-Key`. Deixe vazio para desativar. |
| `STORAGE_BUCKET` | Bucket S3 para salvar roadmaps (opcional). |
| `REDIS_URL` | URL Redis para rate limiting (`redis://redis:6379/0`). |

## Executar CLI

```bash
python agente.py
```

## Executar a API

```bash
uvicorn app.main:app --reload
```

Endpoints:
- `POST /priorizacoes` – aceita JSON (`PrioritizationRequest`) ou upload CSV (campo `file`) e devolve `PrioritizationResponse`.
- `GET /healthz` – verificação simples.

Com docker-compose (inclui Redis + LocalStack):

```bash
docker-compose up --build
```

## Deploy em AWS

### Lambda + API Gateway

1. Empacote aplicação (Zip com dependências ou use container Lambda).
2. Utilize `main_lambda.py` (handler `main_lambda.handler`).
3. Configure variáveis (API key, Redis – caso use ElastiCache –, bucket S3).

### ECS Fargate

1. Build da imagem: `docker build -t prioriza-backlog .`.
2. Publique no ECR e crie serviço Fargate (atrás de Application Load Balancer).
3. Configure Auto Scaling baseado em CPU/memória e CloudWatch (ex.: requests/min).

## Observabilidade & Segurança

- Logs estruturados com `structlog` (prontos para CloudWatch).
- Rate limiting opcional via Redis (`fastapi-limiter`).
- Autenticação por API Key (`X-API-Key`).
- Segredos recomendados no AWS Secrets Manager/SSM Parameter Store.

## Roadmap Próximo

- Persistência de histórico em DynamoDB.
- Testes automatizados cobrindo fluxo da API.
