from fastapi import APIRouter

from app.api.routes.files import router as files_router
from app.api.routes.folders import router as folder_router

api_router = APIRouter()
api_router.include_router(folder_router)
api_router.include_router(files_router)
