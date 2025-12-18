"""
Script para atualizar workflow_stage nos roadmaps salvos.

Os roadmaps armazenam uma cópia dos items no momento da geração.
Este script atualiza os workflow_stages nos roadmaps para refletir os dados atuais.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import get_repository

def fix_roadmap_workflow_stages():
    """Atualiza workflow_stage nos roadmaps salvos."""
    print("=" * 60)
    print("CORREÇÃO: Workflow Stages nos Roadmaps Salvos")
    print("=" * 60)
    
    repo = get_repository()
    
    # Buscar items atuais (com workflow_stage correto)
    items = repo.list_items()
    item_stages = {item.id: item.workflow_stage for item in items}
    
    print(f"\n📋 Items no banco: {len(items)}")
    print(f"   Upstream: {sum(1 for s in item_stages.values() if s == 'upstream')}")
    print(f"   Downstream: {sum(1 for s in item_stages.values() if s == 'downstream')}")
    
    # Buscar roadmaps
    roadmaps = repo.list_roadmaps()
    print(f"\n🗺️  Roadmaps encontrados: {len(roadmaps)}\n")
    
    if not roadmaps:
        print("❌ Nenhum roadmap encontrado.")
        return 0
    
    # Analisar e atualizar
    updated_roadmaps = []
    
    for roadmap in roadmaps:
        updated = False
        changes = []
        
        for item in roadmap.itens:
            if item.id in item_stages:
                correct_stage = item_stages[item.id]
                if item.workflow_stage != correct_stage:
                    changes.append(f"   {item.titulo[:40]} → {correct_stage}")
                    item.workflow_stage = correct_stage
                    updated = True
        
        if updated:
            print(f"🔄 Roadmap: {roadmap.created_at}")
            for change in changes:
                print(change)
            print()
            updated_roadmaps.append(roadmap)
    
    if not updated_roadmaps:
        print("✅ Todos os roadmaps já estão corretos!")
        return 0
    
    print(f"\n📊 Resumo: {len(updated_roadmaps)} roadmap(s) precisam ser atualizados")
    
    # Confirmar
    confirm = input("\nAtualizar roadmaps? (s/N): ").strip().lower()
    
    if confirm != 's':
        print("\n❌ Operação cancelada.")
        return 0
    
    # Atualizar
    print("\n🔄 Atualizando roadmaps...\n")
    
    for roadmap in updated_roadmaps:
        repo.save_roadmap(roadmap)
        print(f"✅ Roadmap {roadmap.created_at} atualizado")
    
    print(f"\n✅ {len(updated_roadmaps)} roadmap(s) atualizado(s) com sucesso!")
    print("\n💡 Recarregue a página do roadmap para ver as mudanças.")
    
    return len(updated_roadmaps)

if __name__ == "__main__":
    try:
        updated = fix_roadmap_workflow_stages()
        sys.exit(0 if updated >= 0 else 1)
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
