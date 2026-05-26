from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from fastapi import status
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.repair import Repair, RepairStatus
from app.repositories.repairs import RepairRepository
from app.schemas.repair import RepairCreate, RepairUpdate

CENTS = Decimal("0.01")


def calculate_profit(repair_cost: Decimal, percentage: Decimal) -> Decimal:
    return (repair_cost * percentage / Decimal("100")).quantize(CENTS, rounding=ROUND_HALF_UP)


class RepairService:
    def __init__(self, db: Session) -> None:
        self.repairs = RepairRepository(db)

    def get_or_raise(self, repair_id: int) -> Repair:
        repair = self.repairs.get(repair_id)
        if not repair:
            raise AppError("Repair not found", status.HTTP_404_NOT_FOUND)
        return repair

    def list(
        self,
        *,
        date_from: date | None,
        date_to: date | None,
        status: RepairStatus | None,
        brand: str | None,
        model: str | None,
        search: str | None,
        page: int,
        page_size: int,
    ):
        if page < 1:
            raise AppError("page must be greater than 0")
        if page_size < 1 or page_size > 100:
            raise AppError("page_size must be between 1 and 100")
        if date_from and date_to and date_from > date_to:
            raise AppError("date_from cannot be after date_to")
        return self.repairs.list(
            date_from=date_from,
            date_to=date_to,
            status=status,
            brand=brand,
            model=model,
            search=search,
            page=page,
            page_size=page_size,
        )

    def create(self, data: RepairCreate) -> Repair:
        profit = calculate_profit(data.repair_cost, data.watchmaker_percentage)
        return self.repairs.create(data, profit)

    def update(self, repair_id: int, data: RepairUpdate) -> Repair:
        repair = self.get_or_raise(repair_id)
        update_data = data.model_dump(exclude_unset=True)
        editable_fields = set(update_data) - {"status"}
        if repair.status != RepairStatus.diagnosis and editable_fields:
            raise AppError("Solo se puede editar una reparacion en estado en diagnostico")
        repair_cost = data.repair_cost if data.repair_cost is not None else repair.repair_cost
        percentage = (
            data.watchmaker_percentage
            if data.watchmaker_percentage is not None
            else repair.watchmaker_percentage
        )
        profit = calculate_profit(repair_cost, percentage)
        return self.repairs.update(repair, data, profit)

    def soft_delete(self, repair_id: int) -> None:
        repair = self.get_or_raise(repair_id)
        self.repairs.soft_delete(repair)
