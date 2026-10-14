from app.entities.enums import EntryType
from app.entities.file import File
from app.entities.folder import Folder
from app.entities.folder_contents import FolderContents
from app.entities.search_match import SearchMatch
from app.schemas.entry import EntryDto, FolderContentsDto, SearchResultDto


def to_entry_dto(entry: Folder | File) -> EntryDto:
    entry_type = EntryType.FOLDER if isinstance(entry, Folder) else EntryType.FILE
    return EntryDto(id=entry.id, name=entry.name, type=entry_type.value)


def to_folder_contents_dto(contents: FolderContents) -> FolderContentsDto:
    return FolderContentsDto(
        id=contents.folder.id,
        name=contents.folder.name,
        parent_id=contents.folder.parent_id,
        path=contents.path,
        children=[to_entry_dto(child) for child in contents.children],
    )


def to_search_result_dto(match: SearchMatch) -> SearchResultDto:
    return SearchResultDto(
        id=match.file.id,
        name=match.file.name,
        path=match.path,
        parent_id=match.file.parent_id,
    )
