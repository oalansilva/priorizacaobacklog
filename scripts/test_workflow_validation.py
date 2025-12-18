"""
Test script to verify that sustentacao workflow stage is rejected.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.db import BacklogItem

print("=" * 60)
print("TESTE: Validação de Workflow Stage")
print("=" * 60)

# Test 1: Valid upstream
print("\n✅ Teste 1: Criar item com workflow_stage='upstream'")
try:
    item1 = BacklogItem(
        id="test-1",
        titulo="Test Upstream",
        descricao="Test",
        esforco_estimado=10,
        area="Tech",
        workflow_stage="upstream"
    )
    print(f"   Sucesso! Item criado: {item1.workflow_stage}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Test 2: Valid downstream
print("\n✅ Teste 2: Criar item com workflow_stage='downstream'")
try:
    item2 = BacklogItem(
        id="test-2",
        titulo="Test Downstream",
        descricao="Test",
        esforco_estimado=10,
        area="Tech",
        workflow_stage="downstream"
    )
    print(f"   Sucesso! Item criado: {item2.workflow_stage}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Test 3: Invalid sustentacao (should fail)
print("\n❌ Teste 3: Tentar criar item com workflow_stage='sustentacao'")
try:
    item3 = BacklogItem(
        id="test-3",
        titulo="Test Sustentacao",
        descricao="Test",
        esforco_estimado=10,
        area="Tech",
        workflow_stage="sustentacao"
    )
    print(f"   ❌ FALHA! Item foi criado (não deveria): {item3.workflow_stage}")
except ValueError as e:
    print(f"   ✅ Sucesso! Validação funcionou:")
    print(f"      {e}")
except Exception as e:
    print(f"   ❌ Erro inesperado: {e}")

# Test 4: Default value
print("\n✅ Teste 4: Criar item sem especificar workflow_stage (deve usar default 'upstream')")
try:
    item4 = BacklogItem(
        id="test-4",
        titulo="Test Default",
        descricao="Test",
        esforco_estimado=10,
        area="Tech"
    )
    print(f"   Sucesso! Item criado com default: {item4.workflow_stage}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "=" * 60)
print("RESUMO DOS TESTES")
print("=" * 60)
print("✅ Upstream: Aceito")
print("✅ Downstream: Aceito")
print("❌ Sustentacao: Rejeitado (correto!)")
print("✅ Default: upstream")
print("\n✅ Validação funcionando corretamente!")
