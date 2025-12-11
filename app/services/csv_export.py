"""Serviço de exportação de roadmaps para CSV."""

from io import StringIO
import csv
from app.models.db import Roadmap
from datetime import datetime
import pytz


def export_roadmap_to_csv(roadmap: Roadmap) -> str:
    """
    Gera arquivo CSV do roadmap compatível com Excel.
    
    Args:
        roadmap: Objeto Roadmap com dados da priorização
        
    Returns:
        String com conteúdo CSV
    """
    output = StringIO()
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    
    # Converter data para fuso horário de São Paulo
    utc_time = datetime.fromisoformat(roadmap.created_at.replace('Z', '+00:00'))
    sp_tz = pytz.timezone('America/Sao_Paulo')
    sp_time = utc_time.astimezone(sp_tz)
    data_criacao = sp_time.strftime("%d/%m/%Y %H:%M")
    
    # === SEÇÃO RESUMO ===
    writer.writerow(['ROADMAP - RESUMO DA PRIORIZAÇÃO'])
    writer.writerow(['Data', data_criacao])
    writer.writerow([])
    
    writer.writerow(['MÉTRICAS'])
    writer.writerow(['Capacidade Total', f'{roadmap.capacidade_total}h'])
    writer.writerow(['Percentual Sustentação', f'{roadmap.percentual_sustentacao}%'])
    writer.writerow(['Capacidade Iniciativas', f'{roadmap.capacidade_iniciativas}h'])
    writer.writerow(['Total de Itens', roadmap.total_itens])
    writer.writerow(['Itens Priorizados', roadmap.itens_priorizados])
    writer.writerow(['Itens Despriorizados', roadmap.itens_despriorizados])
    writer.writerow(['Horas Alocadas', f'{roadmap.horas_alocadas}h'])
    writer.writerow([])
    
    writer.writerow(['PESOS UTILIZADOS'])
    writer.writerow(['Financeiro', f'{roadmap.peso_financeiro}%'])
    writer.writerow(['Negócios', f'{roadmap.peso_negocios}%'])
    writer.writerow(['Cliente', f'{roadmap.peso_cliente}%'])
    writer.writerow(['OKR', f'{roadmap.peso_okr}%'])
    writer.writerow([])
    writer.writerow([])
    
    # === SEÇÃO PRIORIZADOS ===
    writer.writerow(['ITENS PRIORIZADOS'])
    writer.writerow(['#', 'Título', 'Área', 'Esforço (h)', 'Score', 'Impacto Fin.', 'Impacto Neg.', 'Impacto Cli.', 'OKR', 'Must Have', 'Justificativa'])
    
    priorizados = [item for item in roadmap.itens if item.status == "Priorizado"]
    priorizados.sort(key=lambda x: x.prioridade if x.prioridade else 999)
    
    for item in priorizados:
        score_value = item.score if item.score is not None else 0.0
        writer.writerow([
            item.prioridade or '',
            item.titulo or '',
            item.area or '',
            item.esforco_estimado or 0,
            f'{score_value:.1f}%',
            item.impacto_financeiro or 'Não',
            item.impacto_negocios or 'Não',
            item.impacto_cliente or 'Não',
            item.okr or 'Não',
            item.must_have or 'Não',
            item.justificativa or ''
        ])
    
    writer.writerow([])
    writer.writerow([])
    
    # === SEÇÃO DESPRIORIZADOS ===
    writer.writerow(['ITENS DESPRIORIZADOS'])
    writer.writerow(['#', 'Título', 'Área', 'Esforço (h)', 'Score', 'Impacto Fin.', 'Impacto Neg.', 'Impacto Cli.', 'OKR', 'Must Have', 'Justificativa'])
    
    despriorizados = [item for item in roadmap.itens if item.status == "Despriorizado"]
    despriorizados.sort(key=lambda x: x.prioridade if x.prioridade else 999)
    
    for item in despriorizados:
        score_value = item.score if item.score is not None else 0.0
        writer.writerow([
            item.prioridade or '',
            item.titulo or '',
            item.area or '',
            item.esforco_estimado or 0,
            f'{score_value:.1f}%',
            item.impacto_financeiro or 'Não',
            item.impacto_negocios or 'Não',
            item.impacto_cliente or 'Não',
            item.okr or 'Não',
            item.must_have or 'Não',
            item.justificativa or ''
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    return csv_content
