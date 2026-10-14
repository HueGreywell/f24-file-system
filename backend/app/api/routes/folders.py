from fastapi import APIRouter, Depends, Response

from app.api.deps import get_service, parse_path_uuid
from app.api.mappers import to_entry_dto, to_folder_contents_dto
from app.schemas.entry import CreateEntryRequest, EntryDto, FolderContentsDto
from app.services.filesystem_service import FileSystemService

router = APIRouter(prefix="/folders", tags=["Folders"])


@router.post("/{id}", response_model=EntryDto, status_code=201)
async def create_entry(
    id: str,
    request: CreateEntryRequest,
    service: FileSystemService = Depends(get_service),
) -> EntryDto:
    entry = await service.create(parse_path_uuid(id), request)
    return to_entry_dto(entry)


@router.delete("/{id}", status_code=204)
async def delete_folder(
    id: str, service: FileSystemService = Depends(get_service)
) -> Response:
    await service.delete_folder(parse_path_uuid(id))
    return Response(status_code=204)


@router.get("/{id}", response_model=FolderContentsDto)
async def get_folder(
    id: str, service: FileSystemService = Depends(get_service)
) -> FolderContentsDto:
    contents = await service.get_folder(parse_path_uuid(id))
    return to_folder_contents_dto(contents)


@router.get("", response_model=FolderContentsDto)
async def get_root_folder(
    service: FileSystemService = Depends(get_service),
) -> FolderContentsDto:
    contents = await service.get_root()
    return to_folder_contents_dto(contents)
