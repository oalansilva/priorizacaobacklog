"""Serviço de exportação de roadmaps para PDF."""

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from app.models.db import Roadmap
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)


def export_roadmap_to_pdf(roadmap: Roadmap) -> BytesIO:
    """
    Gera arquivo PDF do roadmap com formatação profissional.
    
    Args:
        roadmap: Objeto Roadmap com dados da priorização
        
    Returns:
        BytesIO com o arquivo PDF gerado
    """
    logger.info(f"Iniciando export_roadmap_to_pdf para roadmap {roadmap.id}")
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        # Estilos básicos
        styles = getSampleStyleSheet()
        
        # Converter data para fuso horário de São Paulo
        try:
            if '+' in roadmap.created_at or 'Z' in roadmap.created_at:
                utc_time = datetime.fromisoformat(roadmap.created_at.replace('Z', '+00:00'))
            else:
                utc_time = datetime.fromisoformat(roadmap.created_at).replace(tzinfo=pytz.UTC)
            
            sp_tz = pytz.timezone('America/Sao_Paulo')
            sp_time = utc_time.astimezone(sp_tz)
            data_criacao = sp_time.strftime("%d/%m/%Y %H:%M")
        except Exception as e:
            logger.error(f"Erro ao converter data: {e}")
            data_criacao = str(roadmap.created_at)[:16]
        
        # Função auxiliar para limpar texto mantendo acentos
        def clean_text(text):
            if text is None:
                return ""
            try:
                s = str(text)
                return s.encode('cp1252', 'replace').decode('cp1252')
            except Exception as e:
                logger.warning(f"Erro ao limpar texto '{text}': {e}")
                return str(text)

        # Elementos do PDF
        elements = []
        
        logger.info("Adicionando título e resumo")
        # Título
        title = Paragraph("<b>Detalhes do Roadmap</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Resumo
        resumo_text = f"""
        <b>Data:</b> {data_criacao}<br/>
        <b>Capacidade Total:</b> {roadmap.capacidade_total}h<br/>
        <b>Itens Priorizados:</b> {roadmap.itens_priorizados}<br/>
        <b>Horas Alocadas:</b> {int(roadmap.horas_alocadas)}h
        """
        elements.append(Paragraph(resumo_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Priorizados
        priorizados = [item for item in roadmap.itens if item.status == "Priorizado"]
        priorizados.sort(key=lambda x: x.prioridade if x.prioridade else 999)
        
        logger.info(f"Processando {len(priorizados)} itens priorizados")
        
        if priorizados:
            elements.append(Paragraph(f"<b>Priorizados ({len(priorizados)})</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Tabela simplificada
            data = [['#', 'Titulo', 'Area', 'Horas', 'Score']]
            
            for item in priorizados:
                titulo = clean_text(item.titulo)[:50]
                area = clean_text(item.area)[:20]
                score = item.score if item.score is not None else 0.0
                
                data.append([
                    f"#{item.prioridade or ''}",
                    titulo,
                    area,
                    f"{item.esforco_estimado or 0}h",
                    f"{score:.1f}%"
                ])
            
            table = Table(data, colWidths=[0.5*inch, 3*inch, 1.5*inch, 0.8*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Despriorizados
        despriorizados = [item for item in roadmap.itens if item.status == "Despriorizado"]
        despriorizados.sort(key=lambda x: x.prioridade if x.prioridade else 999)
        
        logger.info(f"Processando {len(despriorizados)} itens despriorizados")
        
        if despriorizados:
            elements.append(Paragraph(f"<b>Despriorizados ({len(despriorizados)})</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))
            
            data = [['#', 'Titulo', 'Area', 'Horas', 'Score']]
            
            for item in despriorizados:
                titulo = clean_text(item.titulo)[:50]
                area = clean_text(item.area)[:20]
                score = item.score if item.score is not None else 0.0
                
                data.append([
                    f"#{item.prioridade or ''}",
                    titulo,
                    area,
                    f"{item.esforco_estimado or 0}h",
                    f"{score:.1f}%"
                ])
            
            table = Table(data, colWidths=[0.5*inch, 3*inch, 1.5*inch, 0.8*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        # Gerar PDF
        logger.info("Construindo documento PDF...")
        doc.build(elements)
        buffer.seek(0)
        
        size = buffer.getbuffer().nbytes
        header = buffer.getvalue()[:8]
        logger.info(f"PDF gerado. Tamanho: {size} bytes. Header: {header}")
        
        return buffer
        
    except Exception as e:
        logger.error(f"FATAL: Erro ao gerar PDF em export_roadmap_to_pdf: {e}", exc_info=True)
        raise
