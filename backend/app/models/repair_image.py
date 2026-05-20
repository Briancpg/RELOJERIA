from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin


class RepairImageType:
    watch = "watch"
    envelope = "envelope"


class RepairImage(Base, SoftDeleteMixin):
    __tablename__ = "repair_images"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    repair_id: Mapped[int] = mapped_column(ForeignKey("repairs.id", ondelete="CASCADE"), index=True, nullable=False)
    image_type: Mapped[str] = mapped_column(String(30), default=RepairImageType.watch, nullable=False, index=True)
    r2_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    public_url: Mapped[str | None] = mapped_column(String(700), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    repair: Mapped["Repair"] = relationship(back_populates="images")

