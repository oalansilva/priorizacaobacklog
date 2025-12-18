"""
Script para corrigir workflow_stage dos items existentes.

Analisa o título e descrição dos items para determinar se são upstream ou downstream.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import get_repository

# Palavras-chave que indicam upstream (descoberta, pesquisa, design)
UPSTREAM_KEYWORDS = [
    'pesquisa', 'análise', 'estudo', 'design', 'protótipo', 'validação',
    'discovery', 'research', 'study', 'prototype', 'validation', 'planejamento',
    'planning', 'especificação', 'specification', 'levantamento', 'investigação'
]

# Palavras-chave que indicam downstream (implementação, desenvolvimento)
DOWNSTREAM_KEYWORDS = [
    'implementar', 'desenvolver', 'criar', 'construir', 'integrar', 'deploy',
    'implement', 'develop', 'create', 'build', 'integrate', 'deployment',
    'codificar', 'programar', 'api', 'backend', 'frontend', 'database',
    'refatorar', 'otimizar', 'migrar', 'atualizar'
]

def classify_item(item):
    """Classifica um item como upstream ou downstream baseado em palavras-chave."""
    text = f"{item.titulo} {item.descricao or ''}".lower()
    
    # Contar matches
    upstream_score = sum(1 for keyword in UPSTREAM_KEYWORDS if keyword in text)
    downstream_score = sum(1 for keyword in DOWNSTREAM_KEYWORDS if keyword in text)
    
    # Se já tem um workflow_stage diferente de upstream, manter
    if item.workflow_stage and item.workflow_stage != 'upstream':
        return item.workflow_stage
    
    # Classificar baseado em score
    if downstream_score > upstream_score:
        return 'downstream'
    else:
        # Default para downstream se não tiver palavras-chave claras de upstream
        # (a maioria dos items de backlog são implementação)
        return 'downstream' if downstream_score > 0 or upstream_score == 0 else 'upstream'

def fix_workflow_stages():
    """Corrige workflow_stage de todos os items."""
    print("=" * 60)
    print("CORREÇÃO: Workflow Stages dos Items")
    print("=" * 60)
    
    repo = get_repository()
    items = repo.list_items()
    
    print(f"\n📋 Total de items: {len(items)}\n")
    
    # Análise
    upstream_items = []
    downstream_items = []
    
    for item in items:
        current_stage = item.workflow_stage
        suggested_stage = classify_item(item)
        
        if current_stage != suggested_stage:
            print(f"🔄 {item.id}: {item.titulo[:50]}")
            print(f"   Atual: {current_stage} → Sugerido: {suggested_stage}")
            
            if suggested_stage == 'upstream':
                upstream_items.append(item)
            else:
                downstream_items.append(item)
    
    if not upstream_items and not downstream_items:
        print("✅ Todos os items já estão com workflow_stage correto!")
        return 0
    
    print(f"\n📊 Resumo:")
    print(f"   Upstream: {len(upstream_items)} items")
    print(f"   Downstream: {len(downstream_items)} items")
    
    # Confirmar
    print("\n⚠️  ATENÇÃO: Esta operação vai atualizar os workflow_stages.")
    print("   Você pode revisar manualmente depois via interface.")
    confirm = input("\nContinuar? (s/N): ").strip().lower()
    
    if confirm != 's':
        print("\n❌ Operação cancelada.")
        return 0
    
    # Atualizar
    print("\n🔄 Atualizando items...\n")
    updated = 0
    
    for item in upstream_items:
        item.workflow_stage = 'upstream'
        repo.update_item(item)
        print(f"✅ {item.titulo[:50]} → upstream")
        updated += 1
    
    for item in downstream_items:
        item.workflow_stage = 'downstream'
        repo.update_item(item)
        print(f"✅ {item.titulo[:50]} → downstream")
        updated += 1
    
    print(f"\n✅ {updated} items atualizados com sucesso!")
    print("\n💡 Dica: Revise os items na interface e ajuste manualmente se necessário.")
    
    return updated

if __name__ == "__main__":
    try:
        updated = fix_workflow_stages()
        sys.exit(0 if updated >= 0 else 1)
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
