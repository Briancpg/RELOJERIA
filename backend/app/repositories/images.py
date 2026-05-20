from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.repair_image import RepairImage


class RepairImageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_repair(self, repair_id: int) -> list[RepairImage]:
        statement = select(RepairImage).where(
            RepairImage.repair_id == repair_id,
            RepairImage.deleted_at.is_(None),
        )
        return list(self.db.scalars(statement).all())

    def get(self, image_id: int, repair_id: int) -> RepairImage | None:
        statement = select(RepairImage).where(
            RepairImage.id == image_id,
            RepairImage.repair_id == repair_id,
            RepairImage.deleted_at.is_(None),
        )
        return self.db.scalar(statement)

    def create(
        self,
        *,
        repair_id: int,
        image_type: str,
        r2_key: str,
        file_name: str,
        content_type: str,
        file_size: int,
        public_url: str | None,
    ) -> RepairImage:
        image = RepairImage(
            repair_id=repair_id,
            image_type=image_type,
            r2_key=r2_key,
            file_name=file_name,
            content_type=content_type,
            file_size=file_size,
            public_url=public_url,
        )
        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)
        return image

    def soft_delete(self, image: RepairImage) -> None:
        image.deleted_at = datetime.now(UTC)
        self.db.add(image)
        self.db.commit()
