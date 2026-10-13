from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.entities.enums import EntryType


class CreateEntryRequest(BaseModel):
    name: str
    type: EntryType

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, value: object) -> object:
        if isinstance(value, str):
            for member in EntryType:
                if member.value.lower() == value.lower():
                    return member
        return value


class EntryDto(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    type: str


class FolderContentsDto(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    parent_id: UUID | None = Field(serialization_alias="parentId")
    path: str
    children: list[EntryDto]


class SearchResultDto(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    path: str
    parent_id: UUID = Field(serialization_alias="parentId")
