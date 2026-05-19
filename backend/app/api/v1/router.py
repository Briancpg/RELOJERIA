from fastapi import APIRouter

from app.api.v1 import auth, dashboard, repairs

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(repairs.router)
api_router.include_router(dashboard.router)

