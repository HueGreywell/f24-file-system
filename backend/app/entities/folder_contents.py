from dataclasses import dataclass

from app.entities.file import File
from app.entities.folder import Folder


@dataclass
class FolderContents:
    folder: Folder
    path: str
    children: list[Folder | File]
