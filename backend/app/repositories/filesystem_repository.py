from uuid import UUID

import asyncpg

from app.entities.exceptions import DuplicateNameException, EntryNotFoundException
from app.entities.file import File
from app.entities.folder import Folder
from app.entities.search_match import SearchMatch
from app.repositories.protocols import FileSystemRepositoryProtocol


class FileSystemRepository(FileSystemRepositoryProtocol):
    def __init__(self, connection: asyncpg.pool.PoolConnectionProxy) -> None:
        self._connection = connection

    async def add_folder(self, folder: Folder) -> None:
        await self._insert_entry(
            "INSERT INTO folders (id, parent_id, name) VALUES ($1, $2, $3)",
            folder.id,
            folder.parent_id,
            folder.name,
        )

    async def add_file(self, file: File) -> None:
        await self._insert_entry(
            "INSERT INTO files (id, parent_id, name) VALUES ($1, $2, $3)",
            file.id,
            file.parent_id,
            file.name,
        )

    async def _insert_entry(self, query: str, *args: object) -> None:
        try:
            await self._connection.execute(query, *args)
        except asyncpg.UniqueViolationError as error:
            raise DuplicateNameException(
                "An entry with this name already exists in the folder."
            ) from error
        except asyncpg.ForeignKeyViolationError as error:
            raise EntryNotFoundException("Parent folder not found.") from error

    async def get_folder(self, folder_id: UUID) -> Folder | None:
        row = await self._connection.fetchrow(
            "SELECT id, parent_id, name FROM folders WHERE id = $1", folder_id
        )
        if row is None:
            return None
        return Folder(id=row["id"], parent_id=row["parent_id"], name=row["name"])

    async def get_root_folder(self) -> Folder | None:
        row = await self._connection.fetchrow(
            "SELECT id, parent_id, name FROM folders WHERE parent_id IS NULL"
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

    async def get_children(self, folder_id: UUID) -> list[Folder | File]:
        rows = await self._connection.fetch(_GET_CHILDREN_SQL, folder_id)
        return [
            Folder(id=row["id"], parent_id=folder_id, name=row["name"])
            if row["type"] == "Folder"
            else File(id=row["id"], parent_id=folder_id, name=row["name"])
            for row in rows
        ]

    async def search_prefix_in_folder(
        self, query: str, folder_id: UUID, limit: int
    ) -> list[SearchMatch]:
        rows = await self._connection.fetch(
            _SEARCH_PREFIX_IN_FOLDER_SQL, folder_id, self._like_prefix(query), limit
        )

        return [self._to_search_match(row) for row in rows]

    async def search_all_files(self, query: str, limit: int) -> list[SearchMatch]:
        rows = await self._connection.fetch(
            _SEARCH_ALL_FILES_SQL, self._like_prefix(query), limit
        )

        return [self._to_search_match(row) for row in rows]

    @staticmethod
    def _like_prefix(query: str) -> str:
        escaped = (query.lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_"))
        return f"{escaped}%"

    @staticmethod
    def _to_search_match(row: asyncpg.Record) -> SearchMatch:
        return SearchMatch(
            file=File(id=row["id"], name=row["name"], parent_id=row["parent_id"]),
            path=row["path"],
        )


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
    SELECT id, name, 'Folder' AS type, 0 AS sort_order, lower(name) COLLATE "C" AS sort_name
    FROM folders WHERE parent_id = $1
    UNION ALL
    SELECT id, name, 'File' AS type, 1 AS sort_order, lower(name) COLLATE "C" AS sort_name
    FROM files WHERE parent_id = $1
    ORDER BY sort_order, sort_name, id
"""

_SEARCH_COMMON_SQL = """
    ancestors AS (
        SELECT match.id AS file_id, folder.id, folder.parent_id, folder.name, 0 AS depth
        FROM matches match JOIN folders folder ON folder.id = match.parent_id
        UNION ALL
        SELECT child.file_id, parent.id, parent.parent_id, parent.name, child.depth + 1
        FROM ancestors child JOIN folders parent ON parent.id = child.parent_id
    ),
    result_paths AS (
        SELECT file_id, string_agg(name, '/' ORDER BY depth DESC) AS path
        FROM ancestors
        GROUP BY file_id
    )
    SELECT match.id AS id, match.name AS name,
           CASE WHEN length(path.path || '/' || match.name) <= 255
                THEN path.path || '/' || match.name
                ELSE '...' || right(path.path || '/' || match.name, 252)
           END AS path,
           match.parent_id AS parent_id
    FROM matches match JOIN result_paths path ON path.file_id = match.id
    ORDER BY LOWER(match.name) COLLATE "C", match.name COLLATE "C", match.id
"""

_SEARCH_ALL_FILES_SQL = f"""
    WITH RECURSIVE matches AS MATERIALIZED (
        SELECT id, name, parent_id
        FROM files
        WHERE LOWER(name) COLLATE "C" LIKE $1 ESCAPE '\\'
        ORDER BY LOWER(name) COLLATE "C", name COLLATE "C", id
        LIMIT $2
    ),
    {_SEARCH_COMMON_SQL}
"""

_SEARCH_PREFIX_IN_FOLDER_SQL = f"""
    WITH RECURSIVE matches AS MATERIALIZED (
        SELECT id, name, parent_id
        FROM files
        WHERE parent_id = $1 AND LOWER(name) COLLATE "C" LIKE $2 ESCAPE '\\'
        ORDER BY LOWER(name) COLLATE "C", name COLLATE "C", id
        LIMIT $3
    ),
    {_SEARCH_COMMON_SQL}
"""
