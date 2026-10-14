from fastapi import APIRouter, Depends, Query, Response

from app.api.deps import get_service, parse_path_uuid
from app.api.mappers import to_search_result_dto
from app.schemas.entry import SearchResultDto
from app.services.filesystem_service import FileSystemService

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/search", response_model=list[SearchResultDto])
async def search_files(
    query: str,
    folder_id: str | None = Query(default=None, alias="folderId"),
    service: FileSystemService = Depends(get_service),
) -> list[SearchResultDto]:
    parsed_folder_id = parse_path_uuid(folder_id) if folder_id is not None else None
    matches = await service.search(query, parsed_folder_id)
    return [to_search_result_dto(match) for match in matches]


@router.delete("/{id}", status_code=204)
async def delete_file(
    id: str, service: FileSystemService = Depends(get_service)
) -> Response:
    await service.delete_file(parse_path_uuid(id))
    return Response(status_code=204)
