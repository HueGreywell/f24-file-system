from collections.abc import AsyncIterator

from fastapi import Depends

from app.db.db import get_pool
from app.repositores.filesystem_repository import FileSystemRepository
from app.repositores.protocols import FileSystemRepositoryProtocol
from app.services.filesystem_service import FileSystemService


async def get_repository() -> AsyncIterator[FileSystemRepositoryProtocol]:
    pool = get_pool()
    async with pool.acquire() as connection:
        yield FileSystemRepository(connection)


async def get_service(
    repository: FileSystemRepository = Depends(get_repository),
) -> FileSystemService:
    return FileSystemService(repository)

