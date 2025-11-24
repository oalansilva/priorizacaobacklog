"""
Script para executar priorização e verificar ordem dos Must Have
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

def run_prioritization_and_check():
    print("\n🚀 Executando nova priorização...\n")
    
    response = requests.post('http://localhost:8000/priorizacoes')
    
    if response.status_code == 200:
        result = response.json()
        priorizados = [item for item in result['itens'] if item['status'] == 'Priorizado']
        
        print("=== ITENS PRIORIZADOS (por ordem de prioridade) ===\n")
        
        must_have_count = 0
        for idx, item in enumerate(priorizados, 1):
            must_have = item.get('must_have', 'Não')
            badge = "⚠️ MUST HAVE" if must_have == 'Sim' else ""
            
            print(f"#{idx} - {item['item']} {badge}")
            
            if must_have == 'Sim':
                must_have_count += 1
                if idx > must_have_count:
                    print(f"   ❌ ERRO: Must Have na posição #{idx}, deveria estar em #{must_have_count}")
        
        print(f"\n✅ Total de Must Have: {must_have_count}")
        print(f"📊 Total priorizados: {len(priorizados)}")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    run_prioritization_and_check()
