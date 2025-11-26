from typing import Optional
import os
import pandas as pd
from pathlib import Path
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


settings_instance = get_settings()

app = FastAPI(
    title="Prioriza Backlog API",
    version="0.1.0",
    description="API para priorização de demandas com AWS Bedrock + LangChain.",
    root_path=settings_instance.root_path,
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

@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    response = await call_next(request)
    # Permissive CSP for Babel standalone and external CDNs
    response.headers["Content-Security-Policy"] = "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:; script-src * 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval';"
    return response

# Get the directory where this file is located
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", include_in_schema=False)
async def read_root():
    return FileResponse(str(STATIC_DIR / "index.html"))


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
    
    # Log Database Type
    logger.info("startup.database_check", database_type=settings.database_type)
    print(f"\n🚀 USING DATABASE: {settings.database_type.upper()}\n")


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


def execute_prioritization(
    capacidade_total: Optional[int] = None,
    percentual_sustentacao: Optional[int] = None,
) -> PrioritizationResponse:
    """
    Função compartilhada para executar priorização e atualizar banco de dados.
    
    Pode ser chamada tanto pelo endpoint /priorizacoes quanto pelo agente.
    
    Args:
        capacidade_total: Capacidade total em horas (usa configuração do sistema se None)
        percentual_sustentacao: Percentual de sustentação (usa configuração do sistema se None)
    
    Returns:
        PrioritizationResponse com resultado da priorização
    
    Raises:
        HTTPException: Se não houver itens no banco de dados
    """
    from app.core.database import get_repository
    
    repo = get_repository()
    
    # Fix: Instantiate service directly to avoid Depends() issue when called from Agent
    from app.config import get_settings
    settings = get_settings()
    service = PrioritizationService(settings=settings)
    
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
            "must_have": item.must_have,
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
    
    result = service.process_dataframe(
        df,
        capacidade_total=capacidade_total,
        percentual_sustentacao=percentual_sustentacao,
    )

    # Atualizar itens no banco de dados com o resultado da priorização
    logger.info(
        "starting_database_update",
        total_result_items=len(result.itens),
        total_db_items=len(items)
    )
    
    updated_count = 0
    not_found_count = 0
    for prioritized_item in result.itens:
        # Encontrar o item original pelo título (assumindo títulos únicos por enquanto)
        # Idealmente, passaríamos o ID por todo o fluxo, mas o LLM recria a lista
        original_item = next((i for i in items if i.titulo == prioritized_item.item), None)
        
        if original_item:
            logger.info(
                "updating_item",
                item_id=original_item.id,
                titulo=original_item.titulo[:30],
                old_prioridade=original_item.prioridade,
                new_prioridade=prioritized_item.prioridade,
                old_status=original_item.status,
                new_status=prioritized_item.status
            )
            original_item.status = prioritized_item.status
            original_item.prioridade = prioritized_item.prioridade
            original_item.justificativa = prioritized_item.justificativa
            repo.update_item(original_item)
            updated_count += 1
        else:
            not_found_count += 1
            logger.warning(
                "item_not_found_in_db",
                titulo=prioritized_item.item[:50]
            )
    
    logger.info(
        "database_update_complete",
        updated_count=updated_count,
        not_found_count=not_found_count,
        total_items=len(result.itens)
    )
    
    return result


@app.post(
    "/priorizacoes",
    response_model=PrioritizationResponse,
    tags=["Priorização"],
    dependencies=[Depends(enforce_api_key)],
)
async def priorizar_backlog(
    request: Request,
    response: Response,
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
        return execute_prioritization(capacidade_total, percentual_sustentacao)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("prioritization_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.exception_handler(ValueError)
async def handle_value_error(_: Request, exc: ValueError) -> JSONResponse:
    """Padroniza retorno para erros de validação."""

    return JSONResponse(status_code=400, content={"detail": str(exc)})
