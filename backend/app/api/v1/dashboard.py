from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin_or_master
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardSummary, JewelryDashboardSummary, StatusCount, WeeklyProfit
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(_: User = Depends(require_admin_or_master), db: Session = Depends(get_db)):
    return DashboardService(db).summary()


@router.get("/my-summary", response_model=JewelryDashboardSummary)
def my_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DashboardService(db).jewelry_summary(current_user.id)


@router.get("/repairs-by-status", response_model=list[StatusCount])
def repairs_by_status(_: User = Depends(require_admin_or_master), db: Session = Depends(get_db)):
    return DashboardService(db).repairs_by_status()


@router.get("/profit-by-week", response_model=list[WeeklyProfit])
def profit_by_week(
    weeks: int = 8,
    _: User = Depends(require_admin_or_master),
    db: Session = Depends(get_db),
):
    return DashboardService(db).profit_by_week(weeks=min(max(weeks, 1), 52))
