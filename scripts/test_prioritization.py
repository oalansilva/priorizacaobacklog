"""
Script para executar priorização e verificar Must Have
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

def test_prioritization():
    print("\n🚀 Executando priorização...")
    response = requests.post('http://localhost:8000/priorizacoes')
    
    if response.status_code == 200:
        result = response.json()
        priorizados = [item for item in result['itens'] if item['status'] == 'Priorizado']
        
        print("\n🎯 TOP 5 ITENS PRIORIZADOS:\n")
        for i, item in enumerate(priorizados[:5], 1):
            must_have_badge = "⚠️ MUST HAVE" if item.get('must_have') == 'Sim' else ""
            print(f"  #{i} - {item['item']} {must_have_badge}")
            if item.get('must_have') == 'Sim':
                print(f"       Justificativa: {item.get('justificativa', 'N/A')[:100]}...")
        
        # Verificar se itens Must Have estão no topo
        must_have_items = [item for item in priorizados if item.get('must_have') == 'Sim']
        if must_have_items:
            print(f"\n✅ {len(must_have_items)} item(ns) Must Have encontrado(s)")
            top_positions = [i+1 for i, item in enumerate(priorizados) if item.get('must_have') == 'Sim']
            print(f"   Posições na lista: {top_positions}")
        else:
            print("\n⚠️ Nenhum item Must Have encontrado")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_prioritization()
