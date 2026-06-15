from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pytest

from app.core.exceptions import AppError
from app.services.dashboard_service import DashboardService
from app.models.repair import RepairStatus
from app.services.dashboard_service import FLOATING_PROFIT_STATUSES, REALIZED_PROFIT_STATUSES
from app.models.repair import Repair
from app.schemas.repair import RepairUpdate
from app.services.repair_service import RepairService, calculate_profit


@dataclass
class FakeUser:
    id: int = 10
    role: str = "admin"
    is_admin: bool = True


class FakeRepairRepository:
    def __init__(self, repair: Repair) -> None:
        self.repair = repair
        self.updated_payload: RepairUpdate | None = None

    def get(self, repair_id: int) -> Repair | None:
        return self.repair if repair_id == self.repair.id else None

    def update(self, repair: Repair, data: RepairUpdate, profit_amount=None) -> Repair:
        self.updated_payload = data
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(repair, key, value)
        if profit_amount is not None:
            repair.profit_amount = profit_amount
        return repair


def make_repair(status: RepairStatus, created_by_user_id: int | None = 10) -> Repair:
    return Repair(
        id=1,
        created_by_user_id=created_by_user_id,
        repair_date=date(2026, 5, 22),
        brand="Seiko",
        model="5",
        description="Chequeo",
        repair_cost=Decimal("1000"),
        watchmaker_percentage=Decimal("50"),
        profit_amount=Decimal("500"),
        status=status,
        customer_name="Juan",
        customer_phone="809-555-1111",
    )


def make_service(repair: Repair, user: FakeUser | None = None) -> RepairService:
    service = RepairService.__new__(RepairService)
    service.repairs = FakeRepairRepository(repair)
    service.current_user = user or FakeUser()
    return service


def test_calculate_profit_uses_decimal_rounding():
    assert calculate_profit(Decimal("1250.00"), Decimal("35")) == Decimal("437.50")
    assert calculate_profit(Decimal("10.00"), Decimal("33.333")) == Decimal("3.33")


def test_week_bounds_are_monday_to_sunday():
    start, end = DashboardService.week_bounds(date(2026, 5, 18))
    assert start == date(2026, 5, 18)
    assert end == date(2026, 5, 24)


def test_dashboard_profit_status_groups():
    assert REALIZED_PROFIT_STATUSES == (RepairStatus.delivered,)
    assert RepairStatus.received in FLOATING_PROFIT_STATUSES
    assert RepairStatus.diagnosis in FLOATING_PROFIT_STATUSES
    assert RepairStatus.in_repair in FLOATING_PROFIT_STATUSES
    assert RepairStatus.waiting_parts in FLOATING_PROFIT_STATUSES
    assert RepairStatus.ready in FLOATING_PROFIT_STATUSES
    assert RepairStatus.delivered not in FLOATING_PROFIT_STATUSES
    assert RepairStatus.cancelled not in FLOATING_PROFIT_STATUSES


def test_repair_workflow_statuses_are_allowed():
    assert tuple(status.value for status in RepairStatus) == (
        "received",
        "diagnosis",
        "in_repair",
        "waiting_parts",
        "ready",
        "delivered",
        "cancelled",
    )
    assert not hasattr(RepairStatus, "pending")
    assert not hasattr(RepairStatus, "completed")


def test_admin_can_edit_active_repair_fields():
    service = make_service(make_repair(RepairStatus.in_repair))

    updated = service.update(1, RepairUpdate(brand="Citizen"))

    assert updated.brand == "Citizen"


def test_delivered_repair_sets_exit_date_when_empty():
    service = make_service(make_repair(RepairStatus.in_repair))

    updated = service.update(1, RepairUpdate(status=RepairStatus.delivered))

    assert updated.status == RepairStatus.delivered
    assert updated.exit_date == date.today()


def test_jewelry_user_cannot_update_repairs():
    jewelry_user = FakeUser(id=20, role="joyeria", is_admin=True)
    service = make_service(make_repair(RepairStatus.received, created_by_user_id=20), jewelry_user)

    with pytest.raises(AppError, match="Admin or master"):
        service.update(1, RepairUpdate(brand="Citizen"))


def test_jewelry_user_cannot_access_other_users_repair():
    jewelry_user = FakeUser(id=20, role="joyeria", is_admin=False)
    service = make_service(make_repair(RepairStatus.received, created_by_user_id=99), jewelry_user)

    with pytest.raises(AppError, match="Repair not found"):
        service.get_or_raise(1)
