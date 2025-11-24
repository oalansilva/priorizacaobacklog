"""Aplicação FastAPI para priorização de backlog."""

from __future__ import annotations

from typing import Optional

import pandas as pd
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware

try:
    import redis.asyncio as redis
except ImportError:  # pragma: no cover
    redis = None  # type: ignore

try:
    from fastapi_limiter import FastAPILimiter
    from fastapi_limiter.depends import RateLimiter
except ImportError:  # pragma: no cover
    FastAPILimiter = None  # type: ignore
    RateLimiter = None  # type: ignore

from app.config import Settings, get_settings
from app.core.prioritization import PrioritizationService
from app.logging import get_logger
from app.models import PrioritizationRequest, PrioritizationResponse
from app.security import enforce_api_key
from app.api import chat, items, settings

logger = get_logger(__name__)


def get_service(settings: Settings = Depends(get_settings)) -> PrioritizationService:
    """Dependência para obter o serviço principal."""
    return PrioritizationService(settings=settings)


app = FastAPI(
    title="Prioriza Backlog API",
    version="0.1.0",
    description="API para priorização de demandas com AWS Bedrock + LangChain.",
)

app.include_router(chat.router)
app.include_router(items.router)
app.include_router(settings.router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False)
async def read_root():
    return FileResponse("app/static/index.html")


@app.on_event("startup")
async def setup_rate_limiter() -> None:
    """Inicializa rate limiter se Redis estiver disponível."""

    settings = get_settings()
    if (
        settings.redis_url
        and redis is not None
        and FastAPILimiter is not None
        and RateLimiter is not None
    ):
        client = redis.from_url(
            settings.redis_url, encoding="utf-8", decode_responses=True
        )
        await FastAPILimiter.init(client)
        logger.info("rate_limiter.initialized", redis_url=settings.redis_url)
    else:
        logger.warning(
            "rate_limiter.disabled",
            reason="Dependências ausentes ou REDIS_URL não configurado.",
        )


async def rate_limit_dependency(
    request: Request,
    response: Response,
    route: APIRoute | None = None,
) -> None:
    """Aplica rate limit caso FastAPI Limiter esteja configurado."""

    settings = get_settings()
    if (
        not settings.redis_url
        or FastAPILimiter is None
        or RateLimiter is None
        or redis is None
    ):
        return

    limiter = RateLimiter(
        times=settings.rate_limit_requests,
        seconds=settings.rate_limit_window_seconds,
    )
    await limiter(request, response, route)


@app.get("/healthz", tags=["Monitorização"])
async def healthcheck() -> dict[str, str]:
    """Endpoint simples para verificação de saúde."""

    return {"status": "ok"}


@app.post(
    "/priorizacoes",
    response_model=PrioritizationResponse,
    tags=["Priorização"],
    dependencies=[Depends(enforce_api_key)],
)
async def priorizar_backlog(
    request: Request,
    response: Response,
    service: PrioritizationService = Depends(get_service),
    capacidade_total: Optional[int] = None,
    percentual_sustentacao: Optional[int] = None,
) -> PrioritizationResponse:
    """
    Prioriza itens do backlog armazenados no banco de dados.

    Parâmetros opcionais:
    - `capacidade_total`: Sobrescreve a capacidade total do sistema.
    - `percentual_sustentacao`: Sobrescreve o percentual de sustentação.
    
    Se não fornecidos, usa os valores configurados no sistema.
    """

    # Aplicar rate limiting
    await rate_limit_dependency(request, response, None)

    try:
        # Importar repositório
        from app.core.database import get_repository
        
        repo = get_repository()
        
        # Obter itens do banco de dados
        items = repo.list_items()
        
        if not items:
            raise HTTPException(
                status_code=400,
                detail="Nenhum item encontrado no banco de dados. Adicione itens usando POST /items primeiro.",
            )
        
        # Converter BacklogItem para formato de DataFrame
        items_dict = []
        for item in items:
            items_dict.append({
                "item": item.titulo,
                "horas": item.esforco_estimado,
                "financeiro": item.impacto_financeiro,
                "negocio": item.impacto_negocios,
                "cliente": item.impacto_cliente,
                "okr": item.okr,
                "categoria": item.categoria,
                "area": item.area,
                "estimado_qp": item.estimado_qp,
            })
        
        df = pd.DataFrame(items_dict)
        
        # Obter configurações do sistema se não fornecidas
        if capacidade_total is None or percentual_sustentacao is None:
            settings = repo.get_settings()
            capacidade_total = capacidade_total or settings.capacidade_total
            percentual_sustentacao = percentual_sustentacao or settings.percentual_sustentacao
        
        return service.process_dataframe(
            df,
            capacidade_total=capacidade_total,
            percentual_sustentacao=percentual_sustentacao,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("prioritization_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.exception_handler(ValueError)
async def handle_value_error(_: Request, exc: ValueError) -> JSONResponse:
    """Padroniza retorno para erros de validação."""

    return JSONResponse(status_code=400, content={"detail": str(exc)})
