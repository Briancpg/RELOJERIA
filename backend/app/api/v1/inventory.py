from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemRead,
    InventoryItemUpdate,
    InventoryListResponse,
    InventoryStatus,
    InventorySummary,
)
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=InventoryListResponse)
def list_inventory(
    search: str | None = None,
    category: str | None = None,
    status_filter: InventoryStatus | None = Query(default=None, alias="status"),
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
):
    items, total = InventoryService(db).list(
        search=search,
        category=category,
        status=status_filter,
        page=page,
        page_size=page_size,
    )
    return InventoryListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/summary", response_model=InventorySummary)
def inventory_summary(db: Session = Depends(get_db)):
    return InventoryService(db).summary()


@router.post("", response_model=InventoryItemRead, status_code=status.HTTP_201_CREATED)
def create_inventory_item(payload: InventoryItemCreate, db: Session = Depends(get_db)):
    return InventoryService(db).create(payload)


@router.get("/{item_id}", response_model=InventoryItemRead)
def get_inventory_item(item_id: int, db: Session = Depends(get_db)):
    return InventoryService(db).get_or_raise(item_id)


@router.patch("/{item_id}", response_model=InventoryItemRead)
def update_inventory_item(item_id: int, payload: InventoryItemUpdate, db: Session = Depends(get_db)):
    return InventoryService(db).update(item_id, payload)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_item(item_id: int, db: Session = Depends(get_db)):
    InventoryService(db).soft_delete(item_id)
    return None
