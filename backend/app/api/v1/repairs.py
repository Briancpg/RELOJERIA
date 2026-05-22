from datetime import date

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.exceptions import AppError
from app.db.session import get_db
from app.models.repair import RepairStatus
from app.models.repair_image import RepairImageType
from app.repositories.images import RepairImageRepository
from app.schemas.repair import (
    EnvelopeExtractionResponse,
    ExtractedRepairFields,
    RepairCreate,
    RepairImageRead,
    RepairListResponse,
    RepairRead,
    RepairUpdate,
)
from app.services.extraction_service import ExtractionService
from app.services.repair_service import RepairService
from app.storage.r2 import ALLOWED_IMAGE_TYPES, R2Storage, detect_image_content_type

router = APIRouter(prefix="/repairs", tags=["repairs"], dependencies=[Depends(get_current_user)])
ALLOWED_IMAGE_UPLOAD_TYPES = {RepairImageType.watch, RepairImageType.envelope}


def validate_image_upload(content: bytes, content_type: str) -> None:
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise AppError("Unsupported image type")
    if not content:
        raise AppError("Image cannot be empty")
    detected_content_type = detect_image_content_type(content)
    if detected_content_type != content_type:
        raise AppError("Image content does not match its declared type")
    max_bytes = settings.max_image_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise AppError(f"Image exceeds {settings.max_image_upload_mb} MB")


@router.get("", response_model=RepairListResponse)
def list_repairs(
    date_from: date | None = None,
    date_to: date | None = None,
    status_filter: RepairStatus | None = Query(default=None, alias="status"),
    brand: str | None = None,
    model: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    items, total = RepairService(db).list(
        date_from=date_from,
        date_to=date_to,
        status=status_filter,
        brand=brand,
        model=model,
        search=search,
        page=page,
        page_size=page_size,
    )
    return RepairListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=RepairRead, status_code=status.HTTP_201_CREATED)
def create_repair(payload: RepairCreate, db: Session = Depends(get_db)):
    return RepairService(db).create(payload)


@router.post("/extract-envelope", response_model=EnvelopeExtractionResponse)
async def extract_envelope(file: UploadFile = File(...)):
    content = await file.read()
    content_type = file.content_type or "application/octet-stream"
    validate_image_upload(content, content_type)
    result = ExtractionService().extract_from_envelope_image(content, content_type)
    extracted = result.data
    fields = ExtractedRepairFields(
        envelope_date=extracted.repair_date,
        brand=extracted.brand,
        model=extracted.model,
        watch_color=extracted.watch_color,
        watch_specifications=extracted.watch_specifications,
        description=extracted.description,
        repair_cost=extracted.repair_cost,
        deposit_amount=extracted.deposit_amount,
        watchmaker_percentage=extracted.watchmaker_percentage,
        customer_name=extracted.customer_name,
        customer_phone=extracted.customer_phone,
        customer_document_id=extracted.customer_document_id,
        invoice_number=extracted.invoice_number,
        notes=extracted.notes,
    )
    return EnvelopeExtractionResponse(
        extracted=result.extracted,
        message=result.message,
        fields=fields,
        confidence=result.confidence,
        raw_text=result.raw_text,
        raw_transcription=result.raw_text,
        raw_text_candidates=result.raw_text_candidates,
        envelope_number=result.envelope_number,
        phone_numbers=result.phone_numbers,
        field_confidences=result.field_confidences,
        warnings=result.warnings,
    )


@router.get("/{repair_id}", response_model=RepairRead)
def get_repair(repair_id: int, db: Session = Depends(get_db)):
    return RepairService(db).get_or_raise(repair_id)


@router.patch("/{repair_id}", response_model=RepairRead)
def update_repair(repair_id: int, payload: RepairUpdate, db: Session = Depends(get_db)):
    return RepairService(db).update(repair_id, payload)


@router.delete("/{repair_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_repair(repair_id: int, db: Session = Depends(get_db)):
    RepairService(db).soft_delete(repair_id)
    return None


@router.post("/{repair_id}/images", response_model=RepairImageRead, status_code=status.HTTP_201_CREATED)
async def upload_image(
    repair_id: int,
    file: UploadFile = File(...),
    image_type: str = Form(RepairImageType.watch),
    db: Session = Depends(get_db),
):
    if image_type not in ALLOWED_IMAGE_UPLOAD_TYPES:
        raise AppError("Invalid image type")
    RepairService(db).get_or_raise(repair_id)
    content = await file.read()
    validate_image_upload(content, file.content_type or "application/octet-stream")
    stored = R2Storage().upload_image(
        repair_id=repair_id,
        file_name=file.filename or "upload",
        content_type=file.content_type or "application/octet-stream",
        content=content,
    )
    return RepairImageRepository(db).create(
        repair_id=repair_id,
        image_type=image_type,
        r2_key=stored.key,
        file_name=file.filename or stored.key,
        content_type=file.content_type or "application/octet-stream",
        file_size=len(content),
        public_url=stored.public_url,
    )


@router.get("/{repair_id}/images", response_model=list[RepairImageRead])
def list_images(repair_id: int, db: Session = Depends(get_db)):
    RepairService(db).get_or_raise(repair_id)
    return RepairImageRepository(db).list_for_repair(repair_id)


@router.delete("/{repair_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(repair_id: int, image_id: int, db: Session = Depends(get_db)):
    RepairService(db).get_or_raise(repair_id)
    repo = RepairImageRepository(db)
    image = repo.get(image_id, repair_id)
    if image:
        repo.soft_delete(image)
    return None
