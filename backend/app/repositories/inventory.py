from datetime import UTC, datetime

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate, InventoryStatus


class InventoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def base_query(self) -> Select[tuple[InventoryItem]]:
        return select(InventoryItem).where(InventoryItem.deleted_at.is_(None))

    def get(self, item_id: int) -> InventoryItem | None:
        return self.db.scalar(self.base_query().where(InventoryItem.id == item_id))

    def get_by_reference(self, reference: str) -> InventoryItem | None:
        return self.db.scalar(
            self.base_query().where(func.lower(InventoryItem.reference) == reference.strip().lower())
        )

    def list(
        self,
        *,
        search: str | None,
        category: str | None,
        status: InventoryStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[InventoryItem], int]:
        statement = self.base_query()
        count_statement = select(func.count()).select_from(InventoryItem).where(InventoryItem.deleted_at.is_(None))
        filters = []
        if search:
            term = f"%{search.strip()}%"
            filters.append(
                or_(
                    InventoryItem.reference.ilike(term),
                    InventoryItem.name.ilike(term),
                    InventoryItem.category.ilike(term),
                    InventoryItem.brand.ilike(term),
                    InventoryItem.location.ilike(term),
                )
            )
        if category:
            filters.append(InventoryItem.category.ilike(f"%{category.strip()}%"))
        if status == "exhausted":
            filters.append(InventoryItem.stock_quantity <= 0)
        elif status == "low_stock":
            filters.append(
                (InventoryItem.stock_quantity > 0) & (InventoryItem.stock_quantity <= InventoryItem.minimum_stock)
            )
        elif status == "available":
            filters.append(InventoryItem.stock_quantity > InventoryItem.minimum_stock)

        for item in filters:
            statement = statement.where(item)
            count_statement = count_statement.where(item)

        total = self.db.scalar(count_statement) or 0
        items = self.db.scalars(
            statement.order_by(InventoryItem.category, InventoryItem.name).offset((page - 1) * page_size).limit(page_size)
        ).all()
        return list(items), total

    def create(self, data: InventoryItemCreate) -> InventoryItem:
        item = InventoryItem(**data.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, item: InventoryItem, data: InventoryItemUpdate) -> InventoryItem:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def soft_delete(self, item: InventoryItem) -> None:
        item.deleted_at = datetime.now(UTC)
        self.db.add(item)
        self.db.commit()
