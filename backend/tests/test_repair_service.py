from datetime import date
from decimal import Decimal

from app.services.dashboard_service import DashboardService
from app.models.repair import RepairStatus
from app.services.dashboard_service import FLOATING_PROFIT_STATUSES, REALIZED_PROFIT_STATUSES
from app.services.repair_service import calculate_profit


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
