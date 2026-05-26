from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

InventoryStatus = Literal["available", "low_stock", "exhausted"]


class InventoryItemBase(BaseModel):
    reference: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=160)
    category: str = Field(min_length=1, max_length=80)
    brand: str | None = Field(default=None, max_length=120)
    description: str | None = None
    stock_quantity: int = Field(default=0, ge=0)
    minimum_stock: int = Field(default=1, ge=0)
    unit_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    location: str | None = Field(default=None, max_length=120)

    @field_validator("reference", "name", "category", "brand", "location", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    reference: str | None = Field(default=None, min_length=1, max_length=80)
    name: str | None = Field(default=None, min_length=1, max_length=160)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    brand: str | None = Field(default=None, max_length=120)
    description: str | None = None
    stock_quantity: int | None = Field(default=None, ge=0)
    minimum_stock: int | None = Field(default=None, ge=0)
    unit_price: Decimal | None = Field(default=None, ge=Decimal("0"))
    location: str | None = Field(default=None, max_length=120)

    @field_validator("reference", "name", "category", "brand", "location", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class InventoryItemRead(InventoryItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def status(self) -> InventoryStatus:
        if self.stock_quantity <= 0:
            return "exhausted"
        if self.stock_quantity <= self.minimum_stock:
            return "low_stock"
        return "available"

    model_config = ConfigDict(from_attributes=True)


class InventoryListResponse(BaseModel):
    items: list[InventoryItemRead]
    total: int
    page: int
    page_size: int


class InventorySummary(BaseModel):
    total_items: int
    available_items: int
    low_stock_items: int
    exhausted_items: int
