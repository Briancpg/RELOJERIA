from datetime import date
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import CheckConstraint, Date, Enum, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin


class RepairStatus(StrEnum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    delivered = "delivered"
    cancelled = "cancelled"


class Repair(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "repairs"
    __table_args__ = (
        CheckConstraint("repair_cost >= 0", name="repair_cost_non_negative"),
        CheckConstraint("watchmaker_percentage >= 0 AND watchmaker_percentage <= 100", name="percentage_range"),
        CheckConstraint("profit_amount >= 0", name="profit_amount_non_negative"),
        Index("ix_repairs_repair_date_status", "repair_date", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    repair_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    brand: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    model: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    repair_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    watchmaker_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    profit_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[RepairStatus] = mapped_column(
        Enum(RepairStatus, name="repair_status", native_enum=False),
        default=RepairStatus.pending,
        index=True,
        nullable=False,
    )
    customer_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    images: Mapped[list["RepairImage"]] = relationship(
        back_populates="repair", cascade="all, delete-orphan", passive_deletes=True
    )

