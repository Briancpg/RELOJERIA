from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from starlette import status

from app.auth.security import decode_token
from app.core.exceptions import AppError
from app.db.session import get_db
from app.models.user import User
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

