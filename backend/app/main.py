from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.services.auth_service import AuthService


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    db = SessionLocal()
    try:
        AuthService(db).ensure_admin_seed()
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health():
    return {"status": "ok"}

