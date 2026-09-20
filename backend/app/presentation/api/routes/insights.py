"""Insights routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.application.dto.analytics import DateRange, SalesFilters
from app.application.use_cases.insights_engine import generate_insights
from app.infrastructure.repositories.implementations import (
    ProductionRepository,
    ProductRepository,
    SalesRepository,
)
from app.presentation.api.dependencies import get_product_repo, get_production_repo, get_sales_repo
from app.presentation.api.schemas.schemas import InsightResponse

router = APIRouter()


def _build_filters(start_date, end_date, product_id, category, channel_id) -> SalesFilters | None:
    dr = None
    if start_date and end_date:
        from datetime import date as date_type
        dr = DateRange(start_date=date_type.fromisoformat(start_date), end_date=date_type.fromisoformat(end_date))
    if not any([dr, product_id, category, channel_id]):
        return None
    return SalesFilters(date_range=dr, product_id=product_id, category=category, channel_id=channel_id)


@router.get("", response_model=list[InsightResponse])
def get_insights(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    product_id: int | None = Query(None),
    category: str | None = Query(None),
    channel_id: int | None = Query(None),
    sales_repo: SalesRepository = Depends(get_sales_repo),
    product_repo: ProductRepository = Depends(get_product_repo),
    production_repo: ProductionRepository = Depends(get_production_repo),
):
    filters = _build_filters(start_date, end_date, product_id, category, channel_id)
    insights = generate_insights(sales_repo, product_repo, production_repo, filters)
    return [
        InsightResponse(
            title=i.title,
            description=i.description,
            evidence=i.evidence,
            recommendation=i.recommendation,
            level=i.level.value,
            metric_value=i.metric_value,
        )
        for i in insights
    ]
