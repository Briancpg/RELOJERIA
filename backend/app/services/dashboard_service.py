from datetime import date, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.repair import Repair, RepairStatus
from app.schemas.dashboard import DashboardSummary, JewelryDashboardSummary, StatusCount, WeeklyProfit

REALIZED_PROFIT_STATUSES = (RepairStatus.delivered,)
ACTIVE_REPAIR_STATUSES = (
    RepairStatus.received,
    RepairStatus.diagnosis,
    RepairStatus.in_repair,
    RepairStatus.waiting_parts,
)
FLOATING_PROFIT_STATUSES = (
    RepairStatus.received,
    RepairStatus.diagnosis,
    RepairStatus.in_repair,
    RepairStatus.waiting_parts,
    RepairStatus.ready,
)
STATUS_SORT_ORDER = (
    RepairStatus.received,
    RepairStatus.diagnosis,
    RepairStatus.in_repair,
    RepairStatus.waiting_parts,
    RepairStatus.ready,
    RepairStatus.delivered,
    RepairStatus.cancelled,
)


def status_sort_expression():
    return case(
        *[(Repair.status == status, index) for index, status in enumerate(STATUS_SORT_ORDER)],
        else_=len(STATUS_SORT_ORDER),
    )


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _today(self) -> date:
        from datetime import datetime

        return datetime.now(ZoneInfo(settings.app_timezone)).date()

    @staticmethod
    def week_bounds(day: date) -> tuple[date, date]:
        start = day - timedelta(days=day.weekday())
        return start, start + timedelta(days=6)

    def _profit_between(
        self,
        start: date | None = None,
        end: date | None = None,
        statuses: tuple[RepairStatus, ...] = REALIZED_PROFIT_STATUSES,
    ) -> Decimal:
        statement = select(func.coalesce(func.sum(Repair.profit_amount), 0)).where(Repair.deleted_at.is_(None))
        if statuses:
            statement = statement.where(Repair.status.in_(statuses))
        date_field = func.coalesce(Repair.exit_date, Repair.repair_date) if statuses == REALIZED_PROFIT_STATUSES else Repair.repair_date
        if start:
            statement = statement.where(date_field >= start)
        if end:
            statement = statement.where(date_field <= end)
        return Decimal(str(self.db.scalar(statement) or 0))

    def _count_status(self, status: RepairStatus) -> int:
        statement = select(func.count()).select_from(Repair).where(
            Repair.deleted_at.is_(None),
            Repair.status == status,
        )
        return int(self.db.scalar(statement) or 0)

    def _count_statuses(self, statuses: tuple[RepairStatus, ...], owner_user_id: int | None = None) -> int:
        statement = select(func.count()).select_from(Repair).where(
            Repair.deleted_at.is_(None),
            Repair.status.in_(statuses),
        )
        if owner_user_id is not None:
            statement = statement.where(Repair.created_by_user_id == owner_user_id)
        return int(self.db.scalar(statement) or 0)

    def _count_delivered_between(self, start: date, end: date, owner_user_id: int | None = None) -> int:
        delivered_at = func.coalesce(Repair.exit_date, Repair.repair_date)
        statement = select(func.count()).select_from(Repair).where(
            Repair.deleted_at.is_(None),
            Repair.status == RepairStatus.delivered,
            delivered_at >= start,
            delivered_at <= end,
        )
        if owner_user_id is not None:
            statement = statement.where(Repair.created_by_user_id == owner_user_id)
        return int(self.db.scalar(statement) or 0)

    def summary(self) -> DashboardSummary:
        today = self._today()
        week_start, week_end = self.week_bounds(today)
        month_start = today.replace(day=1)
        return DashboardSummary(
            currency=settings.app_currency,
            week_start=week_start,
            week_end=week_end,
            total_weekly=self._profit_between(week_start, week_end),
            total_monthly=self._profit_between(month_start, today),
            floating_weekly=self._profit_between(week_start, week_end, FLOATING_PROFIT_STATUSES),
            floating_monthly=self._profit_between(month_start, today, FLOATING_PROFIT_STATUSES),
            floating_profit=self._profit_between(statuses=FLOATING_PROFIT_STATUSES),
            pending_repairs=self._count_statuses((RepairStatus.received, RepairStatus.diagnosis)),
            delivered_repairs=self._count_status(RepairStatus.delivered),
            accumulated_profit=self._profit_between(),
            active_repairs=self._count_statuses(ACTIVE_REPAIR_STATUSES),
            ready_repairs=self._count_status(RepairStatus.ready),
            delivered_weekly=self._count_delivered_between(week_start, week_end),
        )

    def jewelry_summary(self, user_id: int) -> JewelryDashboardSummary:
        return JewelryDashboardSummary(
            sent_repairs=self._count_statuses(tuple(RepairStatus), owner_user_id=user_id),
            in_process_repairs=self._count_statuses(ACTIVE_REPAIR_STATUSES, owner_user_id=user_id),
            ready_repairs=self._count_statuses((RepairStatus.ready,), owner_user_id=user_id),
            delivered_repairs=self._count_statuses((RepairStatus.delivered,), owner_user_id=user_id),
        )

    def repairs_by_status(self) -> list[StatusCount]:
        statement = (
            select(Repair.status, func.count())
            .where(Repair.deleted_at.is_(None))
            .group_by(Repair.status)
            .order_by(status_sort_expression())
        )
        return [StatusCount(status=str(status), count=count) for status, count in self.db.execute(statement).all()]

    def profit_by_week(self, weeks: int = 8) -> list[WeeklyProfit]:
        today = self._today()
        current_start, _ = self.week_bounds(today)
        result = []
        for offset in range(weeks - 1, -1, -1):
            start = current_start - timedelta(weeks=offset)
            end = start + timedelta(days=6)
            result.append(WeeklyProfit(week_start=start, week_end=end, total_profit=self._profit_between(start, end)))
        return result
