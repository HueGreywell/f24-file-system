from typing import Protocol, runtime_checkable
from uuid import UUID

from app.entities.file import File
from app.entities.folder import Folder
from app.schemas.entry import EntryDto, SearchResultDto


@runtime_checkable
class FileSystemRepositoryProtocol(Protocol):
    async def add_folder(self, folder: Folder) -> None: ...

    async def add_file(self, file: File) -> None: ...

    async def get_folder(self, folder_id: UUID) -> Folder | None: ...

    async def delete_file(self, file_id: UUID) -> None: ...

    async def delete_folder(self, folder_id: UUID) -> None: ...

    async def get_folder_path(self, folder_id: UUID) -> str: ...

    async def get_children(self, folder_id: UUID) -> list[EntryDto]: ...

    async def search_exact_in_folder(
        self, query: str, folder_id: UUID, limit: int
    ) -> list[SearchResultDto]: ...

    async def search_all_files(self, query: str, limit: int) -> list[SearchResultDto]: ...

