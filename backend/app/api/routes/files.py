from fastapi import APIRouter, Depends

from app.api.deps import get_service, parse_path_uuid
from app.schemas.entry import CreateEntryRequest, EntryDto
from app.services.filesystem_service import FileSystemService

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/{id}", response_model=EntryDto, status_code=201)
async def create_entry(
    id: str,
    request: CreateEntryRequest,
    service: FileSystemService = Depends(get_service),
) -> EntryDto:
    return await service.create(parse_path_uuid(id), request)
