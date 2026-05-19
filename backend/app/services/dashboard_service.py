from datetime import date, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.repair import Repair, RepairStatus
from app.schemas.dashboard import DashboardSummary, StatusCount, WeeklyProfit


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

    def _profit_between(self, start: date | None = None, end: date | None = None) -> Decimal:
        statement = select(func.coalesce(func.sum(Repair.profit_amount), 0)).where(Repair.deleted_at.is_(None))
        if start:
            statement = statement.where(Repair.repair_date >= start)
        if end:
            statement = statement.where(Repair.repair_date <= end)
        return Decimal(str(self.db.scalar(statement) or 0))

    def _count_status(self, status: RepairStatus) -> int:
        statement = select(func.count()).select_from(Repair).where(
            Repair.deleted_at.is_(None),
            Repair.status == status,
        )
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
            pending_repairs=self._count_status(RepairStatus.pending),
            delivered_repairs=self._count_status(RepairStatus.delivered),
            accumulated_profit=self._profit_between(),
        )

    def repairs_by_status(self) -> list[StatusCount]:
        statement = (
            select(Repair.status, func.count())
            .where(Repair.deleted_at.is_(None))
            .group_by(Repair.status)
            .order_by(Repair.status)
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

