from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    full_name: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class BacklogItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    titulo: str
    descricao: str
    esforco_estimado: int
    area: str
    dependencias: Optional[str] = None
    status: str = "Novo"  # Novo, Priorizado, Despriorizado
    prioridade: int = 999  # 1 a N, onde 1 é mais prioritário
    score: float = 0.0  # 0 a 100, calculado na priorização
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Novos campos Sim/Não
    categoria: Optional[str] = None
    impacto_financeiro: str = "Não"  # Sim/Não
    impacto_negocios: str = "Não"  # Sim/Não
    impacto_cliente: str = "Não"  # Sim/Não
    okr: str = "Não"  # Sim/Não
    must_have: str = "Não"  # Sim/Não - Item obrigatório para priorização
    estimado_qp: str = "Não"  # Sim/Não (apenas informativo)
    estimado_qp: str = "Não"  # Sim/Não (apenas informativo)
    justificativa: Optional[str] = None
    user_id: Optional[str] = None  # Dono do item


class ConversationMessage(BaseModel):
    role: str  # user, assistant
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[ConversationMessage] = []
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    user_id: Optional[str] = None  # Dono da conversa

class SystemSettings(BaseModel):
    id: int = 1
    capacidade_total: int = 1000
    percentual_sustentacao: int = 20
    peso_financeiro: int = 25
    peso_negocios: int = 25
    peso_cliente: int = 25
    peso_okr: int = 25
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())
    user_id: Optional[str] = None  # Configurações do usuário (se None, usa global/default)
    
    # Status de priorização assíncrona
    last_prioritization_status: Optional[str] = None  # "running", "completed", "error"
    last_prioritization_message: Optional[str] = None
    last_prioritization_time: Optional[str] = None


class RoadmapItem(BaseModel):
    """Snapshot de um item no momento da priorização."""
    id: str
    titulo: str
    descricao: str
    esforco_estimado: int
    area: str
    status: str  # Priorizado ou Despriorizado
    prioridade: int
    score: float
    categoria: Optional[str] = None
    impacto_financeiro: str = "Não"
    impacto_negocios: str = "Não"
    impacto_cliente: str = "Não"
    okr: str = "Não"
    must_have: str = "Não"
    justificativa: Optional[str] = None


class Roadmap(BaseModel):
    """Histórico de uma priorização executada."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    user_id: Optional[str] = None  # Dono do roadmap
    
    # Configuração usada
    capacidade_total: int
    percentual_sustentacao: int
    capacidade_iniciativas: int
    
    # Métricas
    total_itens: int
    itens_priorizados: int
    itens_despriorizados: int
    horas_alocadas: int
    
    # Snapshot dos itens
    itens: List[RoadmapItem]
    
    # Pesos usados na priorização
    peso_financeiro: int
    peso_negocios: int
    peso_cliente: int
    peso_okr: int
