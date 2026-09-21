"""Sales routes — timeline, weekday, channel."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.infrastructure.repositories.implementations import SalesRepository
from app.presentation.api.dependencies import get_sales_repo, parse_filters
from app.presentation.api.schemas.schemas import (
    ChannelSalesResponse,
    TimelinePointResponse,
    WeekdaySalesResponse,
)

router = APIRouter()


def _fmt(cents: int) -> str:
    return f"R$ {cents / 100:.2f}".replace(".", ",")


@router.get("/timeline", response_model=list[TimelinePointResponse])
def get_timeline(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    product_id: int | None = Query(None),
    category: str | None = Query(None),
    channel_id: int | None = Query(None),
    sales_repo: SalesRepository = Depends(get_sales_repo),
):
    filters = parse_filters(start_date, end_date, product_id, category, channel_id)
    data = sales_repo.get_timeline(filters)
    return [
        TimelinePointResponse(date=p.date, faturamento=_fmt(p.faturamento_cents), faturamento_cents=p.faturamento_cents, num_pedidos=p.num_pedidos)
        for p in data
    ]


@router.get("/by-weekday", response_model=list[WeekdaySalesResponse])
def get_by_weekday(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    product_id: int | None = Query(None),
    category: str | None = Query(None),
    channel_id: int | None = Query(None),
    sales_repo: SalesRepository = Depends(get_sales_repo),
):
    filters = parse_filters(start_date, end_date, product_id, category, channel_id)
    data = sales_repo.get_by_weekday(filters)
    return [
        WeekdaySalesResponse(
            weekday=w.weekday,
            weekday_number=w.weekday_number,
            faturamento=_fmt(w.faturamento_cents),
            faturamento_cents=w.faturamento_cents,
            num_pedidos=w.num_pedidos,
        )
        for w in data
    ]


@router.get("/by-channel", response_model=list[ChannelSalesResponse])
def get_by_channel(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    product_id: int | None = Query(None),
    category: str | None = Query(None),
    channel_id: int | None = Query(None),
    sales_repo: SalesRepository = Depends(get_sales_repo),
):
    filters = parse_filters(start_date, end_date, product_id, category, channel_id)
    data = sales_repo.get_by_channel(filters)
    return [
        ChannelSalesResponse(
            channel_id=c.channel_id,
            channel_name=c.channel_name,
            faturamento=_fmt(c.faturamento_cents),
            faturamento_cents=c.faturamento_cents,
            num_pedidos=c.num_pedidos,
        )
        for c in data
    ]
