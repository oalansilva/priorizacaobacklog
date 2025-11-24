# Funcionalidade de Deletar Item - Documentação

## ✅ Implementado

Adicionada a funcionalidade de **deletar itens do backlog** via API.

## Mudanças Realizadas

### 1. [database.py](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/priorizacaobacklog/app/core/database.py)

**Adicionado método abstrato:**
```python
@abc.abstractmethod
def delete_item(self, item_id: str) -> bool:
    pass
```

**Implementação no SQLiteRepository:**
```python
def delete_item(self, item_id: str) -> bool:
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        return cursor.rowcount > 0
```

### 2. [items.py](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/priorizacaobacklog/app/api/items.py)

**Adicionado endpoint DELETE:**
```python
@router.delete("/{item_id}")
def delete_item(item_id: str, repo: DatabaseRepository = Depends(get_repository)):
    """Delete an item from the backlog by ID."""
    deleted = repo.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully", "id": item_id}
```

## Como Usar

### Via PowerShell/curl

```powershell
# Deletar item por ID
Invoke-WebRequest -Method DELETE -Uri "http://localhost:8000/items/{item_id}"
```

### Via Python

```python
import requests

# Deletar item
response = requests.delete(f"http://localhost:8000/items/{item_id}")
print(response.json())
# Output: {"message": "Item deleted successfully", "id": "..."}
```

### Via Swagger UI

1. Acesse http://localhost:8000/docs
2. Encontre o endpoint `DELETE /items/{item_id}`
3. Clique em "Try it out"
4. Insira o ID do item
5. Clique em "Execute"

## Testes Realizados

✅ **Teste de deleção bem-sucedida:**
- Item deletado: "Projeto Lucro Alto"
- Total antes: 12 itens
- Total depois: 11 itens
- Resposta: `{"message": "Item deleted successfully", "id": "617246e0-0630-454c-a35e-66bcfca37c92"}`

✅ **Tratamento de erros:**
- Retorna HTTP 404 quando item não existe
- Mensagem: "Item not found"

## Exemplo Completo

```python
# Script: testar_delete.py
import requests

# 1. Listar itens
items = requests.get('http://localhost:8000/items').json()
print(f"Total: {len(items)} itens")

# 2. Deletar primeiro item
item_id = items[0]['id']
response = requests.delete(f"http://localhost:8000/items/{item_id}")
print(response.json())

# 3. Verificar deleção
items_after = requests.get('http://localhost:8000/items').json()
print(f"Total após deleção: {len(items_after)} itens")
```

## Endpoints Disponíveis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/items` | Listar todos os itens |
| POST | `/items` | Adicionar novo item |
| PUT | `/items/{item_id}` | Atualizar item existente |
| **DELETE** | **`/items/{item_id}`** | **Deletar item** ✨ |
