"""Script para adicionar itens de teste ao banco de dados."""
import json
import requests

# Ler itens do arquivo JSON
with open('massa_teste_10_itens.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

# URL da API
api_url = 'http://localhost:8000/items'

# Adicionar cada item
print(f"Adicionando {len(items)} itens ao banco de dados...\n")

for i, item in enumerate(items, 1):
    try:
        response = requests.post(api_url, json=item)
        if response.status_code == 200:
            print(f"✅ {i}. {item['titulo']}")
        else:
            print(f"❌ {i}. {item['titulo']} - Erro: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ {i}. {item['titulo']} - Exceção: {str(e)}")

print(f"\n✅ Processo concluído! Itens adicionados ao banco de dados.")
print(f"📄 Massa de dados salva em: massa_teste_10_itens.json")
