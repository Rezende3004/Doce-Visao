"""FastAPI dependency injection."""

from __future__ import annotations

from datetime import date as date_type
from typing import Literal

from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.application.dto.analytics import DateRange, SalesFilters
from app.infrastructure.database.connection import get_session
from app.infrastructure.repositories.implementations import (
    DimensionRepository,
    ImportRepository,
    ProductionRepository,
    ProductRepository,
    SalesRepository,
)


def get_db() -> Session:
    session = get_session()
    try:
        yield session
    finally:
        session.close()


def get_sales_repo(session: Session = Depends(get_db)) -> SalesRepository:
    return SalesRepository(session)


def get_product_repo(session: Session = Depends(get_db)) -> ProductRepository:
    return ProductRepository(session)


def get_production_repo(session: Session = Depends(get_db)) -> ProductionRepository:
    return ProductionRepository(session)


def get_import_repo(session: Session = Depends(get_db)) -> ImportRepository:
    return ImportRepository(session)


def get_dim_repo(session: Session = Depends(get_db)) -> DimensionRepository:
    return DimensionRepository(session)


VALID_SORT_BY_VALUES: set[str] = {"quantity", "revenue"}


def parse_filters(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    product_id: int | None = Query(None),
    category: str | None = Query(None),
    channel_id: int | None = Query(None),
) -> SalesFilters | None:
    """Parse and validate filter parameters shared across all endpoints.

    Raises 422 if dates are invalid or start_date > end_date.
    Returns None when no filters are specified.
    """
    dr = None
    if (start_date is None) != (end_date is None):
        raise HTTPException(status_code=422, detail="Informe start_date e end_date juntos.")
    if start_date is not None and end_date is not None:
        try:
            sd = date_type.fromisoformat(start_date)
            ed = date_type.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(status_code=422, detail="Formato de data inválido. Use YYYY-MM-DD.")
        if sd > ed:
            raise HTTPException(status_code=422, detail="data_inicial não pode ser posterior a data_final.")
        dr = DateRange(start_date=sd, end_date=ed)
    if not any([dr, product_id, category, channel_id]):
        return None
    return SalesFilters(date_range=dr, product_id=product_id, category=category, channel_id=channel_id)


def parse_sort_by(
    sort_by: str = Query("quantity", pattern=r"^(quantity|revenue)$"),
) -> Literal["quantity", "revenue"]:
    """Validate and normalize sort_by parameter."""
    if sort_by not in VALID_SORT_BY_VALUES:
        raise HTTPException(status_code=422, detail=f"sort_by deve ser um de: {', '.join(sorted(VALID_SORT_BY_VALUES))}")
    return sort_by  # type: ignore[return-value]
