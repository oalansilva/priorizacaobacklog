"""Dependências de segurança (API Key + rate limiting)."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import Settings, get_settings


def get_api_key_header(settings: Settings = Depends(get_settings)) -> APIKeyHeader:
    """Retorna instância configurada do header."""

    return APIKeyHeader(name=settings.api_key_name, auto_error=False)


async def enforce_api_key(
    api_key: str | None = Security(get_api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    """Valida a API Key enviada no header."""

    if settings.api_key_value is None:
        return

    if api_key != settings.api_key_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida ou ausente.",
        )


