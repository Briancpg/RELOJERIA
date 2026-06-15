from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_admin_or_master
from app.db.session import get_db
from app.schemas.reports import ReportsSummary
from app.services.reports_service import ReportsService

router = APIRouter(prefix="/reports", tags=["reports"], dependencies=[Depends(require_admin_or_master)])


@router.get("/summary", response_model=ReportsSummary)
def reports_summary(db: Session = Depends(get_db)):
    return ReportsService(db).summary()
