"""Export routes — CSV download of sales data."""

from __future__ import annotations

import io

import pandas as pd
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.infrastructure.database.models import (
    DimChannelModel,
    DimDateModel,
    DimProductModel,
    FactSaleModel,
)
from app.presentation.api.dependencies import get_db, parse_filters

router = APIRouter()


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

    # Use centralized filter application
    if filters := parse_filters(start_date, end_date, product_id, category, channel_id):
        if filters.date_range:
            query = query.where(
                DimDateModel.full_date >= filters.date_range.start_date,
                DimDateModel.full_date <= filters.date_range.end_date,
            )
        if filters.product_id:
            query = query.where(FactSaleModel.product_id == filters.product_id)
        if filters.category:
            query = query.where(DimProductModel.category == filters.category)
        if filters.channel_id:
            query = query.where(FactSaleModel.channel_id == filters.channel_id)

    rows = db.execute(query).all()
    df = pd.DataFrame(
        rows, columns=["data", "pedido", "produto", "categoria", "canal", "quantidade", "valor_unitario_cents", "desconto_cents", "total_cents", "status"]
    )
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
