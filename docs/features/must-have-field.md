# Campo Must Have

## Descrição

O campo **Must Have** é um atributo booleano (Sim/Não) que marca itens como **obrigatórios** para priorização.

## Comportamento

- **Valor padrão**: `"Não"`
- **Quando definido como "Sim"**: O item se torna obrigatório e deve ser priorizado
- **Exibição na UI**: Badge vermelho com borda `⚠️ Must Have`

## Como usar

### 1. Via Chat
```
Adicione um item com must_have = Sim
```

### 2. Via API
```json
{
  "titulo": "Corrigir bug crítico",
  "descricao": "Bug que impede login",
  "esforco_estimado": 8,
  "area": "Backend",
  "must_have": "Sim"
}
```

### 3. Via Interface Web
- Edite um item existente
- Marque o campo "Must Have" como "Sim"

## Impacto na Priorização

Itens marcados como **Must Have** devem ser considerados pela IA como **obrigatórios** durante a priorização, independentemente de outros critérios.

> **Nota**: A lógica de priorização da IA pode ser ajustada no prompt do sistema para garantir que itens Must Have sejam sempre priorizados.

## Estrutura no Banco de Dados

### SQLite
```sql
must_have TEXT DEFAULT 'Não'
```

### DynamoDB
```python
must_have: str = "Não"  # String attribute
```

## Exemplo de Item Must Have

```json
{
  "id": "123",
  "titulo": "Implementar autenticação 2FA",
  "must_have": "Sim",
  "status": "Priorizado",
  "prioridade": 1
}
```

## Badge na Interface

Quando `must_have === "Sim"`, o item exibe:

```
⚠️ Must Have
```

Com estilo:
- Fundo: `bg-red-50`
- Texto: `text-red-700`
- Borda: `border border-red-300`
