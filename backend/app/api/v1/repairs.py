from datetime import date

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, is_jewelry_user
from app.core.config import settings
from app.core.exceptions import AppError
from app.db.session import get_db
from app.models.repair import RepairStatus
from app.models.repair_image import RepairImageType
from app.models.user import User
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

router = APIRouter(prefix="/repairs", tags=["repairs"])
ALLOWED_IMAGE_UPLOAD_TYPES = {RepairImageType.watch, RepairImageType.envelope}


def repair_for_user(repair, current_user: User) -> RepairRead:
    item = RepairRead.model_validate(repair)
    if is_jewelry_user(current_user):
        return item.model_copy(
            update={
                "internal_cost": None,
                "watchmaker_percentage": None,
                "profit_amount": None,
                "notes": None,
                "envelope_raw_transcription": None,
            }
        )
    return item


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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, total = RepairService(db, current_user).list(
        date_from=date_from,
        date_to=date_to,
        status=status_filter,
        brand=brand,
        model=model,
        search=search,
        page=page,
        page_size=page_size,
    )
    return RepairListResponse(
        items=[repair_for_user(item, current_user) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=RepairRead, status_code=status.HTTP_201_CREATED)
def create_repair(payload: RepairCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return repair_for_user(RepairService(db, current_user).create(payload), current_user)


@router.post("/extract-envelope", response_model=EnvelopeExtractionResponse)
async def extract_envelope(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
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
    response = EnvelopeExtractionResponse(
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
    if is_jewelry_user(current_user):
        return response.model_copy(
            update={
                "message": "Campos sugeridos por Vision AI. Revisa y corrige antes de guardar.",
                "fields": response.fields.model_copy(
                    update={
                        "repair_cost": None,
                        "deposit_amount": None,
                        "watchmaker_percentage": None,
                        "notes": None,
                    }
                ),
                "raw_text": None,
                "raw_transcription": None,
                "raw_text_candidates": [],
                "field_confidences": {
                    key: value
                    for key, value in response.field_confidences.items()
                    if key not in {"repair_cost", "deposit_amount", "watchmaker_percentage", "notes"}
                },
            }
        )
    return response


@router.get("/{repair_id}", response_model=RepairRead)
def get_repair(repair_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return repair_for_user(RepairService(db, current_user).get_or_raise(repair_id), current_user)


@router.patch("/{repair_id}", response_model=RepairRead)
def update_repair(
    repair_id: int,
    payload: RepairUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return repair_for_user(RepairService(db, current_user).update(repair_id, payload), current_user)


@router.delete("/{repair_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_repair(repair_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    RepairService(db, current_user).soft_delete(repair_id)
    return None


@router.post("/{repair_id}/images", response_model=RepairImageRead, status_code=status.HTTP_201_CREATED)
async def upload_image(
    repair_id: int,
    file: UploadFile = File(...),
    image_type: str = Form(RepairImageType.watch),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if image_type not in ALLOWED_IMAGE_UPLOAD_TYPES:
        raise AppError("Invalid image type")
    RepairService(db, current_user).get_or_raise(repair_id)
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
def list_images(repair_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    RepairService(db, current_user).get_or_raise(repair_id)
    return RepairImageRepository(db).list_for_repair(repair_id)


@router.delete("/{repair_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    repair_id: int,
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    RepairService(db, current_user).get_or_raise(repair_id)
    repo = RepairImageRepository(db)
    image = repo.get(image_id, repair_id)
    if image:
        repo.soft_delete(image)
    return None
