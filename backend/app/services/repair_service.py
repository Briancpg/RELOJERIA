from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import status
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.repair import Repair, RepairStatus
from app.models.user import User
from app.repositories.repairs import RepairRepository
from app.schemas.repair import RepairCreate, RepairUpdate

CENTS = Decimal("0.01")
REPAIR_STATUS_GROUPS: dict[str, tuple[RepairStatus, ...]] = {
    "active": (
        RepairStatus.received,
        RepairStatus.diagnosis,
        RepairStatus.in_repair,
        RepairStatus.waiting_parts,
        RepairStatus.ready,
    ),
    "in_process": (
        RepairStatus.received,
        RepairStatus.diagnosis,
        RepairStatus.in_repair,
        RepairStatus.waiting_parts,
    ),
    "ready": (RepairStatus.ready,),
    "delivered": (RepairStatus.delivered,),
    "cancelled": (RepairStatus.cancelled,),
}


def calculate_profit(repair_cost: Decimal, percentage: Decimal) -> Decimal:
    return (repair_cost * percentage / Decimal("100")).quantize(CENTS, rounding=ROUND_HALF_UP)


def is_admin_or_master_user(user: User) -> bool:
    return user.role in {"admin", "maestro"}


class RepairService:
    def __init__(self, db: Session, current_user: User) -> None:
        self.repairs = RepairRepository(db)
        self.current_user = current_user

    def get_or_raise(self, repair_id: int) -> Repair:
        repair = self.repairs.get(repair_id)
        if not repair:
            raise AppError("Repair not found", status.HTTP_404_NOT_FOUND)
        if not self.can_access(repair):
            raise AppError("Repair not found", status.HTTP_404_NOT_FOUND)
        return repair

    def can_access(self, repair: Repair) -> bool:
        if is_admin_or_master_user(self.current_user):
            return True
        return repair.created_by_user_id == self.current_user.id

    def ensure_admin_or_master(self) -> None:
        if not is_admin_or_master_user(self.current_user):
            raise AppError("Admin or master access required", status.HTTP_403_FORBIDDEN)

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
        status_group: str | None = None,
    ):
        if page < 1:
            raise AppError("page must be greater than 0")
        if page_size < 1 or page_size > 100:
            raise AppError("page_size must be between 1 and 100")
        if date_from and date_to and date_from > date_to:
            raise AppError("date_from cannot be after date_to")
        statuses = None
        if status_group:
            statuses = REPAIR_STATUS_GROUPS.get(status_group)
            if statuses is None:
                raise AppError("Invalid status group")
        owner_user_id = None if is_admin_or_master_user(self.current_user) else self.current_user.id
        return self.repairs.list(
            date_from=date_from,
            date_to=date_to,
            status=status,
            brand=brand,
            model=model,
            search=search,
            statuses=statuses if status is None else None,
            owner_user_id=owner_user_id,
            page=page,
            page_size=page_size,
        )

    def create(self, data: RepairCreate) -> Repair:
        if not is_admin_or_master_user(self.current_user):
            data = data.model_copy(
                update={
                    "internal_cost": Decimal("0"),
                    "watchmaker_percentage": Decimal("0"),
                    "status": RepairStatus.received,
                    "exit_date": None,
                    "notes": None,
                    "envelope_raw_transcription": None,
                }
            )
        profit = calculate_profit(data.repair_cost, data.watchmaker_percentage)
        return self.repairs.create(data, profit, created_by_user_id=self.current_user.id)

    def update(self, repair_id: int, data: RepairUpdate) -> Repair:
        self.ensure_admin_or_master()
        repair = self.get_or_raise(repair_id)
        if data.status == RepairStatus.delivered and repair.exit_date is None and data.exit_date is None:
            data = data.model_copy(update={"exit_date": datetime.now().date()})
        repair_cost = data.repair_cost if data.repair_cost is not None else repair.repair_cost
        percentage = (
            data.watchmaker_percentage
            if data.watchmaker_percentage is not None
            else repair.watchmaker_percentage
        )
        profit = calculate_profit(repair_cost, percentage)
        return self.repairs.update(repair, data, profit)

    def soft_delete(self, repair_id: int) -> None:
        self.ensure_admin_or_master()
        repair = self.get_or_raise(repair_id)
        self.repairs.soft_delete(repair)
