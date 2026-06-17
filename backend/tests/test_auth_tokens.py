import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.router import api_router
from app.auth.security import create_access_token, create_refresh_token, decode_token, hash_password
from app.core.exceptions import AppError, register_exception_handlers
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User, UserRole
from app.services.auth_service import AuthService


def test_token_type_is_enforced():
    access = create_access_token("admin@example.com")
    refresh = create_refresh_token("admin@example.com")

    assert decode_token(access, "access") == "admin@example.com"
    assert decode_token(access, "refresh") is None
    assert decode_token(refresh, "refresh") == "admin@example.com"


@pytest.fixture()
def auth_db():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db:
        yield db
    Base.metadata.drop_all(bind=engine)


def test_change_password_requires_current_password(auth_db):
    user = User(
        email="maestro@example.com",
        hashed_password=hash_password("old-password"),
        role=UserRole.maestro,
        is_admin=False,
        is_active=True,
    )
    auth_db.add(user)
    auth_db.commit()

    with pytest.raises(AppError):
        AuthService(auth_db).change_password(user, "wrong-password", "new-password-123")

    assert AuthService(auth_db).authenticate("maestro@example.com", "old-password")


def test_change_password_updates_hash_and_allows_new_login(auth_db):
    user = User(
        email="maestro@example.com",
        hashed_password=hash_password("old-password"),
        role=UserRole.maestro,
        is_admin=False,
        is_active=True,
    )
    auth_db.add(user)
    auth_db.commit()

    AuthService(auth_db).change_password(user, "old-password", "new-password-123")

    with pytest.raises(AppError):
        AuthService(auth_db).authenticate("maestro@example.com", "old-password")
    assert AuthService(auth_db).authenticate("maestro@example.com", "new-password-123")


def test_change_password_endpoint_requires_auth_and_updates_password(auth_db):
    user = User(
        email="maestro@example.com",
        hashed_password=hash_password("old-password"),
        role=UserRole.maestro,
        is_admin=False,
        is_active=True,
    )
    auth_db.add(user)
    auth_db.commit()

    def override_get_db():
        yield auth_db

    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        unauthenticated = client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "old-password", "new_password": "new-password-123"},
        )
        assert unauthenticated.status_code == 401

        token = create_access_token("maestro@example.com")
        response = client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "old-password", "new_password": "new-password-123"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204

        old_login = client.post(
            "/api/v1/auth/login",
            json={"email": "maestro@example.com", "password": "old-password"},
        )
        assert old_login.status_code == 401

        new_login = client.post(
            "/api/v1/auth/login",
            json={"email": "maestro@example.com", "password": "new-password-123"},
        )
        assert new_login.status_code == 200

    app.dependency_overrides.clear()
