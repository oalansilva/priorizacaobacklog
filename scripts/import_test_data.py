import json
import sys
import os

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.core.database import get_repository
from app.models.db import BacklogItem

def import_data():
    repo = get_repository()
    
    try:
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'massa_teste_10_itens.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            items_data = json.load(f)
            
        print(f"Found {len(items_data)} items to import.")
        
        count = 0
        for item_data in items_data:
            # Create BacklogItem instance
            # We don't specify id, created_at, status, prioridade as they have defaults
            item = BacklogItem(
                titulo=item_data['titulo'],
                descricao=item_data['descricao'],
                esforco_estimado=item_data['esforco_estimado'],
                area=item_data['area'],
                categoria=item_data['categoria'],
                impacto_financeiro=item_data['impacto_financeiro'],
                impacto_negocios=item_data['impacto_negocios'],
                impacto_cliente=item_data['impacto_cliente'],
                okr=item_data['okr'],
                estimado_qp=item_data['estimado_qp']
            )
            
            # Add to database
            repo.add_item(item)
            count += 1
            print(f"Imported: {item.titulo}")
            
        print(f"\nSuccessfully imported {count} items.")
        
    except Exception as e:
        print(f"Error importing data: {e}")

if __name__ == "__main__":
    import_data()
