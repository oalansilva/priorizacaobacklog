from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.core.database import get_repository, DatabaseRepository
from app.models.db import BacklogItem

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/", response_model=List[BacklogItem])
def list_items(repo: DatabaseRepository = Depends(get_repository)):
    return repo.list_items()

@router.post("/", response_model=BacklogItem)
def add_item(item: BacklogItem, repo: DatabaseRepository = Depends(get_repository)):
    return repo.add_item(item)
