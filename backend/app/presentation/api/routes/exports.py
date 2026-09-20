"""Export routes — CSV download of sales data."""
from __future__ import annotations

import io

import pandas as pd
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.application.dto.analytics import DateRange, SalesFilters
from app.infrastructure.database.models import (
    DimChannelModel,
    DimDateModel,
    DimProductModel,
    FactSaleModel,
)
from app.presentation.api.dependencies import get_db

router = APIRouter()


def _build_filters(start_date, end_date, product_id, category, channel_id) -> SalesFilters | None:
    dr = None
    if start_date and end_date:
        from datetime import date as date_type
        dr = DateRange(start_date=date_type.fromisoformat(start_date), end_date=date_type.fromisoformat(end_date))
    if not any([dr, product_id, category, channel_id]):
        return None
    return SalesFilters(date_range=dr, product_id=product_id, category=category, channel_id=channel_id)


@router.get("/sales")
def export_sales(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    product_id: int | None = Query(None),
    category: str | None = Query(None),
    channel_id: int | None = Query(None),
    db=Depends(get_db),
):
    query = (
        select(
            DimDateModel.full_date.label("data"),
            FactSaleModel.external_order_id.label("pedido"),
            DimProductModel.name.label("produto"),
            DimProductModel.category.label("categoria"),
            DimChannelModel.name.label("canal"),
            FactSaleModel.quantity.label("quantidade"),
            FactSaleModel.unit_price_cents.label("valor_unitario_cents"),
            FactSaleModel.discount_cents.label("desconto_cents"),
            FactSaleModel.total_cents.label("total_cents"),
            FactSaleModel.status,
        )
        .join(DimDateModel, FactSaleModel.date_id == DimDateModel.id)
        .join(DimProductModel, FactSaleModel.product_id == DimProductModel.id)
        .outerjoin(DimChannelModel, FactSaleModel.channel_id == DimChannelModel.id)
        .where(FactSaleModel.status == "completed")
    )

    if start_date and end_date:
        from datetime import date as date_type
        query = query.where(
            DimDateModel.full_date >= date_type.fromisoformat(start_date),
            DimDateModel.full_date <= date_type.fromisoformat(end_date),
        )
    if product_id:
        query = query.where(FactSaleModel.product_id == product_id)
    if category:
        query = query.where(DimProductModel.category == category)
    if channel_id:
        query = query.where(FactSaleModel.channel_id == channel_id)

    rows = db.execute(query).all()
    df = pd.DataFrame(rows, columns=["data", "pedido", "produto", "categoria", "canal", "quantidade",
                                      "valor_unitario_cents", "desconto_cents", "total_cents", "status"])
    df["valor_unitario"] = df["valor_unitario_cents"] / 100
    df["desconto"] = df["desconto_cents"] / 100
    df["total"] = df["total_cents"] / 100
    df = df.drop(columns=["valor_unitario_cents", "desconto_cents", "total_cents"])

    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=export_vendas.csv"},
    )
