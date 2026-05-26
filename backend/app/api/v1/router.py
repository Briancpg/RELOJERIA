from fastapi import APIRouter

from app.api.v1 import auth, clients, dashboard, inventory, repairs, reports

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(repairs.router)
api_router.include_router(clients.router)
api_router.include_router(inventory.router)
api_router.include_router(reports.router)
api_router.include_router(dashboard.router)
