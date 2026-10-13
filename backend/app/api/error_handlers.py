import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.error import ErrorDto
from app.services.exceptions import DomainException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainException)
    async def domain_exception_handler(
        _: Request, exc: DomainException
    ) -> JSONResponse:
        error = ErrorDto(code=exc.code, message=exc.message)
        return JSONResponse(status_code=exc.status_code, content=error.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        error = ErrorDto(code="VALIDATION_ERROR", message=str(exc))
        return JSONResponse(status_code=422, content=error.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error", exc_info=exc)
        error = ErrorDto(code="INTERNAL_ERROR", message="Internal server error.")
        return JSONResponse(status_code=500, content=error.model_dump())
