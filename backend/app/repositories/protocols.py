from typing import Protocol, runtime_checkable
from uuid import UUID

from app.entities.file import File
from app.entities.folder import Folder


@runtime_checkable
class FileSystemRepositoryProtocol(Protocol):
    async def add_folder(self, folder: Folder) -> None: ...

    async def add_file(self, file: File) -> None: ...

    async def get_folder(self, folder_id: UUID) -> Folder | None: ...

    async def delete_file(self, file_id: UUID) -> None: ...

    async def delete_folder(self, folder_id: UUID) -> None: ...
