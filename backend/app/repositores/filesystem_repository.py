import asyncpg

from app.repositores.protocols import FileSystemRepositoryProtocol


class FileSystemRepository(FileSystemRepositoryProtocol):
    def __init__(self, connection: asyncpg.pool.PoolConnectionProxy) -> None:
        self._connection = connection
