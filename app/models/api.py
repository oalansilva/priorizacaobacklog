from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class DemandItem(BaseModel):
    """Representa um item de backlog a ser priorizado."""
    item: str = Field(..., description="Nome ou descrição do item.")
    horas: float = Field(..., ge=0, description="Esforço estimado em horas.")
    cliente: Optional[str] = Field(None, description="Impacto no cliente.")
    negocio: Optional[str] = Field(None, description="Impacto no negócio.")
    financeiro: Optional[str] = Field(None, description="Impacto financeiro.")
    okr: Optional[str] = Field(None, description="OKR relacionado.")
    estimado_qp: Optional[str] = Field(None, description="Estimado QP.")
    categoria: Optional[str] = Field(None, description="Categoria do item.")
    area: Optional[str] = Field(None, description="Área responsável.")
    outros_dados: Optional[dict] = Field(
        default=None, description="Campo livre para atributos adicionais."
    )

    @field_validator("item")
    @classmethod
    def validar_item(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Item não pode ser vazio.")
        return value.strip()

class PrioritizedItem(DemandItem):
    """Item priorizado pelo LLM."""
    prioridade: int = Field(..., ge=1)
    justificativa: str = Field(..., description="Motivação fornecida pelo modelo.")
    status: str = Field(..., description="Priorizado ou Despriorizado.")

class PrioritizationRequest(BaseModel):
    """Payload de entrada para API/serviços internos."""
    capacidade_total: int = Field(..., gt=0)
    percentual_sustentacao: int = Field(default=20, ge=0, le=100)
    itens: List[DemandItem] = Field(..., min_length=1)

class PrioritizationResponse(BaseModel):
    """Resposta retornada pela API ou pelo serviço CLI."""
    capacidade_iniciativas: float
    horas_alocadas: float
    itens: List[PrioritizedItem]
    roadmap_url: Optional[str] = None
    gerado_em: datetime = Field(default_factory=datetime.utcnow)
