from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.reports import ReportsSummary
from app.services.reports_service import ReportsService

router = APIRouter(prefix="/reports", tags=["reports"], dependencies=[Depends(get_current_user)])


@router.get("/summary", response_model=ReportsSummary)
def reports_summary(db: Session = Depends(get_db)):
    return ReportsService(db).summary()
