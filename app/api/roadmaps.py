from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from app.core.database import get_repository, DatabaseRepository
from app.models.db import Roadmap

router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])

@router.get("/", response_model=List[Roadmap])
def list_roadmaps(repo: DatabaseRepository = Depends(get_repository)):
    """Lista todos os roadmaps salvos ordenados por data (mais recente primeiro)."""
    return repo.list_roadmaps()

@router.get("/{roadmap_id}", response_model=Roadmap)
def get_roadmap(roadmap_id: str, repo: DatabaseRepository = Depends(get_repository)):
    """Obtém um roadmap específico pelo ID."""
    roadmap = repo.get_roadmap(roadmap_id)
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap não encontrado")
    return roadmap

@router.get("/{roadmap_id}/export")
def export_roadmap(roadmap_id: str, repo: DatabaseRepository = Depends(get_repository)):
    """Exporta roadmap para arquivo CSV compatível com Excel."""
    from app.services.csv_export import export_roadmap_to_csv
    from datetime import datetime
    from fastapi.responses import Response
    
    roadmap = repo.get_roadmap(roadmap_id)
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap não encontrado")
    
    csv_content = export_roadmap_to_csv(roadmap)
    
    # Nome do arquivo com data
    data_criacao = datetime.fromisoformat(roadmap.created_at).strftime("%Y%m%d_%H%M")
    filename = f"roadmap_{data_criacao}.csv"
    
    return Response(
        content=csv_content.encode('utf-8-sig'),  # BOM para Excel reconhecer UTF-8
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )



@router.get("/debug-pdf")
def debug_pdf():
    """Endpoint para debugar instalação do ReportLab."""
    import sys
    results = {
        "python_version": sys.version,
        "reportlab_installed": False,
        "reportlab_version": None,
        "error": None
    }
    
    try:
        import reportlab
        results["reportlab_installed"] = True
        results["reportlab_version"] = reportlab.Version
        results["file"] = reportlab.__file__
    except ImportError as e:
        results["error"] = str(e)
    except Exception as e:
        results["error"] = f"Unexpected error: {str(e)}"
        
    return results

@router.get("/{roadmap_id}/export-pdf")
def export_roadmap_pdf(roadmap_id: str, repo: DatabaseRepository = Depends(get_repository)):
    """Exporta roadmap para arquivo PDF."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Iniciando exportação PDF para roadmap {roadmap_id}")
        
        from app.services.pdf_export import export_roadmap_to_pdf
        from datetime import datetime
        from fastapi.responses import Response
        
        roadmap = repo.get_roadmap(roadmap_id)
        if not roadmap:
            raise HTTPException(status_code=404, detail="Roadmap não encontrado")
        
        logger.info(f"Roadmap encontrado: {len(roadmap.itens)} itens")
        
        pdf_buffer = export_roadmap_to_pdf(roadmap)
        
        pdf_size = pdf_buffer.getbuffer().nbytes
        logger.info(f"PDF gerado com sucesso. Tamanho: {pdf_size} bytes")
        
        # Nome do arquivo com data
        try:
            data_criacao = datetime.fromisoformat(roadmap.created_at.replace('Z', '+00:00')).strftime("%Y%m%d_%H%M")
        except:
            data_criacao = "roadmap"
        
        filename = f"roadmap_{data_criacao}.pdf"
        
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Erro ao exportar PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}")

@router.delete("/{roadmap_id}")
def delete_roadmap(roadmap_id: str, repo: DatabaseRepository = Depends(get_repository)):
    """Deleta um roadmap pelo ID."""
    deleted = repo.delete_roadmap(roadmap_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Roadmap não encontrado")
    return {"message": "Roadmap deletado com sucesso", "id": roadmap_id}
