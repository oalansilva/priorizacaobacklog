# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Added
- Migração completa para AWS DynamoDB
- Campo de prioridade numérica (1 a N)
- Ordenação automática do backlog por prioridade
- Badge visual de prioridade (#N) antes do título
- Documentação reorganizada em estrutura `docs/`
- Scripts utilitários movidos para `scripts/`
- Guia de organização de documentação

### Changed
- Banco de dados padrão alterado de SQLite para DynamoDB
- Nomenclatura de arquivos .md para kebab-case
- README.md simplificado e modernizado
- Interface do backlog agora ordena por prioridade

### Fixed
- Erro "database is locked" do SQLite eliminado
- Persistência de dados de priorização no banco
- Exibição de números de prioridade na interface

## [0.1.0] - 2025-11-24

### Added
- Sistema de priorização com AWS Bedrock
- Interface web com React
- API REST com FastAPI
- Funcionalidade de chat conversacional
- Exclusão de itens do backlog
- Pesos configuráveis para priorização
- Testes locais e em produção
- Massa de dados de teste

[Unreleased]: https://github.com/seu-usuario/priorizacaobacklog/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/seu-usuario/priorizacaobacklog/releases/tag/v0.1.0
