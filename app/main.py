"""Aplicação FastAPI para priorização de backlog."""

from __future__ import annotations

import io
from typing import Optional

import pandas as pd
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
)
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

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

logger = get_logger(__name__)


def get_service(settings: Settings = Depends(get_settings)) -> PrioritizationService:
    """Dependência para obter o serviço principal."""

    return PrioritizationService(settings=settings)


app = FastAPI(
    title="Prioriza Backlog API",
    version="0.1.0",
    description="API para priorização de demandas com AWS Bedrock + LangChain.",
)


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
)
async def priorizar_backlog(
    request: Request,
    service: PrioritizationService = Depends(get_service),
    _auth: None = Depends(enforce_api_key),
    _rate: None = Depends(rate_limit_dependency),
    file: Optional[UploadFile] = File(
        default=None, description="CSV contendo as demandas."
    ),
    capacidade_total: Optional[int] = Form(
        default=None, description="Sobrescreve a capacidade total via formulário."
    ),
    percentual_sustentacao: Optional[int] = Form(
        default=None,
        description="Sobrescreve o percentual de sustentação via formulário.",
    ),
) -> PrioritizationResponse:
    """
    Prioriza itens enviados via JSON ou upload CSV.

    - Content-Type `application/json`: enviar `PrioritizationRequest`.
    - Content-Type `multipart/form-data`: enviar arquivo CSV em `file`.
    """

    content_type = request.headers.get("content-type", "")

    try:
        if content_type.startswith("application/json"):
            payload = await request.json()
            dados = PrioritizationRequest.model_validate(payload)
            df = pd.DataFrame([item.model_dump() for item in dados.itens])
            return service.process_dataframe(
                df,
                capacidade_total=dados.capacidade_total,
                percentual_sustentacao=dados.percentual_sustentacao,
            )

        if "multipart/form-data" in content_type:
            if not file:
                raise HTTPException(
                    status_code=400,
                    detail="Envie o ficheiro CSV no campo 'file'.",
                )

            conteudo = await file.read()
            buffer = io.BytesIO(conteudo)
            df = pd.read_csv(buffer, sep=";")
            return service.process_dataframe(
                df,
                capacidade_total=capacidade_total,
                percentual_sustentacao=percentual_sustentacao,
            )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    raise HTTPException(
        status_code=415,
        detail="Content-Type não suportado. Use application/json ou multipart/form-data.",
    )


@app.exception_handler(ValueError)
async def handle_value_error(_: Request, exc: ValueError) -> JSONResponse:
    """Padroniza retorno para erros de validação."""

    return JSONResponse(status_code=400, content={"detail": str(exc)})


