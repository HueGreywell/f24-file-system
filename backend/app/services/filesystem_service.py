from uuid import UUID, uuid4

from app.entities.enums import EntryType
from app.entities.file import File
from app.entities.folder import Folder
from app.repositories.protocols import FileSystemRepositoryProtocol
from app.schemas.entry import CreateEntryRequest, EntryDto
from app.services import name_validator
from app.services.exceptions import *


class FileSystemService:
    def __init__(self, repository: FileSystemRepositoryProtocol) -> None:
        self._repository = repository

    async def create(self, parent_id: UUID, request: CreateEntryRequest) -> EntryDto:
        name = name_validator.normalize(request.name)

        if await self._repository.get_folder(parent_id) is None:
            raise EntryNotFoundException("Parent folder not found.")

        if request.type == EntryType.FOLDER:
            folder = Folder(id=uuid4(), parent_id=parent_id, name=name)
            await self._repository.add_folder(folder)
            return EntryDto(id=folder.id, name=folder.name, type="folder")

        file = File(id=uuid4(), parent_id=parent_id, name=name)
        await self._repository.add_file(file)
        return EntryDto(id=file.id, name=file.name, type="file")

    async def delete_file(self, file_id: UUID) -> None:
        await self._repository.delete_file(file_id)

    async def delete_folder(self, folder_id: UUID) -> None:
        folder = await self._repository.get_folder(folder_id)
        if folder is None:
            raise EntryNotFoundException("Folder not found.")
        if folder.parent_id is None:
            raise CannotDeleteRootException("The root folder cannot be deleted.")

        await self._repository.delete_folder(folder_id)
