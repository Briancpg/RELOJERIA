from fastapi import status
from sqlalchemy.orm import Session

from app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.config import settings
from app.core.exceptions import AppError
from app.models.user import User
from app.repositories.users import UserRepository


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def ensure_admin_seed(self) -> None:
        existing = self.users.get_by_email(settings.admin_email)
        if existing:
            return
        self.users.create_admin(settings.admin_email, hash_password(settings.admin_password))

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if not user or not user.is_active or not verify_password(password, user.hashed_password):
            raise AppError("Invalid email or password", status.HTTP_401_UNAUTHORIZED)
        return user

    def issue_tokens(self, user: User):
        return {
            "access_token": create_access_token(user.email),
            "refresh_token": create_refresh_token(user.email),
            "token_type": "bearer",
        }

    def refresh(self, refresh_token: str):
        email = decode_token(refresh_token, "refresh")
        if not email:
            raise AppError("Invalid refresh token", status.HTTP_401_UNAUTHORIZED)
        user = self.users.get_by_email(email)
        if not user or not user.is_active:
            raise AppError("Invalid refresh token", status.HTTP_401_UNAUTHORIZED)
        return self.issue_tokens(user)

