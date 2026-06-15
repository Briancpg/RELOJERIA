from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from starlette import status

from app.auth.security import decode_token
from app.core.exceptions import AppError
from app.db.session import get_db
from app.models.user import User
from app.models.user import UserRole
from app.repositories.users import UserRepository

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise AppError("Authentication required", status.HTTP_401_UNAUTHORIZED)
    email = decode_token(credentials.credentials, "access")
    if not email:
        raise AppError("Invalid access token", status.HTTP_401_UNAUTHORIZED)
    user = UserRepository(db).get_by_email(email)
    if not user or not user.is_active:
        raise AppError("Invalid access token", status.HTTP_401_UNAUTHORIZED)
    return user


def is_admin_or_master(user: User) -> bool:
    return user.role in {UserRole.admin, UserRole.maestro}


def is_jewelry_user(user: User) -> bool:
    return user.role == UserRole.joyeria


def require_admin_or_master(current_user: User = Depends(get_current_user)) -> User:
    if not is_admin_or_master(current_user):
        raise AppError("Admin or master access required", status.HTTP_403_FORBIDDEN)
    return current_user
