"""Centralized exception handlers."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions.errors import (
    DomainError,
    DuplicateImportError,
    InvalidSaleStatusError,
    NegativeValueError,
)

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(DuplicateImportError)
    async def duplicate_handler(request: Request, exc: DuplicateImportError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(InvalidSaleStatusError)
    async def status_handler(request: Request, exc: InvalidSaleStatusError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(NegativeValueError)
    async def negative_handler(request: Request, exc: NegativeValueError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(DomainError)
    async def domain_handler(request: Request, exc: DomainError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def value_handler(request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception")
        return JSONResponse(status_code=500, content={"detail": "Erro interno do servidor."})
