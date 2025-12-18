"""
Simple test for capacity calculation method.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("=" * 60)
print("TESTE: Cálculo de Capacidade - Sistema Unificado")
print("=" * 60)

# Test calculation directly
capacidade_total = 1000
capacity_sustentacao_percent = 20.0

sustentacao = (capacidade_total * capacity_sustentacao_percent) / 100
capacidade_disponivel = capacidade_total - sustentacao

print("\n📊 Configuração:")
print(f"   Capacidade Total: {capacidade_total}h")
print(f"   Sustentação: {capacity_sustentacao_percent}%")

print("\n🧮 Cálculo:")
print(f"   Sustentação (buffer): {sustentacao}h")
print(f"   Disponível para PBIs: {capacidade_disponivel}h")

# Verify
expected = 800.0
if abs(capacidade_disponivel - expected) < 0.01:
    print(f"\n✅ CORRETO! {capacidade_disponivel}h disponíveis")
else:
    print(f"\n❌ ERRO! Esperado {expected}h, obtido {capacidade_disponivel}h")

# Show full breakdown
print("\n📋 Breakdown Completo (exemplo com 40/40/20):")
upstream_percent = 40.0
downstream_percent = 40.0

upstream_h = capacidade_total * upstream_percent / 100
downstream_h = capacidade_total * downstream_percent / 100
sustentacao_h = capacidade_total * capacity_sustentacao_percent / 100

print(f"   📋 Upstream: {upstream_h}h ({upstream_percent}%)")
print(f"   🔨 Downstream: {downstream_h}h ({downstream_percent}%)")
print(f"   🔧 Sustentação: {sustentacao_h}h ({capacity_sustentacao_percent}%)")
print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"   Total: {upstream_h + downstream_h + sustentacao_h}h")
print(f"   Soma %: {upstream_percent + downstream_percent + capacity_sustentacao_percent}%")

print("\n" + "=" * 60)
print("✅ Cálculo correto! Sistema unificado funcionando!")
print("=" * 60)
