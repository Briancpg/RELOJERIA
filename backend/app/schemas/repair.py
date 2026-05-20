from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.repair import RepairStatus


class RepairBase(BaseModel):
    repair_date: date
    brand: str = Field(min_length=1, max_length=120)
    model: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1)
    repair_cost: Decimal = Field(ge=Decimal("0"))
    watchmaker_percentage: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))
    status: RepairStatus = RepairStatus.pending
    customer_name: str | None = Field(default=None, max_length=160)
    notes: str | None = None

    @field_validator("brand", "model", "description", "customer_name", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class RepairCreate(RepairBase):
    pass


class RepairUpdate(BaseModel):
    repair_date: date | None = None
    brand: str | None = Field(default=None, min_length=1, max_length=120)
    model: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, min_length=1)
    repair_cost: Decimal | None = Field(default=None, ge=Decimal("0"))
    watchmaker_percentage: Decimal | None = Field(default=None, ge=Decimal("0"), le=Decimal("100"))
    status: RepairStatus | None = None
    customer_name: str | None = Field(default=None, max_length=160)
    notes: str | None = None


class RepairImageRead(BaseModel):
    id: int
    repair_id: int
    image_type: str
    file_name: str
    content_type: str
    file_size: int
    public_url: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RepairRead(BaseModel):
    id: int
    repair_date: date
    brand: str
    model: str
    description: str
    repair_cost: Decimal
    watchmaker_percentage: Decimal
    profit_amount: Decimal
    status: RepairStatus
    customer_name: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    images: list[RepairImageRead] = []

    model_config = ConfigDict(from_attributes=True)


class RepairListResponse(BaseModel):
    items: list[RepairRead]
    total: int
    page: int
    page_size: int


class ExtractedRepairFields(BaseModel):
    repair_date: date | None = None
    brand: str | None = None
    model: str | None = None
    description: str | None = None
    repair_cost: Decimal | None = None
    watchmaker_percentage: Decimal | None = None
    customer_name: str | None = None
    notes: str | None = None


class EnvelopeExtractionResponse(BaseModel):
    extracted: bool
    message: str
    fields: ExtractedRepairFields
    confidence: float | None = None
    raw_text: str | None = None
