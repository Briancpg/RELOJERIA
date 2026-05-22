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


class FakeRepairRepository:
    def __init__(self, repair: Repair) -> None:
        self.repair = repair
        self.updated_payload: RepairUpdate | None = None

    def get(self, repair_id: int) -> Repair | None:
        return self.repair if repair_id == self.repair.id else None

    def update(self, repair: Repair, data: RepairUpdate, profit_amount=None) -> Repair:
        self.updated_payload = data
        if data.status is not None:
            repair.status = data.status
        if profit_amount is not None:
            repair.profit_amount = profit_amount
        return repair


def make_repair(status: RepairStatus) -> Repair:
    return Repair(
        id=1,
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


def make_service(repair: Repair) -> RepairService:
    service = RepairService.__new__(RepairService)
    service.repairs = FakeRepairRepository(repair)
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
    assert RepairStatus.pending in FLOATING_PROFIT_STATUSES
    assert RepairStatus.in_progress in FLOATING_PROFIT_STATUSES
    assert RepairStatus.delivered not in FLOATING_PROFIT_STATUSES
    assert RepairStatus.cancelled not in FLOATING_PROFIT_STATUSES


def test_only_four_repair_statuses_are_allowed():
    assert tuple(status.value for status in RepairStatus) == (
        "pending",
        "in_progress",
        "delivered",
        "cancelled",
    )
    assert not hasattr(RepairStatus, "completed")


def test_non_pending_repair_rejects_field_edits():
    service = make_service(make_repair(RepairStatus.in_progress))

    with pytest.raises(AppError, match="pendiente"):
        service.update(1, RepairUpdate(brand="Citizen"))


def test_non_pending_repair_allows_status_change_only():
    service = make_service(make_repair(RepairStatus.in_progress))

    updated = service.update(1, RepairUpdate(status=RepairStatus.delivered))

    assert updated.status == RepairStatus.delivered
