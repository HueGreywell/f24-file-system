from dataclasses import dataclass
from uuid import UUID


@dataclass
class Folder:
    id: UUID 
    name: str
    parent_id: UUID | None = None
