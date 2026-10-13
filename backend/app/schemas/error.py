from pydantic import BaseModel


class ErrorDto(BaseModel):
    code: str
    message: str
