"""
Script para verificar justificativas sem números ordinais
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_repository

def check_justifications():
    repo = get_repository()
    items = repo.list_items()
    priorizados = [i for i in items if i.status == 'Priorizado']
    priorizados.sort(key=lambda x: x.prioridade)
    
    print(f"\n📋 Verificando {len(priorizados)} itens priorizados:\n")
    
    ordinals = ["primeira", "segunda", "terceira", "quarta", "quinta", "sexta", "sétima", "oitava", "nona", "décima", 
                "1º", "2º", "3º", "4º", "5º", "#1", "#2", "#3"]
    
    for item in priorizados:
        justificativa_lower = item.justificativa.lower()
        has_ordinal = any(ord in justificativa_lower for ord in ordinals)
        
        status_icon = "❌" if has_ordinal else "✅"
        print(f"{status_icon} #{item.prioridade} - {item.titulo}")
        print(f"   Justificativa: {item.justificativa[:100]}...")
        
        if has_ordinal:
            print(f"   ⚠️ CONTÉM ORDINAL! (Verificar texto completo)")

if __name__ == "__main__":
    check_justifications()
