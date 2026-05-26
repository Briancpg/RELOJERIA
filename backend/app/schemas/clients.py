from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class ClientSummary(BaseModel):
    client_key: str
    customer_name: str
    customer_phone: str | None
    customer_document_id: str | None
    total_repairs: int
    active_repairs: int
    delivered_repairs: int
    total_spent: Decimal
    last_repair_date: date | None


class ClientListResponse(BaseModel):
    items: list[ClientSummary]
    total: int
    page: int
    page_size: int
