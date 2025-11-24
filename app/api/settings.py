from fastapi import APIRouter, Depends
from app.core.database import get_repository, DatabaseRepository
from app.models.db import SystemSettings

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/", response_model=SystemSettings)
def get_settings(repo: DatabaseRepository = Depends(get_repository)):
    return repo.get_settings()

@router.put("/", response_model=SystemSettings)
def update_settings(settings: SystemSettings, repo: DatabaseRepository = Depends(get_repository)):
    return repo.update_settings(settings)
