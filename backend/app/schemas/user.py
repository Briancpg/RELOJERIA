from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}
