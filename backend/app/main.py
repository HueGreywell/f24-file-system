from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(title="File System API")
app.include_router(api_router)


