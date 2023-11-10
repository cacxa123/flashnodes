from fastapi import APIRouter

from app.api.api_v1.endpoints import admin, analytics, login, projects, users, utils

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["Login"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(utils.router, prefix="/utils", tags=["Utils"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
