from decimal import Decimal

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.repair import Repair, RepairStatus
from app.schemas.clients import ClientSummary


class ClientsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, *, search: str | None, page: int, page_size: int) -> tuple[list[ClientSummary], int]:
        if page < 1:
            raise AppError("page must be greater than 0")
        if page_size < 1 or page_size > 100:
            raise AppError("page_size must be between 1 and 100")

        client_key = func.coalesce(
            func.nullif(Repair.customer_phone, ""),
            func.nullif(Repair.customer_document_id, ""),
            Repair.customer_name,
        ).label("client_key")
        filters = [Repair.deleted_at.is_(None), Repair.customer_name.is_not(None), Repair.customer_name != ""]
        if search:
            term = f"%{search.strip()}%"
            filters.append(
                or_(
                    Repair.customer_name.ilike(term),
                    Repair.customer_phone.ilike(term),
                    Repair.customer_document_id.ilike(term),
                    Repair.invoice_number.ilike(term),
                )
            )

        active_case = case(
            (
                Repair.status.in_(
                    (
                        RepairStatus.diagnosis,
                        RepairStatus.in_repair,
                        RepairStatus.waiting_parts,
                        RepairStatus.ready,
                    )
                ),
                1,
            ),
            else_=0,
        )
        delivered_case = case((Repair.status == RepairStatus.delivered, 1), else_=0)
        spent_case = case((Repair.status == RepairStatus.delivered, Repair.repair_cost), else_=0)
        grouped = (
            select(
                client_key,
                func.max(Repair.customer_name).label("customer_name"),
                func.max(Repair.customer_phone).label("customer_phone"),
                func.max(Repair.customer_document_id).label("customer_document_id"),
                func.count(Repair.id).label("total_repairs"),
                func.coalesce(func.sum(active_case), 0).label("active_repairs"),
                func.coalesce(func.sum(delivered_case), 0).label("delivered_repairs"),
                func.coalesce(func.sum(spent_case), 0).label("total_spent"),
                func.max(Repair.repair_date).label("last_repair_date"),
            )
            .where(*filters)
            .group_by(client_key)
        ).subquery()

        total = self.db.scalar(select(func.count()).select_from(grouped)) or 0
        rows = self.db.execute(
            select(grouped)
            .order_by(grouped.c.last_repair_date.desc().nullslast(), grouped.c.customer_name)
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        items = [
            ClientSummary(
                client_key=str(row.client_key),
                customer_name=row.customer_name,
                customer_phone=row.customer_phone,
                customer_document_id=row.customer_document_id,
                total_repairs=int(row.total_repairs),
                active_repairs=int(row.active_repairs),
                delivered_repairs=int(row.delivered_repairs),
                total_spent=Decimal(str(row.total_spent or 0)),
                last_repair_date=row.last_repair_date,
            )
            for row in rows
        ]
        return items, int(total)
