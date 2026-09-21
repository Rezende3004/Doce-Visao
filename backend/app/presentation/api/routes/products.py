"""Product routes — ranking, category performance, margin, filters."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.infrastructure.repositories.implementations import DimensionRepository, ProductRepository
from app.presentation.api.dependencies import get_dim_repo, get_product_repo, parse_filters
from app.presentation.api.schemas.schemas import (
    CategoryPerformanceResponse,
    FilterOptionsResponse,
    MarginResponse,
    ProductRankingResponse,
)

router = APIRouter()


def _fmt(cents: int) -> str:
    return f"R$ {cents / 100:.2f}".replace(".", ",")


@router.get("/ranking", response_model=list[ProductRankingResponse])
def get_ranking(
    sort_by: str = Query("quantity", pattern="^(quantity|revenue)$"),
    limit: int = Query(20, ge=1, le=100),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    product_id: int | None = Query(None),
    category: str | None = Query(None),
    channel_id: int | None = Query(None),
    product_repo: ProductRepository = Depends(get_product_repo),
):
    filters = parse_filters(start_date, end_date, product_id, category, channel_id)
    if sort_by == "revenue":
        data = product_repo.get_ranking_by_revenue(filters, limit)
    else:
        data = product_repo.get_ranking_by_quantity(filters, limit)
    return [
        ProductRankingResponse(
            product_id=p.product_id,
            product_name=p.product_name,
            category=p.category,
            quantity=p.quantity,
            faturamento=_fmt(p.faturamento_cents),
            faturamento_cents=p.faturamento_cents,
        )
        for p in data
    ]


@router.get("/categories/performance", response_model=list[CategoryPerformanceResponse])
def get_category_performance(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    product_id: int | None = Query(None),
    category: str | None = Query(None),
    channel_id: int | None = Query(None),
    product_repo: ProductRepository = Depends(get_product_repo),
):
    filters = parse_filters(start_date, end_date, product_id, category, channel_id)
    data = product_repo.get_category_performance(filters)
    return [
        CategoryPerformanceResponse(
            category=c.category,
            quantity=c.quantity,
            faturamento=_fmt(c.faturamento_cents),
            faturamento_cents=c.faturamento_cents,
            share_percentual=c.share_percentual,
        )
        for c in data
    ]


@router.get("/margin", response_model=MarginResponse)
def get_margin(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    product_id: int | None = Query(None),
    category: str | None = Query(None),
    channel_id: int | None = Query(None),
    product_repo: ProductRepository = Depends(get_product_repo),
):
    filters = parse_filters(start_date, end_date, product_id, category, channel_id)
    m = product_repo.get_margin_info(filters)
    return MarginResponse(
        faturamento=_fmt(m.faturamento_cents),
        faturamento_cents=m.faturamento_cents,
        custo_total=_fmt(m.custo_total_cents),
        custo_total_cents=m.custo_total_cents,
        margem=_fmt(m.margem_cents),
        margem_cents=m.margem_cents,
        margem_percentual=m.margem_percentual,
        coverage_percentual=m.coverage_percentual,
    )


@router.get("/filters/options", response_model=FilterOptionsResponse)
def get_filter_options(
    dim_repo: DimensionRepository = Depends(get_dim_repo),
):
    categories = dim_repo.list_categories()
    products = [{"id": p.id, "name": p.name, "category": p.category} for p in dim_repo.list_products()]
    channels = [{"id": c.id, "name": c.name} for c in dim_repo.list_channels()]
    return FilterOptionsResponse(categories=categories, products=products, channels=channels)
