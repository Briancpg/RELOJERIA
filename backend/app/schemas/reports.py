from decimal import Decimal

from pydantic import BaseModel

from app.schemas.inventory import InventorySummary


class NameCount(BaseModel):
    name: str
    count: int


class ReportsSummary(BaseModel):
    currency: str
    total_repairs: int
    total_estimated_revenue: Decimal
    collected_revenue: Decimal
    pending_revenue: Decimal
    registered_clients: int
    status_counts: list[NameCount]
    brand_counts: list[NameCount]
    inventory: InventorySummary
