# 🎯 Prioriza Backlog

Sistema inteligente de priorização de backlog usando IA (AWS Bedrock + Claude).

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![AWS](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)

## 🚀 Quick Start

```bash
# Clone e configure
git clone <repo-url>
cd priorizacaobacklog

# Crie ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instale dependências
pip install -r requirements.txt

# Configure AWS
cp .env.example .env
# Edite .env com suas credenciais AWS

# Execute localmente
uvicorn app.main:app --reload
```

Acesse: **http://localhost:8000**

## 📋 Funcionalidades

- ✅ Priorização inteligente de backlog usando IA
- ✅ Análise de impacto (financeiro, negócios, cliente, OKR)
- ✅ Interface web interativa e **Responsiva (Mobile First)** 📱
- ✅ **Priorização Assíncrona** com notificação de status em tempo real ⚡
- ✅ API REST completa
- ✅ Persistência em DynamoDB
- ✅ Ordenação por prioridade numérica (1 a N)
- ✅ Chat conversacional para gerenciar itens

## 📚 Documentação

### Configuração Inicial
- [Configuração AWS](docs/setup/aws-configuration.md) - Setup de credenciais e DynamoDB
- [Guia de Documentação](DOCUMENTATION_GUIDE.md) - Como organizar docs

### Guias de Uso
- [Testes Locais](docs/guides/testing-local.md) - Como testar a aplicação localmente
- [Testes em Produção](docs/guides/testing-production.md) - Validação em ambiente AWS
- [Dados de Teste](docs/guides/test-data.md) - Como usar massa de dados de teste

### Funcionalidades
- [Exclusão de Itens](docs/features/delete-item.md) - Como deletar itens do backlog
- [Pesos de Priorização](docs/features/priority-weights.md) - Como funcionam os pesos configuráveis

## 🛠️ Tecnologias

- **Backend**: FastAPI, Python 3.11
- **IA**: AWS Bedrock (Claude 3.5 Sonnet)
- **Banco de Dados**: AWS DynamoDB
- **Frontend**: React (vanilla JS)
- **Deploy**: Docker, AWS Lambda

## 📁 Estrutura do Projeto

```
priorizacaobacklog/
├── app/                    # Código da aplicação
│   ├── api/               # Endpoints da API
│   ├── core/              # Lógica de negócio
│   ├── models/            # Modelos de dados
│   └── static/            # Frontend React
├── docs/                   # Documentação
│   ├── setup/             # Guias de configuração
│   ├── guides/            # Guias de uso
│   └── features/          # Documentação de features
├── scripts/                # Scripts utilitários
├── README.md              # Este arquivo
└── requirements.txt       # Dependências Python
```

## 🧪 Scripts Úteis

```bash
# Importar dados de teste
python scripts/import_test_data.py

# Inicializar DynamoDB
python scripts/init_dynamodb.py

# Executar priorização via API
python scripts/run_prioritization.py
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 📞 Suporte

Para dúvidas ou problemas, abra uma [issue](https://github.com/seu-usuario/priorizacaobacklog/issues).
