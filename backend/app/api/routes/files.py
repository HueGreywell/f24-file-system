from fastapi import APIRouter, Depends, Response

from app.api.deps import get_service, parse_path_uuid
from app.services.filesystem_service import FileSystemService

router = APIRouter(prefix="/files", tags=["files"])


@router.delete("/{id}", status_code=204)
async def delete_file(
    id: str, service: FileSystemService = Depends(get_service)
) -> Response:
    await service.delete_file(parse_path_uuid(id))
    return Response(status_code=204)
