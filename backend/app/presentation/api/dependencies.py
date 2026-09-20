"""FastAPI dependency injection."""
from __future__ import annotations

from fastapi import Depends, Query
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


def parse_filters(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    product_id: int | None = Query(None),
    category: str | None = Query(None),
    channel_id: int | None = Query(None),
) -> SalesFilters | None:
    from datetime import date as date_type
    dr = None
    if start_date and end_date:
        dr = DateRange(
            start_date=date_type.fromisoformat(start_date),
            end_date=date_type.fromisoformat(end_date),
        )
    if not any([dr, product_id, category, channel_id]):
        return None
    return SalesFilters(date_range=dr, product_id=product_id, category=category, channel_id=channel_id)
