from uuid import UUID

from app.entities.file import File
from app.entities.folder import Folder
from app.schemas.entry import EntryDto, SearchResultDto
from app.services.exceptions import DuplicateNameException, EntryNotFoundException


class FakeRepository:
    """In-memory stand-in for FileSystemRepositoryProtocol, used to unit-test
    the service layer without a database."""

    def __init__(self) -> None:
        self.folders: dict[UUID, Folder] = {}
        self.files: dict[UUID, File] = {}

    def _siblings_have_name(self, parent_id: UUID | None, name: str) -> bool:
        lowered = name.lower()
        return any(
            f.parent_id == parent_id and f.name.lower() == lowered
            for f in self.files.values()
        ) or any(
            f.parent_id == parent_id and f.name.lower() == lowered
            for f in self.folders.values()
        )

    async def add_folder(self, folder: Folder) -> None:
        if self._siblings_have_name(folder.parent_id, folder.name):
            raise DuplicateNameException(
                "An entry with this name already exists in the folder."
            )
        self.folders[folder.id] = folder

    async def add_file(self, file: File) -> None:
        if self._siblings_have_name(file.parent_id, file.name):
            raise DuplicateNameException(
                "An entry with this name already exists in the folder."
            )
        self.files[file.id] = file

    async def get_folder(self, folder_id: UUID) -> Folder | None:
        return self.folders.get(folder_id)

    async def get_root_folder(self) -> Folder | None:
        for folder in self.folders.values():
            if folder.parent_id is None:
                return folder
        return None

    async def delete_file(self, file_id: UUID) -> None:
        if file_id not in self.files:
            raise EntryNotFoundException("File not found.")
        del self.files[file_id]

    async def delete_folder(self, folder_id: UUID) -> None:
        to_delete = [folder_id]
        while to_delete:
            current = to_delete.pop()
            self.folders.pop(current, None)
            self.files = {
                fid: f for fid, f in self.files.items() if f.parent_id != current
            }
            to_delete.extend(
                fid for fid, f in self.folders.items() if f.parent_id == current
            )

    async def get_folder_path(self, folder_id: UUID) -> str:
        parts = []
        current: UUID | None = folder_id
        while current is not None:
            folder = self.folders[current]
            parts.append(folder.name)
            current = folder.parent_id
        return "/".join(reversed(parts))

    async def get_children(self, folder_id: UUID) -> list[EntryDto]:
        folders = sorted(
            (f for f in self.folders.values() if f.parent_id == folder_id),
            key=lambda f: f.name.lower(),
        )
        files = sorted(
            (f for f in self.files.values() if f.parent_id == folder_id),
            key=lambda f: f.name.lower(),
        )
        return [EntryDto(id=f.id, name=f.name, type="Folder") for f in folders] + [
            EntryDto(id=f.id, name=f.name, type="File") for f in files
        ]

    async def _to_search_result(self, file: File) -> SearchResultDto:
        path = await self.get_folder_path(file.parent_id)
        return SearchResultDto(
            id=file.id,
            name=file.name,
            path=f"{path}/{file.name}",
            parent_id=file.parent_id,
        )

    async def search_exact_in_folder(
        self, query: str, folder_id: UUID, limit: int
    ) -> list[SearchResultDto]:
        matches = [
            f
            for f in self.files.values()
            if f.parent_id == folder_id and f.name.lower() == query.lower()
        ]
        matches.sort(key=lambda f: f.name.lower())
        return [await self._to_search_result(f) for f in matches[:limit]]

    async def search_all_files(self, query: str, limit: int) -> list[SearchResultDto]:
        lowered = query.lower()
        matches = [f for f in self.files.values() if f.name.lower().startswith(lowered)]
        matches.sort(key=lambda f: f.name.lower())
        return [await self._to_search_result(f) for f in matches[:limit]]
