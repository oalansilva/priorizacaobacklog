"""
Script para adicionar o campo must_have aos itens existentes no DynamoDB
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_repository

def update_items_with_must_have():
    repo = get_repository()
    items = repo.list_items()
    
    print(f"Atualizando {len(items)} itens com campo must_have...")
    
    for item in items:
        # Garantir que o campo must_have existe (padrão: "Não")
        if not hasattr(item, 'must_have') or item.must_have is None:
            item.must_have = "Não"
            repo.update_item(item)
            print(f"✓ Atualizado: {item.titulo}")
        else:
            print(f"- Já possui must_have: {item.titulo}")
    
    print("\n✅ Atualização concluída!")

if __name__ == "__main__":
    update_items_with_must_have()
