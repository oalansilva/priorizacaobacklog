"""Módulo de segurança para autenticação e autorização."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import Settings, get_settings

# Configurações de Senha e Token
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Constantes de JWT (idealmente no config.py)
SECRET_KEY = "CHANGE_THIS_TO_A_SECURE_SECRET_KEY_IN_PRODUCTION"  # FIXME: Mover para Settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None


def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password):
    return PWD_CONTEXT.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(OAUTH2_SCHEME),
    # repo=Depends(get_repository) # Evitar dependência circular se possível, ou importar dentro
) -> TokenData:
    """Valida o token e retorna os dados do usuário (TokenData)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if username is None:
            raise credentials_exception
            
        token_data = TokenData(username=username, user_id=user_id)
        
    except JWTError:
        raise credentials_exception
        
    return token_data


# Manter compatibilidade com API Key antiga se necessário, ou remover.
# Para manter compatibilidade com o código existente que usa enforce_api_key:
def get_api_key_header(settings: Settings = Depends(get_settings)) -> APIKeyHeader:
    """Retorna instância configurada do header."""
    return APIKeyHeader(name=settings.api_key_name, auto_error=False)

async def enforce_api_key(
    api_key: str | None = Security(get_api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    """Valida a API Key enviada no header (Depreciado/Legado)."""
    if settings.api_key_value is None:
        return

    if api_key != settings.api_key_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida ou ausente.",
        )
