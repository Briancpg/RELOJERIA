from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email, User.deleted_at.is_(None))
        return self.db.scalar(statement)

    def create_admin(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password, is_active=True, is_admin=True)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

