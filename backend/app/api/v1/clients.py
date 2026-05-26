from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.clients import ClientListResponse
from app.services.clients_service import ClientsService

router = APIRouter(prefix="/clients", tags=["clients"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=ClientListResponse)
def list_clients(
    search: str | None = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
):
    items, total = ClientsService(db).list(search=search, page=page, page_size=page_size)
    return ClientListResponse(items=items, total=total, page=page, page_size=page_size)
