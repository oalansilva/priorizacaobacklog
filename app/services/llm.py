"""Fábrica para instanciar modelos LLM."""

from __future__ import annotations

from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

try:
    from langchain_aws import ChatBedrock
except ImportError as exc:  # pragma: no cover
    ChatBedrock = None  # type: ignore[assignment]

from app.config import get_settings, Settings


class MissingDependencyError(RuntimeError):
    """Erro lançado quando um provider não está disponível."""


def get_llm(settings: Optional[Settings] = None) -> BaseChatModel:
    """Retorna instância do LLM com base nas configurações."""

    cfg = settings or get_settings()
    provider = cfg.llm_provider.lower()

    if provider == "bedrock":
        if ChatBedrock is None:
            raise MissingDependencyError(
                "langchain-aws não está instalado. Execute `pip install langchain-aws`."
            )

        return ChatBedrock(
            model_id=cfg.bedrock_model_id,
            region_name=cfg.aws_region,
            credentials_profile_name=cfg.aws_profile,
            temperature=cfg.temperature,
        )

    if provider == "openai":
        if not cfg.openai_api_key:
            raise MissingDependencyError(
                "OPENAI_API_KEY não definido nas variáveis de ambiente."
            )

        return ChatOpenAI(
            model=cfg.openai_model,
            temperature=cfg.temperature,
            api_key=cfg.openai_api_key,
        )

    raise ValueError(f"Provider LLM '{provider}' não suportado.")


