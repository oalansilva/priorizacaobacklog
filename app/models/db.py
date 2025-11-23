from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid

class BacklogItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    titulo: str
    descricao: str
    valor_negocio: str  # Alto, Médio, Baixo
    esforco_estimado: int
    area: str
    dependencias: Optional[str] = None
    prazo: Optional[str] = None
    status: str = "Novo"  # Novo, Priorizado, Despriorizado
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class ConversationMessage(BaseModel):
    role: str  # user, assistant
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[ConversationMessage] = []
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
