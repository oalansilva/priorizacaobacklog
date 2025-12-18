# Project Context

## Purpose
ARCADIA (formerly "Gênio Priorizador") is a smart backlog prioritization system using AI (AWS Bedrock, Claude) and LangChain. It automates the prioritization of backlog items based on customizable criteria (e.g., Must Have, financial impact, strategic alignment) and ensures capacity constraints are respected.

## Tech Stack
- **Backend**: Python 3.11+, FastAPI
- **AI/LLM**: LangChain, AWS Bedrock (Claude models)
- **Database**:
    - Local: SQLite
    - Production (AWS): DynamoDB
- **Infrastructure**: AWS Lambda (serverless via Mangum), Docker
- **Frontend**: React (embedded in `app/static` or served separately)

## Project Conventions

### Code Style
- **Python**: Follows PEP8. Uses `ruff` for linting.
- **JavaScript/React**: Standard React practices.
- **Documentation**: Markdown files in `docs/` (kebab-case filenames).

### Architecture Patterns
- **Serverless**: The application is designed to run as an AWS Lambda function behind API Gateway.
- **Pattern**: Repository pattern for database access (`SQLiteRepository`, `DynamoDBRepository`).
- **Service Layer**: Business logic resides in `app/services` and `app/core`.

### Testing Strategy
- **Framework**: `pytest`
- **Scope**: Unit tests (`test_*.py` in root) and integration tests.
- **Data**: Uses test data generation scripts in `scripts/`.

### Git Workflow
- Manual commits to the main repository.
- Detailed commit messages describing changes.

## Domain Context
- **Backlog Item**: A task or feature request with attributes like `financeiro`, `negocio`, `cliente`, `okr` (impacts), and `status`.
- **Prioritization**: The process of ranking items. "Must Have" items get top priority (100% score). others are scored based on weights.
- **Capacity**: A limit (e.g., hours or points) that restricts how many items can be "Prioritized".
- **Self-Correction**: The system validates LLM output and asks it to correct itself if the output format is invalid.

## Important Constraints
- **AWS Lambda**: Execution time limits (timeout set to 60s+), read-only filesystem (except `/tmp`).
- **Statelessness**: The API must be stateless.
- **Timezone**: Times must be displayed in São Paulo (UTC-3).

## External Dependencies
- **AWS Services**: Bedrock, DynamoDB, Lambda, CloudWatch.
- **LLM Providers**: Anthropic (via Bedrock).
