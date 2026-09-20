"""Production routes — waste analysis."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.application.dto.analytics import DateRange, SalesFilters
from app.infrastructure.repositories.implementations import ProductionRepository
from app.presentation.api.dependencies import get_production_repo
from app.presentation.api.schemas.schemas import ProductionWasteResponse

router = APIRouter()


def _build_filters(start_date, end_date, product_id, category, channel_id) -> SalesFilters | None:
    dr = None
    if start_date and end_date:
        from datetime import date as date_type
        dr = DateRange(start_date=date_type.fromisoformat(start_date), end_date=date_type.fromisoformat(end_date))
    if not any([dr, product_id, category, channel_id]):
        return None
    return SalesFilters(date_range=dr, product_id=product_id, category=category, channel_id=channel_id)


@router.get("/waste", response_model=list[ProductionWasteResponse])
def get_waste(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    product_id: int | None = Query(None),
    category: str | None = Query(None),
    channel_id: int | None = Query(None),
    production_repo: ProductionRepository = Depends(get_production_repo),
):
    filters = _build_filters(start_date, end_date, product_id, category, channel_id)
    data = production_repo.get_waste_by_product(filters)
    return [
        ProductionWasteResponse(
            product_id=w.product_id,
            product_name=w.product_name,
            produced=w.produced,
            sold=w.sold,
            discarded=w.discarded,
            waste_rate=w.waste_rate,
        )
        for w in data
    ]
