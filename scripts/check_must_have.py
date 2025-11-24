"""
Script para verificar itens Must Have após priorização
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_repository

def check_must_have_items():
    repo = get_repository()
    items = repo.list_items()
    
    must_have_items = [i for i in items if i.must_have == 'Sim']
    
    print(f"\n📋 Total de itens Must Have: {len(must_have_items)}\n")
    
    for item in must_have_items:
        print(f"✅ {item.titulo}")
        print(f"   Status: {item.status}")
        print(f"   Prioridade: #{item.prioridade}")
        print(f"   Must Have: {item.must_have}")
        if item.justificativa:
            print(f"   Justificativa: {item.justificativa[:100]}...")
        print()
    
    # Verificar se algum Must Have foi despriorizado
    despriorizados = [i for i in must_have_items if i.status == 'Despriorizado']
    if despriorizados:
        print(f"\n⚠️ ATENÇÃO: {len(despriorizados)} item(ns) Must Have foram DESPRIORIZADOS:")
        for item in despriorizados:
            print(f"   - {item.titulo}")
    else:
        print(f"\n✅ Todos os itens Must Have estão PRIORIZADOS!")

if __name__ == "__main__":
    check_must_have_items()
