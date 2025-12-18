"""
Migration script to convert items with workflow_stage='sustentacao' to 'downstream'.

Sustentacao is NOT a workflow stage - it's only a capacity reservation for unplanned work.
All planned PBIs must be either 'upstream' or 'downstream'.

This script:
1. Lists all items with workflow_stage='sustentacao'
2. Converts them to workflow_stage='downstream' (reactive implementation work)
3. Updates each item in the database
4. Reports the migration results

Usage:
    python scripts/migrate_sustentacao_items.py
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import get_repository


def migrate_sustentacao_to_downstream():
    """Convert all items with workflow_stage='sustentacao' to 'downstream'."""
    print("=" * 60)
    print("MIGRAÇÃO: Sustentação → Downstream")
    print("=" * 60)
    print("\nMotivo: Sustentação NÃO é um workflow stage válido.")
    print("É apenas uma reserva de capacidade para trabalho não planejado.\n")
    
    repo = get_repository()
    items = repo.list_items()
    
    # Find items with sustentacao
    sustentacao_items = [item for item in items if item.workflow_stage == "sustentacao"]
    
    if not sustentacao_items:
        print("✅ Nenhum item com workflow_stage='sustentacao' encontrado.")
        print("Migração não necessária!")
        return 0
    
    print(f"📋 Encontrados {len(sustentacao_items)} items com workflow_stage='sustentacao':\n")
    
    for item in sustentacao_items:
        print(f"  - {item.id}: {item.titulo} ({item.esforco_estimado}h)")
    
    # Confirm migration
    print(f"\n⚠️  Estes items serão convertidos para workflow_stage='downstream'")
    confirm = input("\nContinuar com a migração? (s/N): ").strip().lower()
    
    if confirm != 's':
        print("\n❌ Migração cancelada pelo usuário.")
        return 0
    
    print("\n🔄 Iniciando migração...\n")
    
    migrated_count = 0
    errors = []
    
    for item in sustentacao_items:
        try:
            # Update workflow_stage
            item.workflow_stage = "downstream"
            repo.update_item(item)
            migrated_count += 1
            print(f"✅ Migrado: {item.id} - {item.titulo}")
        except Exception as e:
            error_msg = f"❌ Erro ao migrar {item.id}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)
    
    # Summary
    print("\n" + "=" * 60)
    print("RESUMO DA MIGRAÇÃO")
    print("=" * 60)
    print(f"Total de items encontrados: {len(sustentacao_items)}")
    print(f"✅ Migrados com sucesso: {migrated_count}")
    print(f"❌ Erros: {len(errors)}")
    
    if errors:
        print("\nErros encontrados:")
        for error in errors:
            print(f"  {error}")
    
    print("\n✅ Migração concluída!")
    return migrated_count


if __name__ == "__main__":
    try:
        migrated = migrate_sustentacao_to_downstream()
        sys.exit(0 if migrated >= 0 else 1)
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
