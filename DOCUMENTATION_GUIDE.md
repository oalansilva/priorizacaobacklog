# 📚 Guia de Organização de Documentação Markdown

## Estrutura Recomendada

```
projeto/
├── README.md                    # Visão geral do projeto (sempre na raiz)
├── docs/                        # Toda documentação adicional
│   ├── getting-started/         # Guias de início
│   │   ├── installation.md
│   │   ├── configuration.md
│   │   └── quick-start.md
│   ├── guides/                  # Guias de uso
│   │   ├── testing.md
│   │   ├── deployment.md
│   │   └── troubleshooting.md
│   ├── architecture/            # Documentação técnica
│   │   ├── overview.md
│   │   ├── database.md
│   │   └── api.md
│   ├── development/             # Para desenvolvedores
│   │   ├── contributing.md
│   │   ├── code-style.md
│   │   └── testing-guide.md
│   └── reference/               # Referências
│       ├── api-reference.md
│       └── configuration-reference.md
├── CHANGELOG.md                 # Histórico de mudanças (raiz)
├── CONTRIBUTING.md              # Como contribuir (raiz)
└── LICENSE.md                   # Licença (raiz)
```

## Arquivos que Devem Ficar na Raiz

1. **README.md** - Obrigatório, primeira coisa que as pessoas veem
2. **CHANGELOG.md** - Histórico de versões
3. **CONTRIBUTING.md** - Guia para contribuidores
4. **LICENSE.md** - Licença do projeto
5. **CODE_OF_CONDUCT.md** - Código de conduta (projetos open source)

## Organização Sugerida para Seu Projeto

### Estrutura Proposta

```
priorizacaobacklog/
├── README.md                           # ✅ Já existe
├── CHANGELOG.md                        # 📝 Criar
├── docs/
│   ├── setup/
│   │   ├── aws-configuration.md        # CONFIGURACAO_AWS.md
│   │   └── local-setup.md              # Novo (combinar partes do README)
│   ├── guides/
│   │   ├── testing-local.md            # TESTE_LOCAL.md
│   │   ├── testing-production.md       # COMO_TESTAR_PROD.md
│   │   └── test-data.md                # MASSA_TESTE_README.md
│   ├── features/
│   │   ├── delete-item.md              # DELETE_ITEM_DOC.md
│   │   └── priority-weights.md         # VERIFICACAO_PESOS.md
│   └── architecture/
│       ├── database-migration.md       # Novo (DynamoDB)
│       └── api-overview.md             # Novo
└── scripts/                            # Scripts utilitários
    ├── import_test_data.py
    ├── init_dynamodb.py
    └── run_prioritization.py
```

## Boas Práticas

### 1. Nomenclatura
- **Usar kebab-case**: `api-reference.md` ✅ (não `API_REFERENCE.md` ❌)
- **Ser descritivo**: `testing-production.md` ✅ (não `teste_prod.md` ❌)
- **Evitar abreviações**: `configuration.md` ✅ (não `config.md` ❌)

### 2. Estrutura de Cada Arquivo
```markdown
# Título Principal (H1 - apenas um por arquivo)

Breve descrição do que este documento cobre.

## Seção 1 (H2)
Conteúdo...

### Subseção 1.1 (H3)
Detalhes...

## Seção 2
...
```

### 3. Links Internos
```markdown
<!-- Usar caminhos relativos -->
Veja [Guia de Instalação](./setup/installation.md)

<!-- Para raiz -->
Veja [README](../README.md)
```

### 4. README.md Principal
Deve conter:
- **Título e descrição** breve
- **Badges** (build status, coverage, etc.)
- **Quick Start** (instalação rápida)
- **Links para documentação** detalhada
- **Licença e contribuição**

### 5. Manutenção
- **Manter atualizado**: Documentação desatualizada é pior que sem documentação
- **Revisar regularmente**: Ao adicionar features, atualizar docs
- **Usar templates**: Criar templates para tipos comuns de docs

## Ferramentas Úteis

- **MkDocs**: Gera site estático a partir de Markdown
- **Docusaurus**: Framework para documentação (React)
- **GitBook**: Plataforma de documentação
- **mdBook**: Gerador de livros em Markdown (Rust)

## Exemplo de README.md Ideal

```markdown
# 🎯 Prioriza Backlog

Sistema inteligente de priorização de backlog usando IA (AWS Bedrock).

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)]()

## 🚀 Quick Start

\`\`\`bash
# Clone e configure
git clone ...
cd priorizacaobacklog
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt

# Configure AWS
cp .env.example .env
# Edite .env com suas credenciais

# Execute
uvicorn app.main:app --reload
\`\`\`

Acesse: http://localhost:8000

## 📚 Documentação

- [Configuração AWS](docs/setup/aws-configuration.md)
- [Guia de Testes](docs/guides/testing-local.md)
- [Referência da API](docs/reference/api-reference.md)

## 🤝 Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 Licença

MIT License - veja [LICENSE](LICENSE)
```

## Próximos Passos Recomendados

1. Criar pasta `docs/`
2. Mover arquivos `.md` para subpastas apropriadas
3. Renomear para kebab-case
4. Atualizar links internos
5. Simplificar README.md principal
6. Criar CHANGELOG.md
