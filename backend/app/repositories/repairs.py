from datetime import UTC, date, datetime

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.repair import Repair, RepairStatus
from app.schemas.repair import RepairCreate, RepairUpdate


class RepairRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def base_query(self) -> Select[tuple[Repair]]:
        return select(Repair).options(selectinload(Repair.images)).where(Repair.deleted_at.is_(None))

    def get(self, repair_id: int) -> Repair | None:
        statement = self.base_query().where(Repair.id == repair_id)
        return self.db.scalar(statement)

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
    ) -> tuple[list[Repair], int]:
        statement = self.base_query()
        count_statement = select(func.count()).select_from(Repair).where(Repair.deleted_at.is_(None))

        filters = []
        if date_from:
            filters.append(Repair.repair_date >= date_from)
        if date_to:
            filters.append(Repair.repair_date <= date_to)
        if status:
            filters.append(Repair.status == status)
        if brand:
            filters.append(Repair.brand.ilike(f"%{brand.strip()}%"))
        if model:
            filters.append(Repair.model.ilike(f"%{model.strip()}%"))
        if search:
            term = f"%{search.strip()}%"
            filters.append(or_(Repair.brand.ilike(term), Repair.model.ilike(term), Repair.description.ilike(term)))

        for item in filters:
            statement = statement.where(item)
            count_statement = count_statement.where(item)

        total = self.db.scalar(count_statement) or 0
        items = self.db.scalars(
            statement.order_by(Repair.repair_date.desc(), Repair.id.desc()).offset((page - 1) * page_size).limit(page_size)
        ).all()
        return list(items), total

    def create(self, data: RepairCreate, profit_amount) -> Repair:
        repair = Repair(**data.model_dump(), profit_amount=profit_amount)
        self.db.add(repair)
        self.db.commit()
        self.db.refresh(repair)
        return self.get(repair.id) or repair

    def update(self, repair: Repair, data: RepairUpdate, profit_amount=None) -> Repair:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(repair, key, value)
        if profit_amount is not None:
            repair.profit_amount = profit_amount
        self.db.add(repair)
        self.db.commit()
        self.db.refresh(repair)
        return self.get(repair.id) or repair

    def soft_delete(self, repair: Repair) -> None:
        repair.deleted_at = datetime.now(UTC)
        self.db.add(repair)
        self.db.commit()

