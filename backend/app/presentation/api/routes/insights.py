"""Insights routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.application.use_cases.insights_engine import generate_insights
from app.infrastructure.repositories.implementations import (
    ProductionRepository,
    ProductRepository,
    SalesRepository,
)
from app.presentation.api.dependencies import get_product_repo, get_production_repo, get_sales_repo, parse_filters
from app.presentation.api.schemas.schemas import InsightResponse

router = APIRouter()


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
    filters = parse_filters(start_date, end_date, product_id, category, channel_id)
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
