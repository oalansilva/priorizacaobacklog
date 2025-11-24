import requests
import json

# Execute prioritization
url = "http://localhost:8000/priorizacoes"
headers = {"X-API-Key": "sua-chave-api-aqui"}  # Ajuste se necessário

print("Executando priorização...")
response = requests.post(url, headers=headers)

if response.status_code == 200:
    result = response.json()
    print(f"\n✅ Priorização concluída!")
    print(f"Total de itens: {len(result['itens'])}")
    print(f"\nItens priorizados:")
    for item in result['itens']:
        if item['status'] == 'Priorizado':
            print(f"  #{item['prioridade']} - {item['item']}")
else:
    print(f"❌ Erro: {response.status_code}")
    print(response.text)
