from decimal import Decimal

from sqlalchemy import CheckConstraint, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin, TimestampMixin


class InventoryItem(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "inventory_items"
    __table_args__ = (
        CheckConstraint("stock_quantity >= 0", name="inventory_stock_non_negative"),
        CheckConstraint("minimum_stock >= 0", name="inventory_minimum_stock_non_negative"),
        CheckConstraint("unit_price >= 0", name="inventory_unit_price_non_negative"),
        Index("ix_inventory_items_reference", "reference", unique=True),
        Index("ix_inventory_items_category_brand", "category", "brand"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reference: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    brand: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    minimum_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
