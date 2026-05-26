from fastapi import status as http_status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.inventory import InventoryItem
from app.repositories.inventory import InventoryRepository
from app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate, InventoryStatus, InventorySummary


class InventoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.items = InventoryRepository(db)

    def get_or_raise(self, item_id: int) -> InventoryItem:
        item = self.items.get(item_id)
        if not item:
            raise AppError("Inventory item not found", http_status.HTTP_404_NOT_FOUND)
        return item

    def list(
        self,
        *,
        search: str | None,
        category: str | None,
        status: InventoryStatus | None,
        page: int,
        page_size: int,
    ):
        if page < 1:
            raise AppError("page must be greater than 0")
        if page_size < 1 or page_size > 100:
            raise AppError("page_size must be between 1 and 100")
        return self.items.list(search=search, category=category, status=status, page=page, page_size=page_size)

    def create(self, data: InventoryItemCreate) -> InventoryItem:
        if self.items.get_by_reference(data.reference):
            raise AppError("Inventory reference already exists")
        return self.items.create(data)

    def update(self, item_id: int, data: InventoryItemUpdate) -> InventoryItem:
        item = self.get_or_raise(item_id)
        if data.reference and data.reference.lower() != item.reference.lower():
            existing = self.items.get_by_reference(data.reference)
            if existing and existing.id != item.id:
                raise AppError("Inventory reference already exists")
        return self.items.update(item, data)

    def soft_delete(self, item_id: int) -> None:
        self.items.soft_delete(self.get_or_raise(item_id))

    def summary(self) -> InventorySummary:
        base = InventoryItem.deleted_at.is_(None)
        total = self.db.scalar(select(func.count()).select_from(InventoryItem).where(base)) or 0
        exhausted = (
            self.db.scalar(
                select(func.count()).select_from(InventoryItem).where(base, InventoryItem.stock_quantity <= 0)
            )
            or 0
        )
        low_stock = (
            self.db.scalar(
                select(func.count()).select_from(InventoryItem).where(
                    base,
                    InventoryItem.stock_quantity > 0,
                    InventoryItem.stock_quantity <= InventoryItem.minimum_stock,
                )
            )
            or 0
        )
        available = (
            self.db.scalar(
                select(func.count()).select_from(InventoryItem).where(
                    base,
                    InventoryItem.stock_quantity > InventoryItem.minimum_stock,
                )
            )
            or 0
        )
        return InventorySummary(
            total_items=int(total),
            available_items=int(available),
            low_stock_items=int(low_stock),
            exhausted_items=int(exhausted),
        )
