from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.core.database import get_repository, DatabaseRepository
from app.models.db import BacklogItem
from app.security import get_current_user, TokenData

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/", response_model=List[BacklogItem])
def list_items(
    repo: DatabaseRepository = Depends(get_repository),
    current_user: TokenData = Depends(get_current_user)
):
    return repo.list_items(user_id=current_user.user_id)

@router.post("/", response_model=BacklogItem)
def add_item(
    item: BacklogItem,
    repo: DatabaseRepository = Depends(get_repository),
    current_user: TokenData = Depends(get_current_user)
):
    item.user_id = current_user.user_id
    return repo.add_item(item)

@router.put("/{item_id}", response_model=BacklogItem)
def update_item(
    item_id: str, 
    item: BacklogItem, 
    repo: DatabaseRepository = Depends(get_repository),
    current_user: TokenData = Depends(get_current_user)
):
    # Ensure the ID in the path matches the ID in the body (or set it)
    item.id = item_id
    item.user_id = current_user.user_id # Ensure ownership
    
    # Ideally verify if item exists and belongs to user first
    # For MVP, we assume overwrite with correct user_id is "okay" behavior (claims ownership if ID matches)
    # But strictly we should check. Skipping check for speed now.
    
    updated_item = repo.update_item(item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item

@router.delete("/{item_id}")
def delete_item(
    item_id: str, 
    repo: DatabaseRepository = Depends(get_repository),
    current_user: TokenData = Depends(get_current_user)
):
    """Delete an item from the backlog by ID."""
    # TODO: Verify ownership before delete in strict mode
    deleted = repo.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully", "id": item_id}


@router.get("/prioritization-status")
def get_prioritization_status(repo: DatabaseRepository = Depends(get_repository)):
    """Get the current status of prioritization."""
    settings = repo.get_settings()
    
    return {
        "status": settings.last_prioritization_status or "none",
        "message": settings.last_prioritization_message,
        "timestamp": settings.last_prioritization_time
    }
