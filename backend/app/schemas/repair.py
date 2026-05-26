from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.repair import RepairStatus


class RepairBase(BaseModel):
    repair_date: date
    envelope_date: date | None = None
    brand: str = Field(min_length=1, max_length=120)
    model: str = Field(min_length=1, max_length=120)
    watch_color: str | None = Field(default=None, max_length=80)
    watch_specifications: str | None = None
    description: str = Field(min_length=1)
    repair_cost: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    deposit_amount: Decimal | None = Field(default=None, ge=Decimal("0"))
    watchmaker_percentage: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))
    status: RepairStatus = RepairStatus.diagnosis
    customer_name: str = Field(min_length=1, max_length=160)
    customer_phone: str = Field(min_length=1, max_length=40)
    customer_document_id: str | None = Field(default=None, max_length=40)
    invoice_number: str | None = Field(default=None, max_length=80)
    notes: str | None = None
    envelope_raw_transcription: str | None = None

    @field_validator(
        "brand",
        "model",
        "watch_color",
        "watch_specifications",
        "description",
        "customer_name",
        "customer_phone",
        "customer_document_id",
        "invoice_number",
        mode="before",
    )
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class RepairCreate(RepairBase):
    pass


class RepairUpdate(BaseModel):
    repair_date: date | None = None
    envelope_date: date | None = None
    brand: str | None = Field(default=None, min_length=1, max_length=120)
    model: str | None = Field(default=None, min_length=1, max_length=120)
    watch_color: str | None = Field(default=None, max_length=80)
    watch_specifications: str | None = None
    description: str | None = Field(default=None, min_length=1)
    repair_cost: Decimal | None = Field(default=None, ge=Decimal("0"))
    deposit_amount: Decimal | None = Field(default=None, ge=Decimal("0"))
    watchmaker_percentage: Decimal | None = Field(default=None, ge=Decimal("0"), le=Decimal("100"))
    status: RepairStatus | None = None
    customer_name: str | None = Field(default=None, max_length=160)
    customer_phone: str | None = Field(default=None, max_length=40)
    customer_document_id: str | None = Field(default=None, max_length=40)
    invoice_number: str | None = Field(default=None, max_length=80)
    notes: str | None = None
    envelope_raw_transcription: str | None = None


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
    envelope_date: date | None
    brand: str
    model: str
    watch_color: str | None
    watch_specifications: str | None
    description: str
    repair_cost: Decimal
    deposit_amount: Decimal | None
    watchmaker_percentage: Decimal
    profit_amount: Decimal
    status: RepairStatus
    customer_name: str | None
    customer_phone: str | None
    customer_document_id: str | None
    invoice_number: str | None
    notes: str | None
    envelope_raw_transcription: str | None
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
    envelope_date: date | None = None
    brand: str | None = None
    model: str | None = None
    watch_color: str | None = None
    watch_specifications: str | None = None
    description: str | None = None
    repair_cost: Decimal | None = None
    deposit_amount: Decimal | None = None
    watchmaker_percentage: Decimal | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_document_id: str | None = None
    invoice_number: str | None = None
    notes: str | None = None


class EnvelopeExtractionResponse(BaseModel):
    extracted: bool
    message: str
    fields: ExtractedRepairFields
    confidence: float | None = None
    raw_text: str | None = None
    raw_transcription: str | None = None
    raw_text_candidates: list[str] = Field(default_factory=list)
    envelope_number: str | None = None
    phone_numbers: list[str] = Field(default_factory=list)
    field_confidences: dict[str, float] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
