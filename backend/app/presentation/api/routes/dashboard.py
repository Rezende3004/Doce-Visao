"""Dashboard routes — summary KPIs."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.application.dto.analytics import DateRange, SalesFilters
from app.infrastructure.repositories.implementations import SalesRepository
from app.presentation.api.dependencies import get_sales_repo
from app.presentation.api.schemas.schemas import DashboardSummaryResponse

router = APIRouter()


def _fmt(cents: int) -> str:
    return f"R$ {cents / 100:.2f}".replace(".", ",")


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_summary(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    product_id: int | None = Query(None),
    category: str | None = Query(None),
    channel_id: int | None = Query(None),
    sales_repo: SalesRepository = Depends(get_sales_repo),
):
    filters = _build_filters(start_date, end_date, product_id, category, channel_id)
    summary = sales_repo.get_summary(filters)
    return DashboardSummaryResponse(
        faturamento=_fmt(summary.faturamento_cents),
        faturamento_cents=summary.faturamento_cents,
        num_pedidos=summary.num_pedidos,
        ticket_medio=_fmt(summary.ticket_medio_cents),
        ticket_medio_cents=summary.ticket_medio_cents,
        itens_vendidos=summary.itens_vendidos,
        faturamento_anterior=_fmt(summary.faturamento_anterior_cents) if summary.faturamento_anterior_cents is not None else None,
        crescimento_percentual=summary.crescimento_percentual,
    )


def _build_filters(start_date, end_date, product_id, category, channel_id) -> SalesFilters | None:
    dr = None
    if start_date and end_date:
        from datetime import date as date_type
        dr = DateRange(start_date=date_type.fromisoformat(start_date), end_date=date_type.fromisoformat(end_date))
    if not any([dr, product_id, category, channel_id]):
        return None
    return SalesFilters(date_range=dr, product_id=product_id, category=category, channel_id=channel_id)
