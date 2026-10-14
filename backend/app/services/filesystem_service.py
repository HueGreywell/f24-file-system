from uuid import UUID, uuid4

from app.entities.enums import EntryType
from app.entities.exceptions import CannotDeleteRootException, EntryNotFoundException
from app.entities.file import File
from app.entities.folder import Folder
from app.entities.folder_contents import FolderContents
from app.entities.search_match import SearchMatch
from app.repositories.protocols import FileSystemRepositoryProtocol
from app.services import name_validator

SEARCH_RESULT_LIMIT = 10


class FileSystemService:
    def __init__(self, repository: FileSystemRepositoryProtocol) -> None:
        self._repository = repository

    async def create(self, parent_id: UUID, name: str, entry_type: EntryType) -> Folder | File:
        name = name_validator.normalize(name)

        if await self._repository.get_folder(parent_id) is None:
            raise EntryNotFoundException("Parent folder not found.")

        if entry_type == EntryType.FOLDER:
            folder = Folder(id=uuid4(), parent_id=parent_id, name=name)
            await self._repository.add_folder(folder)
            return folder

        file = File(id=uuid4(), parent_id=parent_id, name=name)
        await self._repository.add_file(file)
        return file

    async def delete_file(self, file_id: UUID) -> None:
        await self._repository.delete_file(file_id)

    async def delete_folder(self, folder_id: UUID) -> None:
        folder = await self._repository.get_folder(folder_id)
        if folder is None:
            raise EntryNotFoundException("Folder not found.")
        if folder.parent_id is None:
            raise CannotDeleteRootException("The root folder cannot be deleted.")

        await self._repository.delete_folder(folder_id)

    async def get_folder(self, folder_id: UUID) -> FolderContents:
        folder = await self._repository.get_folder(folder_id)
        if folder is None:
            raise EntryNotFoundException("Folder not found.")
        return await self._build_folder_contents(folder)

    async def get_root(self) -> FolderContents:
        folder = await self._repository.get_root_folder()
        if folder is None:
            raise EntryNotFoundException("Root folder not found.")
        return await self._build_folder_contents(folder)

    async def _build_folder_contents(self, folder: Folder) -> FolderContents:
        path = await self._repository.get_folder_path(folder.id)
        children = await self._repository.get_children(folder.id)
        return FolderContents(folder=folder, path=path, children=children)

    async def search(self, query: str, folder_id: UUID | None) -> list[SearchMatch]:
        query = query.strip()
        if not query:
            return []

        if folder_id is not None:
            if await self._repository.get_folder(folder_id) is None:
                raise EntryNotFoundException("Folder not found.")
            return await self._repository.search_exact_in_folder(
                query, folder_id, SEARCH_RESULT_LIMIT
            )

        return await self._repository.search_all_files(query, SEARCH_RESULT_LIMIT)
