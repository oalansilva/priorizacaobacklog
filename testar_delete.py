"""Script para testar a funcionalidade de deletar item."""
import requests

# Listar itens
print("Listando itens do banco...")
response = requests.get('http://localhost:8000/items')
items = response.json()
print(f"Total de itens: {len(items)}\n")

if items:
    # Pegar o primeiro item para deletar
    item_to_delete = items[0]
    print(f"Item a ser deletado:")
    print(f"  ID: {item_to_delete['id']}")
    print(f"  Título: {item_to_delete['titulo']}")
    print(f"  Área: {item_to_delete['area']}\n")
    
    # Deletar o item
    print("Deletando item...")
    delete_response = requests.delete(f"http://localhost:8000/items/{item_to_delete['id']}")
    
    if delete_response.status_code == 200:
        print(f"✅ Item deletado com sucesso!")
        print(f"   Resposta: {delete_response.json()}\n")
        
        # Verificar se foi realmente deletado
        print("Verificando itens restantes...")
        response = requests.get('http://localhost:8000/items')
        remaining_items = response.json()
        print(f"Total de itens após deleção: {len(remaining_items)}")
        print(f"✅ Teste concluído! Item removido com sucesso.")
    else:
        print(f"❌ Erro ao deletar: {delete_response.status_code}")
        print(f"   Resposta: {delete_response.text}")
else:
    print("❌ Nenhum item encontrado no banco de dados.")
