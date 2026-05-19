from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.dashboard import DashboardSummary, StatusCount, WeeklyProfit
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)])


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db)):
    return DashboardService(db).summary()


@router.get("/repairs-by-status", response_model=list[StatusCount])
def repairs_by_status(db: Session = Depends(get_db)):
    return DashboardService(db).repairs_by_status()


@router.get("/profit-by-week", response_model=list[WeeklyProfit])
def profit_by_week(weeks: int = 8, db: Session = Depends(get_db)):
    return DashboardService(db).profit_by_week(weeks=min(max(weeks, 1), 52))

