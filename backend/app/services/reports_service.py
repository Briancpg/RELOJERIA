from decimal import Decimal

from sqlalchemy import case, distinct, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.repair import Repair, RepairStatus
from app.schemas.reports import NameCount, ReportsSummary
from app.services.inventory_service import InventoryService


STATUS_SORT_ORDER = (
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


class ReportsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _sum_repair_cost(self, statuses: tuple[RepairStatus, ...] | None = None) -> Decimal:
        statement = select(func.coalesce(func.sum(Repair.repair_cost), 0)).where(Repair.deleted_at.is_(None))
        if statuses is not None:
            statement = statement.where(Repair.status.in_(statuses))
        return Decimal(str(self.db.scalar(statement) or 0))

    def summary(self) -> ReportsSummary:
        active_statuses = (
            RepairStatus.diagnosis,
            RepairStatus.in_repair,
            RepairStatus.waiting_parts,
            RepairStatus.ready,
        )
        total_repairs = self.db.scalar(select(func.count()).select_from(Repair).where(Repair.deleted_at.is_(None))) or 0
        client_key = func.coalesce(
            func.nullif(Repair.customer_phone, ""),
            func.nullif(Repair.customer_document_id, ""),
            Repair.customer_name,
        )
        clients = (
            self.db.scalar(
                select(func.count(distinct(client_key))).where(
                    Repair.deleted_at.is_(None),
                    Repair.customer_name.is_not(None),
                    Repair.customer_name != "",
                )
            )
            or 0
        )
        status_counts = [
            NameCount(name=str(status), count=int(count))
            for status, count in self.db.execute(
                select(Repair.status, func.count())
                .where(Repair.deleted_at.is_(None))
                .group_by(Repair.status)
                .order_by(status_sort_expression())
            ).all()
        ]
        brand_counts = [
            NameCount(name=brand or "Sin marca", count=int(count))
            for brand, count in self.db.execute(
                select(Repair.brand, func.count())
                .where(Repair.deleted_at.is_(None))
                .group_by(Repair.brand)
                .order_by(func.count().desc(), Repair.brand)
                .limit(8)
            ).all()
        ]
        return ReportsSummary(
            currency=settings.app_currency,
            total_repairs=int(total_repairs),
            total_estimated_revenue=self._sum_repair_cost(
                (
                    RepairStatus.diagnosis,
                    RepairStatus.in_repair,
                    RepairStatus.waiting_parts,
                    RepairStatus.ready,
                    RepairStatus.delivered,
                )
            ),
            collected_revenue=self._sum_repair_cost((RepairStatus.delivered,)),
            pending_revenue=self._sum_repair_cost(active_statuses),
            registered_clients=int(clients),
            status_counts=status_counts,
            brand_counts=brand_counts,
            inventory=InventoryService(self.db).summary(),
        )
