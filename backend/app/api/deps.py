from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import Depends

from app.db.db import get_pool
from app.entities.exceptions import EntryNotFoundException
from app.repositories.filesystem_repository import FileSystemRepository
from app.repositories.protocols import FileSystemRepositoryProtocol
from app.services.filesystem_service import FileSystemService


async def get_repository() -> AsyncIterator[FileSystemRepositoryProtocol]:
    pool = get_pool()
    async with pool.acquire() as connection:
        yield FileSystemRepository(connection)


async def get_service(
    repository: FileSystemRepositoryProtocol = Depends(get_repository),
) -> FileSystemService:
    return FileSystemService(repository)


def parse_path_uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as error:
        raise EntryNotFoundException("Entry not found.") from error
