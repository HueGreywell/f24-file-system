from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.db.db import connect, disconnect


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect()
    yield
    await disconnect()


app = FastAPI(title="File System API", lifespan=lifespan)
app.include_router(api_router)
