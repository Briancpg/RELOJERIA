from datetime import date

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.repair import RepairStatus
from app.models.user import User
from app.repositories.images import RepairImageRepository
from app.schemas.repair import RepairCreate, RepairImageRead, RepairListResponse, RepairRead, RepairUpdate
from app.services.repair_service import RepairService
from app.storage.r2 import R2Storage

router = APIRouter(prefix="/repairs", tags=["repairs"], dependencies=[Depends(get_current_user)])


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
async def upload_image(repair_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    RepairService(db).get_or_raise(repair_id)
    content = await file.read()
    stored = R2Storage().upload_image(
        repair_id=repair_id,
        file_name=file.filename or "upload",
        content_type=file.content_type or "application/octet-stream",
        content=content,
    )
    return RepairImageRepository(db).create(
        repair_id=repair_id,
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

