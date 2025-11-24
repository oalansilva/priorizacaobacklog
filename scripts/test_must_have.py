"""
Script para testar a priorização com itens Must Have
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_repository

def test_must_have():
    repo = get_repository()
    items = repo.list_items()
    
    # Marcar um item como Must Have para teste
    if items:
        test_item = items[5]  # Pegar um item do meio da lista
        print(f"\n🔧 Marcando item como Must Have: {test_item.titulo}")
        test_item.must_have = "Sim"
        repo.update_item(test_item)
        print(f"✅ Item atualizado: must_have = {test_item.must_have}")
        
        print(f"\n📋 Agora execute a priorização via API:")
        print(f"   POST http://localhost:8000/priorizacoes")
        print(f"\n🎯 O item '{test_item.titulo}' deve aparecer no topo da lista priorizada!")
    else:
        print("❌ Nenhum item encontrado no banco de dados")

if __name__ == "__main__":
    test_must_have()
