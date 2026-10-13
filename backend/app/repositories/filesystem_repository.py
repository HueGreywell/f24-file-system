from uuid import UUID

import asyncpg

from app.entities.file import File
from app.entities.folder import Folder
from app.repositories.protocols import FileSystemRepositoryProtocol
from app.services.exceptions import EntryNotFoundException


class FileSystemRepository(FileSystemRepositoryProtocol):
    def __init__(self, connection: asyncpg.pool.PoolConnectionProxy) -> None:
        self._connection = connection

    async def add_folder(self, folder: Folder) -> None:
        await self._connection.execute(
            "INSERT INTO folders (id, parent_id, name) VALUES ($1, $2, $3)",
            folder.id,
            folder.parent_id,
            folder.name,
        )

    async def add_file(self, file: File) -> None:
        await self._connection.execute(
            "INSERT INTO files (id, parent_id, name) VALUES ($1, $2, $3)",
            file.id,
            file.parent_id,
            file.name,
        )

    async def get_folder(self, folder_id: UUID) -> Folder | None:
        row = await self._connection.fetchrow(
            "SELECT id, parent_id, name FROM folders WHERE id = $1", folder_id
        )
        if row is None:
            return None
        return Folder(id=row["id"], parent_id=row["parent_id"], name=row["name"])

    async def delete_folder(self, folder_id: UUID) -> None:
        await self._connection.execute("DELETE FROM folders WHERE id = $1", folder_id)

    async def delete_file(self, file_id: UUID) -> None:
        result = await self._connection.execute("DELETE FROM files WHERE id = $1", file_id)
        if result == "DELETE 0":
            raise EntryNotFoundException("File not found.")

