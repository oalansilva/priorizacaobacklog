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

@router.put("/{item_id}", response_model=BacklogItem)
def update_item(item_id: str, item: BacklogItem, repo: DatabaseRepository = Depends(get_repository)):
    # Ensure the ID in the path matches the ID in the body (or set it)
    item.id = item_id
    updated_item = repo.update_item(item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item

@router.delete("/{item_id}")
def delete_item(item_id: str, repo: DatabaseRepository = Depends(get_repository)):
    """Delete an item from the backlog by ID."""
    deleted = repo.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully", "id": item_id}
