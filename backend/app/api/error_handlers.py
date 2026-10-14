import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.entities.exceptions import (
    CannotDeleteRootException,
    DomainException,
    DuplicateNameException,
    EntryNotFoundException,
    InvalidNameException,
)
from app.schemas.error import ErrorDto

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    def respond(exc: DomainException, status_code: int) -> JSONResponse:
        error = ErrorDto(code=exc.code, message=exc.message)
        return JSONResponse(status_code=status_code, content=error.model_dump())

    @app.exception_handler(InvalidNameException)
    async def invalid_name_handler(_: Request, exc: InvalidNameException) -> JSONResponse:
        return respond(exc, 400)

    @app.exception_handler(EntryNotFoundException)
    async def entry_not_found_handler(_: Request, exc: EntryNotFoundException) -> JSONResponse:
        return respond(exc, 404)

    @app.exception_handler(CannotDeleteRootException)
    async def cannot_delete_root_handler(
        _: Request, exc: CannotDeleteRootException
    ) -> JSONResponse:
        return respond(exc, 400)

    @app.exception_handler(DuplicateNameException)
    async def duplicate_name_handler(_: Request, exc: DuplicateNameException) -> JSONResponse:
        return respond(exc, 409)

    @app.exception_handler(DomainException)
    async def domain_exception_handler(_: Request, exc: DomainException) -> JSONResponse:
        return respond(exc, 400)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        first_error = exc.errors()[0]
        message = f"{first_error['loc'][-1]}: {first_error['msg']}"
        error = ErrorDto(code="VALIDATION_ERROR", message=message)
        return JSONResponse(status_code=422, content=error.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error", exc_info=exc)
        error = ErrorDto(code="INTERNAL_ERROR", message="Internal server error.")
        return JSONResponse(status_code=500, content=error.model_dump())
