"""Configurações centralizadas da aplicação."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

load_dotenv()


class Settings(BaseModel):
    """Define parâmetros de configuração carregados via variáveis de ambiente."""

    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    aws_profile: Optional[str] = Field(default=None, alias="AWS_PROFILE")
    bedrock_model_id: Optional[str] = Field(
        default=None,
        alias="BEDROCK_MODEL_ID",
    )
    bedrock_guardrail_id: Optional[str] = Field(
        default=None, alias="BEDROCK_GUARDRAIL_ID"
    )
    bedrock_guardrail_version: str = Field(
        default="DRAFT", alias="BEDROCK_GUARDRAIL_VERSION"
    )
    llm_provider: str = Field(default="bedrock", alias="LLM_PROVIDER")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    default_capacidade_total: int = Field(default=1000, alias="DEFAULT_CAPACIDADE_TOTAL")
    default_percentual_sustentacao: int = Field(
        default=20, alias="DEFAULT_PERCENTUAL_SUSTENTACAO"
    )
    storage_bucket: Optional[str] = Field(default=None, alias="STORAGE_BUCKET")
    storage_prefix: str = Field(default="roadmaps/", alias="STORAGE_PREFIX")
    resultado_sheet_name: Optional[str] = Field(
        default=None, alias="RESULTADO_SHEET_NAME"
    )
    api_key_name: str = Field(default="X-API-Key", alias="API_KEY_NAME")
    api_key_value: Optional[str] = Field(default=None, alias="API_KEY_VALUE")
    log_prefix: str = Field(default="[DIAGNÓSTICO]", alias="LOG_PREFIX")
    temperature: float = Field(default=0.3, alias="LLM_TEMPERATURE")
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")
    rate_limit_requests: int = Field(default=10, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(
        default=60, alias="RATE_LIMIT_WINDOW_SECONDS"
    )
    
    # Database Configuration
    database_type: str = Field(default="dynamodb", alias="DATABASE_TYPE")  # Changed default to dynamodb
    dynamodb_table_items: str = Field(default="backlog_items", alias="DYNAMODB_TABLE_ITEMS")
    dynamodb_table_conversations: str = Field(default="backlog_conversations", alias="DYNAMODB_TABLE_CONVERSATIONS")
    dynamodb_table_settings: str = Field(default="backlog_settings", alias="DYNAMODB_TABLE_SETTINGS")
    dynamodb_table_roadmaps: str = Field(default="backlog_roadmaps", alias="DYNAMODB_TABLE_ROADMAPS")
    dynamodb_table_users: str = Field(default="backlog_users", alias="DYNAMODB_TABLE_USERS")
    root_path: str = Field(default="", alias="ROOT_PATH")

    @field_validator("llm_provider")
    @classmethod
    def validar_provider(cls, value: str) -> str:
        permitido = {"bedrock", "openai"}
        prov = value.lower().strip()
        if prov not in permitido:
            raise ValueError(f"LLM_PROVIDER precisa ser um de {permitido}")
        return prov

    @field_validator("default_percentual_sustentacao")
    @classmethod
    def validar_percentual(cls, value: int) -> int:
        if not 0 <= value <= 100:
            raise ValueError("DEFAULT_PERCENTUAL_SUSTENTACAO deve estar entre 0 e 100")
        return value

    class Config:
        populate_by_name = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retorna configuração única para uso global."""

    data = {key: val for key, val in os.environ.items()}
    return Settings(**data)


