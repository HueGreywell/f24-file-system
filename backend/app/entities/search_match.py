from dataclasses import dataclass

from app.entities.file import File


@dataclass
class SearchMatch:
    file: File
    path: str
