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
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Novos campos Sim/Não
    categoria: Optional[str] = None
    impacto_financeiro: str = "Não"  # Sim/Não
    impacto_negocios: str = "Não"  # Sim/Não
    impacto_cliente: str = "Não"  # Sim/Não
    okr: str = "Não"  # Sim/Não
    estimado_qp: str = "Não"  # Sim/Não
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
    capacidade_total: int = 1000
    percentual_sustentacao: int = 20
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
