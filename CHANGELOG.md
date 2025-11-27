# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Unreleased]

## [0.2.0] - 2025-11-26

### Added
- **Priorização Assíncrona**: Execução em background via threading para evitar timeouts.
- **Notificação de Status**: Sistema de feedback em tempo real sobre o status da priorização.
- **Design Responsivo**: Interface otimizada para dispositivos móveis (Mobile First).
- **Status UI**: Banner visual na tela de Backlog mostrando status (running/completed/error).
- **Endpoint de Status**: Novo endpoint `/items/prioritization-status`.
- **Agent Tool**: Nova ferramenta `check_prioritization_status` para o agente.
- **Histórico Persistente**: Status da última priorização salvo no DynamoDB.

### Changed
- **Performance**: Remoção de logs excessivos para melhor desempenho.
- **Segurança**: Atualização do CSP para permitir scripts inline necessários.
- **UX**: Auto-refresh inteligente do status na interface.

## [0.1.1] - 2025-11-25

### Added
- Migração completa para AWS DynamoDB.
- Campo de prioridade numérica (1 a N).
- Ordenação automática do backlog por prioridade.
- Badge visual de prioridade (#N) antes do título.

### Changed
- Banco de dados padrão alterado de SQLite para DynamoDB.
- Interface do backlog agora ordena por prioridade.

### Fixed
- Erro "database is locked" do SQLite eliminado.
- Persistência de dados de priorização no banco.

## [0.1.0] - 2025-11-24

### Added
- Sistema de priorização com AWS Bedrock.
- Interface web com React.
- API REST com FastAPI.
- Funcionalidade de chat conversacional.
- Exclusão de itens do backlog.
- Pesos configuráveis para priorização.
- Testes locais e em produção.
- Massa de dados de teste.

[Unreleased]: https://github.com/seu-usuario/priorizacaobacklog/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/seu-usuario/priorizacaobacklog/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/seu-usuario/priorizacaobacklog/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/seu-usuario/priorizacaobacklog/releases/tag/v0.1.0
