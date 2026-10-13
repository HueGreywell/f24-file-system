from dataclasses import dataclass
from uuid import UUID


@dataclass
class File:
    id: UUID
    name: str
    parent_id: UUID 
