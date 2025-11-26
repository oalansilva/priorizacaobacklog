from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid

class BacklogItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    titulo: str
    descricao: str
    esforco_estimado: int
    area: str
    dependencias: Optional[str] = None
    status: str = "Novo"  # Novo, Priorizado, Despriorizado
    prioridade: int = 999  # 1 a N, onde 1 é mais prioritário
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Novos campos Sim/Não
    categoria: Optional[str] = None
    impacto_financeiro: str = "Não"  # Sim/Não
    impacto_negocios: str = "Não"  # Sim/Não
    impacto_cliente: str = "Não"  # Sim/Não
    okr: str = "Não"  # Sim/Não
    must_have: str = "Não"  # Sim/Não - Item obrigatório para priorização
    estimado_qp: str = "Não"  # Sim/Não (apenas informativo)
    justificativa: Optional[str] = None


class ConversationMessage(BaseModel):
    role: str  # user, assistant
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[ConversationMessage] = []
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class SystemSettings(BaseModel):
    id: int = 1
    capacidade_total: int = 1000
    percentual_sustentacao: int = 20
    peso_financeiro: int = 25
    peso_negocios: int = 25
    peso_cliente: int = 25
    peso_okr: int = 25
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Status de priorização assíncrona
    last_prioritization_status: Optional[str] = None  # "running", "completed", "error"
    last_prioritization_message: Optional[str] = None
    last_prioritization_time: Optional[str] = None

