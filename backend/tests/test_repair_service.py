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
from app.schemas.repair import RepairCreate
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
        self.created_payload: RepairCreate | None = None

    def get(self, repair_id: int) -> Repair | None:
        return self.repair if repair_id == self.repair.id else None

    def update(self, repair: Repair, data: RepairUpdate, profit_amount=None) -> Repair:
        self.updated_payload = data
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(repair, key, value)
        if profit_amount is not None:
            repair.profit_amount = profit_amount
        return repair

    def create(self, data: RepairCreate, profit_amount, created_by_user_id: int | None = None) -> Repair:
        self.created_payload = data
        self.repair = make_repair(data.status, created_by_user_id=created_by_user_id)
        self.repair.repair_date = data.repair_date
        self.repair.brand = data.brand
        self.repair.model = data.model
        self.repair.description = data.description
        self.repair.repair_cost = data.repair_cost
        self.repair.internal_cost = data.internal_cost
        self.repair.watchmaker_percentage = data.watchmaker_percentage
        self.repair.profit_amount = profit_amount
        self.repair.customer_name = data.customer_name
        self.repair.customer_phone = data.customer_phone
        self.repair.notes = data.notes
        self.repair.envelope_raw_transcription = data.envelope_raw_transcription
        return self.repair


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
    assert RepairStatus.submitted not in FLOATING_PROFIT_STATUSES
    assert RepairStatus.pending in FLOATING_PROFIT_STATUSES
    assert RepairStatus.in_process in FLOATING_PROFIT_STATUSES
    assert RepairStatus.ready in FLOATING_PROFIT_STATUSES
    assert RepairStatus.delivered not in FLOATING_PROFIT_STATUSES
    assert RepairStatus.cancelled not in FLOATING_PROFIT_STATUSES


def test_repair_workflow_statuses_are_allowed():
    assert tuple(status.value for status in RepairStatus) == (
        "submitted",
        "pending",
        "in_process",
        "ready",
        "delivered",
        "cancelled",
    )
    assert not hasattr(RepairStatus, "received")
    assert not hasattr(RepairStatus, "diagnosis")
    assert not hasattr(RepairStatus, "in_repair")
    assert not hasattr(RepairStatus, "waiting_parts")
    assert not hasattr(RepairStatus, "completed")


def test_admin_can_edit_active_repair_fields():
    service = make_service(make_repair(RepairStatus.in_process))

    updated = service.update(1, RepairUpdate(brand="Citizen"))

    assert updated.brand == "Citizen"


def test_delivered_repair_sets_exit_date_when_empty():
    service = make_service(make_repair(RepairStatus.in_process))

    updated = service.update(1, RepairUpdate(status=RepairStatus.delivered))

    assert updated.status == RepairStatus.delivered
    assert updated.exit_date == date.today()


def test_jewelry_user_cannot_update_repairs():
    jewelry_user = FakeUser(id=20, role="joyeria", is_admin=True)
    service = make_service(make_repair(RepairStatus.submitted, created_by_user_id=20), jewelry_user)

    with pytest.raises(AppError, match="Admin or master"):
        service.update(1, RepairUpdate(brand="Citizen"))


def test_jewelry_user_cannot_access_other_users_repair():
    jewelry_user = FakeUser(id=20, role="joyeria", is_admin=False)
    service = make_service(make_repair(RepairStatus.submitted, created_by_user_id=99), jewelry_user)

    with pytest.raises(AppError, match="Repair not found"):
        service.get_or_raise(1)


def make_create_payload(status: RepairStatus) -> RepairCreate:
    return RepairCreate(
        repair_date=date(2026, 6, 17),
        brand="Seiko",
        model="5",
        description="Chequeo",
        repair_cost=Decimal("1000"),
        internal_cost=Decimal("300"),
        watchmaker_percentage=Decimal("50"),
        status=status,
        customer_name="Juan",
        customer_phone="809-555-1111",
        notes="nota",
        envelope_raw_transcription="texto privado",
    )


def test_jewelry_create_repair_starts_submitted_and_clears_internal_fields():
    jewelry_user = FakeUser(id=20, role="joyeria", is_admin=False)
    service = make_service(make_repair(RepairStatus.pending), jewelry_user)

    created = service.create(make_create_payload(RepairStatus.delivered))

    assert created.status == RepairStatus.submitted
    assert created.created_by_user_id == 20
    assert created.internal_cost == Decimal("0")
    assert created.watchmaker_percentage == Decimal("0")
    assert created.profit_amount == Decimal("0.00")
    assert created.notes is None
    assert created.envelope_raw_transcription is None


def test_admin_create_repair_starts_pending_even_if_payload_has_other_status():
    service = make_service(make_repair(RepairStatus.pending), FakeUser(role="admin"))

    created = service.create(make_create_payload(RepairStatus.delivered))

    assert created.status == RepairStatus.pending
    assert created.exit_date is None


def test_admin_can_move_submitted_repair_to_in_process():
    service = make_service(make_repair(RepairStatus.submitted))

    updated = service.update(1, RepairUpdate(status=RepairStatus.in_process))

    assert updated.status == RepairStatus.in_process


def test_admin_cannot_move_existing_repair_back_to_submitted():
    service = make_service(make_repair(RepairStatus.pending))

    with pytest.raises(AppError, match="Submitted status"):
        service.update(1, RepairUpdate(status=RepairStatus.submitted))
