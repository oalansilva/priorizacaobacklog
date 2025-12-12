from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import get_repository
from app.models.db import User
from app.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    verify_password,
    Token,
)
from app.logging import get_logger

router = APIRouter(prefix="/auth", tags=["Autenticação"])
logger = get_logger(__name__)


@router.post("/register", response_model=User)
async def register(
    user_data: dict,  # Simplificando para dict inicialmente, ideal seria Schema
    repo=Depends(get_repository),
) -> User:
    """Registra um novo usuário."""
    email = user_data.get("email")
    password = user_data.get("password")
    full_name = user_data.get("full_name")

    if not email or not password or not full_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email, senha e nome completo são obrigatórios.",
        )

    # Verificar se usuário já existe (necessita de suporte no repo, mas vamos assumir que repo.create_user trata ou verificamos antes)
    # Por enquanto, como o repo usa SQLite/DynamoDB simples, vamos apenas criar.
    # TODO: Adicionar verificação de duplicidade no repository layer.

    hashed_password = get_password_hash(password)
    
    new_user = User(
        email=email,
        password_hash=hashed_password,
        full_name=full_name
    )
    
    # repo.create_user precisa ser implementado ou adaptado
    saved_user = repo.create_user(new_user) 
    
    return saved_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    repo=Depends(get_repository),
) -> Token:
    """Login para obter token JWT."""
    user = repo.get_user_by_email(form_data.username)
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")
