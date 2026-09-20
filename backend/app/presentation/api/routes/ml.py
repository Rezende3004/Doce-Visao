"""ML routes — Machine Learning endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.application.dto.analytics import DateRange, SalesFilters
from app.infrastructure.database.connection import get_session
from app.infrastructure.repositories.implementations import (
    ProductRepository,
    SalesRepository,
)
from app.ml.anomaly.detection import detect_anomalies_isolation_forest
from app.ml.clustering.products import cluster_products, optimal_number_of_clusters
from app.ml.forecasting.demand import forecast_demand
from app.ml.trends.classification import (
    classify_all_products_trends,
    classify_product_trend,
    detect_seasonality,
)

router = APIRouter()


def _build_filters(start_date, end_date, product_id, category, channel_id) -> SalesFilters | None:
    dr = None
    if start_date and end_date:
        from datetime import date as date_type
        dr = DateRange(start_date=date_type.fromisoformat(start_date), end_date=date_type.fromisoformat(end_date))
    if not any([dr, product_id, category, channel_id]):
        return None
    return SalesFilters(date_range=dr, product_id=product_id, category=category, channel_id=channel_id)


@router.get("/forecast/demand")
def get_demand_forecast(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    days: int = Query(30, ge=7, le=90),
):
    """Forecast future demand based on historical data."""
    session = get_session()
    try:
        sales_repo = SalesRepository(session)
        filters = _build_filters(start_date, end_date, None, None, None)
        timeline = sales_repo.get_timeline(filters)

        timeline_data = [
            {"date": t.date.isoformat(), "faturamento_cents": t.faturamento_cents, "num_pedidos": t.num_pedidos}
            for t in timeline
        ]

        return forecast_demand(timeline_data, days_to_forecast=days)
    finally:
        session.close()


@router.get("/anomalies/sales")
def get_sales_anomalies(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    contamination: float = Query(0.05, ge=0.01, le=0.1),
):
    """Detect anomalous sales using Isolation Forest."""
    session = get_session()
    try:
        from sqlalchemy import select

        from app.infrastructure.database.models import DimDateModel, DimProductModel, FactSaleModel

        query = (
            select(
                DimDateModel.full_date.label("date"),
                DimProductModel.id.label("product_id"),
                DimProductModel.name.label("product_name"),
                FactSaleModel.quantity,
                FactSaleModel.total_cents,
                FactSaleModel.unit_price_cents,
            )
            .join(DimDateModel, FactSaleModel.date_id == DimDateModel.id)
            .join(DimProductModel, FactSaleModel.product_id == DimProductModel.id)
            .where(FactSaleModel.status == "completed")
        )

        if start_date and end_date:
            from datetime import date as date_type
            query = query.where(
                DimDateModel.full_date >= date_type.fromisoformat(start_date),
                DimDateModel.full_date <= date_type.fromisoformat(end_date),
            )

        rows = session.execute(query).all()
        sales_data = [
            {
                "date": r.date.isoformat(),
                "product_id": r.product_id,
                "product_name": r.product_name,
                "quantity": r.quantity,
                "total_cents": r.total_cents,
                "unit_price_cents": r.unit_price_cents,
            }
            for r in rows
        ]

        return detect_anomalies_isolation_forest(sales_data, contamination=contamination)
    finally:
        session.close()


@router.get("/clustering/products")
def get_product_clusters(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    n_clusters: int = Query(3, ge=2, le=10),
):
    """Cluster products based on sales metrics."""
    session = get_session()
    try:
        product_repo = ProductRepository(session)
        filters = _build_filters(start_date, end_date, None, None, None)

        ranking = product_repo.get_ranking_by_quantity(filters, limit=100)

        product_metrics = [
            {
                "product_id": p.product_id,
                "product_name": p.product_name,
                "quantity": p.quantity,
                "faturamento_cents": p.faturamento_cents,
            }
            for p in ranking
        ]

        return cluster_products(product_metrics, n_clusters=n_clusters)
    finally:
        session.close()


@router.get("/clustering/optimal-k")
def get_optimal_clusters(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    max_k: int = Query(10, ge=3, le=15),
):
    """Find optimal number of clusters using elbow method."""
    session = get_session()
    try:
        product_repo = ProductRepository(session)
        filters = _build_filters(start_date, end_date, None, None, None)

        ranking = product_repo.get_ranking_by_quantity(filters, limit=100)

        product_metrics = [
            {
                "product_id": p.product_id,
                "product_name": p.product_name,
                "quantity": p.quantity,
                "faturamento_cents": p.faturamento_cents,
            }
            for p in ranking
        ]

        return optimal_number_of_clusters(product_metrics, max_clusters=max_k)
    finally:
        session.close()


@router.get("/trends/all-products")
def get_all_product_trends(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    min_periods: int = Query(7, ge=3, le=30),
):
    """Classify trends for all products."""
    session = get_session()
    try:
        from sqlalchemy import select

        from app.infrastructure.database.models import DimDateModel, DimProductModel, FactSaleModel

        query = (
            select(
                DimDateModel.full_date.label("date"),
                DimProductModel.id.label("product_id"),
                DimProductModel.name.label("product_name"),
                FactSaleModel.quantity,
            )
            .join(DimDateModel, FactSaleModel.date_id == DimDateModel.id)
            .join(DimProductModel, FactSaleModel.product_id == DimProductModel.id)
            .where(FactSaleModel.status == "completed")
        )

        if start_date and end_date:
            from datetime import date as date_type
            query = query.where(
                DimDateModel.full_date >= date_type.fromisoformat(start_date),
                DimDateModel.full_date <= date_type.fromisoformat(end_date),
            )

        rows = session.execute(query).all()
        sales_data = [
            {
                "date": r.date.isoformat(),
                "product_id": r.product_id,
                "product_name": r.product_name,
                "quantity": r.quantity,
            }
            for r in rows
        ]

        return classify_all_products_trends(sales_data, min_periods=min_periods)
    finally:
        session.close()


@router.get("/trends/product/{product_id}")
def get_product_trend(
    product_id: int,
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    min_periods: int = Query(7, ge=3, le=30),
):
    """Classify trend for a specific product."""
    session = get_session()
    try:
        from sqlalchemy import select

        from app.infrastructure.database.models import DimDateModel, DimProductModel, FactSaleModel

        query = (
            select(
                DimDateModel.full_date.label("date"),
                DimProductModel.id.label("product_id"),
                DimProductModel.name.label("product_name"),
                FactSaleModel.quantity,
            )
            .join(DimDateModel, FactSaleModel.date_id == DimDateModel.id)
            .join(DimProductModel, FactSaleModel.product_id == DimProductModel.id)
            .where(FactSaleModel.status == "completed", FactSaleModel.product_id == product_id)
        )

        if start_date and end_date:
            from datetime import date as date_type
            query = query.where(
                DimDateModel.full_date >= date_type.fromisoformat(start_date),
                DimDateModel.full_date <= date_type.fromisoformat(end_date),
            )

        rows = session.execute(query).all()
        sales_data = [
            {
                "date": r.date.isoformat(),
                "product_id": r.product_id,
                "product_name": r.product_name,
                "quantity": r.quantity,
            }
            for r in rows
        ]

        return classify_product_trend(sales_data, product_id, min_periods=min_periods)
    finally:
        session.close()


@router.get("/seasonality")
def get_seasonality(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    period: str = Query("weekly", regex="^(weekly|monthly|quarterly)$"),
):
    """Detect seasonality patterns in sales."""
    session = get_session()
    try:
        from sqlalchemy import select

        from app.infrastructure.database.models import DimDateModel, FactSaleModel

        query = (
            select(
                DimDateModel.full_date.label("date"),
                FactSaleModel.quantity,
            )
            .join(DimDateModel, FactSaleModel.date_id == DimDateModel.id)
            .where(FactSaleModel.status == "completed")
        )

        if start_date and end_date:
            from datetime import date as date_type
            query = query.where(
                DimDateModel.full_date >= date_type.fromisoformat(start_date),
                DimDateModel.full_date <= date_type.fromisoformat(end_date),
            )

        rows = session.execute(query).all()
        sales_data = [{"date": r.date.isoformat(), "quantity": r.quantity} for r in rows]

        return detect_seasonality(sales_data, period=period)
    finally:
        session.close()
