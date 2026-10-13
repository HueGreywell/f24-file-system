from uuid import UUID

import asyncpg

from app.entities.file import File
from app.entities.folder import Folder
from app.repositories.protocols import FileSystemRepositoryProtocol
from app.schemas.entry import EntryDto
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
        result = await self._connection.execute(
            "DELETE FROM files WHERE id = $1", file_id
        )

        if result == "DELETE 0":
            raise EntryNotFoundException("File not found.")

    async def get_folder_path(self, folder_id: UUID) -> str:
        return await self._connection.fetchval(_GET_FOLDER_PATH_SQL, folder_id)

    async def get_children(self, folder_id: UUID) -> list[EntryDto]:
        rows = await self._connection.fetch(_GET_CHILDREN_SQL, folder_id)
        return [
            EntryDto(id=row["id"], name=row["name"], type=row["type"]) for row in rows
        ]


_GET_FOLDER_PATH_SQL = """
    WITH RECURSIVE ancestors AS (
        SELECT id, parent_id, name, 0 AS depth FROM folders WHERE id = $1
        UNION ALL
        SELECT parent.id, parent.parent_id, parent.name, child.depth + 1
        FROM folders parent JOIN ancestors child ON child.parent_id = parent.id
    )
    SELECT CASE WHEN length(string_agg(name, '/' ORDER BY depth DESC)) <= 255
                THEN string_agg(name, '/' ORDER BY depth DESC)
                ELSE '...' || right(string_agg(name, '/' ORDER BY depth DESC), 252)
           END AS value
    FROM ancestors
"""

_GET_CHILDREN_SQL = """
    SELECT id, name, 'folder' AS type, 0 AS sort_order, lower(name) COLLATE "C" AS sort_name
    FROM folders WHERE parent_id = $1
    UNION ALL
    SELECT id, name, 'file' AS type, 1 AS sort_order, lower(name) COLLATE "C" AS sort_name
    FROM files WHERE parent_id = $1
    ORDER BY sort_order, sort_name, id
"""
