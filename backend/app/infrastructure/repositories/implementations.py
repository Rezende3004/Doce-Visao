"""Repository implementations using SQLAlchemy."""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.application.dto.analytics import (
    CategoryPerformance,
    ChannelSales,
    DashboardSummary,
    DateRange,
    MarginInfo,
    ProductionWaste,
    ProductRanking,
    SalesFilters,
    TimelinePoint,
    WeekdaySales,
)
from app.domain.services.calculations import (
    calculate_growth,
    calculate_margin,
    calculate_ticket_medio,
    calculate_waste_rate,
)
from app.infrastructure.database.models import (
    DimChannelModel,
    DimDateModel,
    DimProductModel,
    FactProductionModel,
    FactSaleModel,
    ImportBatchModel,
    ImportErrorModel,
)


class ImportRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def check_duplicate(self, file_hash: str) -> ImportBatchModel | None:
        return self.session.scalar(
            select(ImportBatchModel).where(ImportBatchModel.file_hash == file_hash)
        )

    def create_batch(
        self,
        import_type: str,
        filename: str,
        file_hash: str,
        total_rows: int,
    ) -> ImportBatchModel:
        batch = ImportBatchModel(
            import_type=import_type,
            original_filename=filename,
            file_hash=file_hash,
            status="processing",
            total_rows=total_rows,
        )
        self.session.add(batch)
        self.session.flush()
        return batch

    def add_error(self, batch_id: int, row_number: int, field: str | None, message: str, raw: str | None) -> None:
        error = ImportErrorModel(
            import_batch_id=batch_id,
            row_number=row_number,
            field_name=field,
            error_message=message,
            raw_data=raw,
        )
        self.session.add(error)

    def finalize_batch(self, batch: ImportBatchModel, accepted: int, rejected: int, status: str = "completed") -> None:
        batch.accepted_rows = accepted
        batch.rejected_rows = rejected
        batch.status = status
        batch.completed_at = datetime.now()
        self.session.flush()

    def get_batch(self, batch_id: int) -> ImportBatchModel | None:
        return self.session.scalar(select(ImportBatchModel).where(ImportBatchModel.id == batch_id))

    def list_batches(self, limit: int = 50, offset: int = 0) -> list[ImportBatchModel]:
        return list(
            self.session.scalars(
                select(ImportBatchModel).order_by(ImportBatchModel.created_at.desc()).offset(offset).limit(limit)
            ).all()
        )

    def get_errors(self, batch_id: int) -> list[ImportErrorModel]:
        return list(
            self.session.scalars(
                select(ImportErrorModel).where(ImportErrorModel.import_batch_id == batch_id)
            ).all()
        )


class SalesRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _apply_filters(self, query, filters: SalesFilters | None = None, skip_date_join: bool = False):
        if filters is None:
            return query
        if filters.date_range and not skip_date_join:
            query = query.join(DimDateModel).where(
                DimDateModel.full_date >= filters.date_range.start_date,
                DimDateModel.full_date <= filters.date_range.end_date,
            )
        elif filters.date_range and skip_date_join:
            query = query.where(
                DimDateModel.full_date >= filters.date_range.start_date,
                DimDateModel.full_date <= filters.date_range.end_date,
            )
        if filters.product_id:
            query = query.where(FactSaleModel.product_id == filters.product_id)
        if filters.category:
            query = query.join(DimProductModel).where(DimProductModel.category == filters.category)
        if filters.channel_id:
            query = query.where(FactSaleModel.channel_id == filters.channel_id)
        return query

    def get_summary(self, filters: SalesFilters | None = None) -> DashboardSummary:
        base = select(
            func.coalesce(func.sum(FactSaleModel.total_cents), 0).label("faturamento"),
            func.count(func.distinct(FactSaleModel.external_order_id)).label("pedidos"),
            func.coalesce(func.sum(FactSaleModel.quantity), 0).label("itens"),
        ).where(FactSaleModel.status == "completed")

        base = self._apply_filters(base, filters)
        row = self.session.execute(base).one()

        faturamento = row.faturamento
        pedidos = row.pedidos
        itens = row.itens
        ticket = calculate_ticket_medio(faturamento, pedidos)

        crescimento = None
        faturamento_anterior = None
        if filters and filters.date_range:
            prev_range = self._previous_period(filters.date_range)
            prev_filters = SalesFilters(
                date_range=prev_range,
                product_id=filters.product_id,
                category=filters.category,
                channel_id=filters.channel_id,
            )
            prev_q = select(func.coalesce(func.sum(FactSaleModel.total_cents), 0)).where(
                FactSaleModel.status == "completed"
            )
            prev_q = self._apply_filters(prev_q, prev_filters)
            faturamento_anterior = self.session.scalar(prev_q)
            crescimento = calculate_growth(faturamento, faturamento_anterior)

        return DashboardSummary(
            faturamento_cents=faturamento,
            num_pedidos=pedidos,
            ticket_medio_cents=ticket,
            itens_vendidos=itens,
            faturamento_anterior_cents=faturamento_anterior,
            crescimento_percentual=crescimento,
        )

    def _previous_period(self, dr: DateRange) -> DateRange:
        from datetime import timedelta
        duration = (dr.end_date - dr.start_date).days + 1
        prev_end = dr.start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=duration - 1)
        return DateRange(start_date=prev_start, end_date=prev_end)

    def get_timeline(self, filters: SalesFilters | None = None) -> list[TimelinePoint]:
        query = (
            select(
                DimDateModel.full_date,
                func.coalesce(func.sum(FactSaleModel.total_cents), 0).label("faturamento"),
                func.count(func.distinct(FactSaleModel.external_order_id)).label("pedidos"),
            )
            .join(DimDateModel, FactSaleModel.date_id == DimDateModel.id)
            .where(FactSaleModel.status == "completed")
            .group_by(DimDateModel.full_date)
            .order_by(DimDateModel.full_date)
        )
        query = self._apply_filters(query, filters, skip_date_join=True)
        rows = self.session.execute(query).all()
        return [TimelinePoint(date=r.full_date, faturamento_cents=r.faturamento, num_pedidos=r.pedidos) for r in rows]

    def get_by_weekday(self, filters: SalesFilters | None = None) -> list[WeekdaySales]:
        query = (
            select(
                DimDateModel.weekday_name,
                DimDateModel.weekday_number,
                func.coalesce(func.sum(FactSaleModel.total_cents), 0).label("faturamento"),
                func.count(func.distinct(FactSaleModel.external_order_id)).label("pedidos"),
            )
            .join(DimDateModel, FactSaleModel.date_id == DimDateModel.id)
            .where(FactSaleModel.status == "completed")
            .group_by(DimDateModel.weekday_name, DimDateModel.weekday_number)
            .order_by(DimDateModel.weekday_number)
        )
        query = self._apply_filters(query, filters, skip_date_join=True)
        rows = self.session.execute(query).all()
        return [
            WeekdaySales(weekday=r.weekday_name, weekday_number=r.weekday_number, faturamento_cents=r.faturamento, num_pedidos=r.pedidos)
            for r in rows
        ]

    def get_by_channel(self, filters: SalesFilters | None = None) -> list[ChannelSales]:
        query = (
            select(
                DimChannelModel.id,
                DimChannelModel.name,
                func.coalesce(func.sum(FactSaleModel.total_cents), 0).label("faturamento"),
                func.count(func.distinct(FactSaleModel.external_order_id)).label("pedidos"),
            )
            .join(DimChannelModel, FactSaleModel.channel_id == DimChannelModel.id)
            .where(FactSaleModel.status == "completed")
            .group_by(DimChannelModel.id, DimChannelModel.name)
            .order_by(func.sum(FactSaleModel.total_cents).desc())
        )
        query = self._apply_filters(query, filters)
        rows = self.session.execute(query).all()
        return [
            ChannelSales(channel_id=r.id, channel_name=r.name, faturamento_cents=r.faturamento, num_pedidos=r.pedidos)
            for r in rows
        ]


class ProductRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_ranking_by_quantity(self, filters: SalesFilters | None = None, limit: int = 20) -> list[ProductRanking]:
        query = (
            select(
                DimProductModel.id,
                DimProductModel.name,
                DimProductModel.category,
                func.coalesce(func.sum(FactSaleModel.quantity), 0).label("quantity"),
                func.coalesce(func.sum(FactSaleModel.total_cents), 0).label("faturamento"),
            )
            .join(DimProductModel, FactSaleModel.product_id == DimProductModel.id)
            .where(FactSaleModel.status == "completed")
            .group_by(DimProductModel.id, DimProductModel.name, DimProductModel.category)
            .order_by(func.sum(FactSaleModel.quantity).desc())
            .limit(limit)
        )
        if filters:
            if filters.date_range:
                query = query.join(DimDateModel).where(
                    DimDateModel.full_date >= filters.date_range.start_date,
                    DimDateModel.full_date <= filters.date_range.end_date,
                )
            if filters.category:
                query = query.where(DimProductModel.category == filters.category)
            if filters.product_id:
                query = query.where(DimProductModel.id == filters.product_id)
        rows = self.session.execute(query).all()
        return [
            ProductRanking(
                product_id=r.id,
                product_name=r.name,
                category=r.category,
                quantity=r.quantity,
                faturamento_cents=r.faturamento,
            )
            for r in rows
        ]

    def get_ranking_by_revenue(self, filters: SalesFilters | None = None, limit: int = 20) -> list[ProductRanking]:
        query = (
            select(
                DimProductModel.id,
                DimProductModel.name,
                DimProductModel.category,
                func.coalesce(func.sum(FactSaleModel.quantity), 0).label("quantity"),
                func.coalesce(func.sum(FactSaleModel.total_cents), 0).label("faturamento"),
            )
            .join(DimProductModel, FactSaleModel.product_id == DimProductModel.id)
            .where(FactSaleModel.status == "completed")
            .group_by(DimProductModel.id, DimProductModel.name, DimProductModel.category)
            .order_by(func.sum(FactSaleModel.total_cents).desc())
            .limit(limit)
        )
        if filters:
            if filters.date_range:
                query = query.join(DimDateModel).where(
                    DimDateModel.full_date >= filters.date_range.start_date,
                    DimDateModel.full_date <= filters.date_range.end_date,
                )
            if filters.category:
                query = query.where(DimProductModel.category == filters.category)
        rows = self.session.execute(query).all()
        return [
            ProductRanking(
                product_id=r.id,
                product_name=r.name,
                category=r.category,
                quantity=r.quantity,
                faturamento_cents=r.faturamento,
            )
            for r in rows
        ]

    def get_category_performance(self, filters: SalesFilters | None = None) -> list[CategoryPerformance]:
        query = (
            select(
                DimProductModel.category,
                func.coalesce(func.sum(FactSaleModel.quantity), 0).label("quantity"),
                func.coalesce(func.sum(FactSaleModel.total_cents), 0).label("faturamento"),
            )
            .join(DimProductModel, FactSaleModel.product_id == DimProductModel.id)
            .where(FactSaleModel.status == "completed")
            .group_by(DimProductModel.category)
            .order_by(func.sum(FactSaleModel.total_cents).desc())
        )
        if filters:
            if filters.date_range:
                query = query.join(DimDateModel).where(
                    DimDateModel.full_date >= filters.date_range.start_date,
                    DimDateModel.full_date <= filters.date_range.end_date,
                )
        rows = self.session.execute(query).all()
        total = sum(r.faturamento for r in rows)
        return [
            CategoryPerformance(
                category=r.category,
                quantity=r.quantity,
                faturamento_cents=r.faturamento,
                share_percentual=(r.faturamento / total * 100) if total > 0 else 0.0,
            )
            for r in rows
        ]

    def get_margin_info(self, filters: SalesFilters | None = None) -> MarginInfo:
        query = select(
            func.coalesce(func.sum(FactSaleModel.total_cents), 0).label("faturamento"),
            func.coalesce(func.sum(FactSaleModel.unit_cost_cents * FactSaleModel.quantity), 0).label("custo"),
            func.count(FactSaleModel.id).label("total"),
            func.count(FactSaleModel.unit_cost_cents).label("com_custo"),
        ).where(FactSaleModel.status == "completed", FactSaleModel.unit_cost_cents.isnot(None))

        if filters:
            if filters.date_range:
                query = query.join(DimDateModel).where(
                    DimDateModel.full_date >= filters.date_range.start_date,
                    DimDateModel.full_date <= filters.date_range.end_date,
                )
            if filters.product_id:
                query = query.where(FactSaleModel.product_id == filters.product_id)
            if filters.category:
                query = query.join(DimProductModel).where(DimProductModel.category == filters.category)

        row = self.session.execute(query).one()
        faturamento = row.faturamento
        custo = row.custo
        margem, percentual = calculate_margin(faturamento, custo)
        coverage = (row.com_custo / row.total * 100) if row.total > 0 else 0.0
        return MarginInfo(
            faturamento_cents=faturamento,
            custo_total_cents=custo,
            margem_cents=margem,
            margem_percentual=percentual,
            coverage_percentual=coverage,
        )


class ProductionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_waste_by_product(self, filters: SalesFilters | None = None) -> list[ProductionWaste]:
        query = (
            select(
                DimProductModel.id,
                DimProductModel.name,
                func.coalesce(func.sum(FactProductionModel.produced_quantity), 0).label("produced"),
                func.coalesce(func.sum(FactProductionModel.sold_quantity), 0).label("sold"),
                func.coalesce(func.sum(FactProductionModel.discarded_quantity), 0).label("discarded"),
            )
            .join(DimProductModel, FactProductionModel.product_id == DimProductModel.id)
            .group_by(DimProductModel.id, DimProductModel.name)
            .order_by(func.sum(FactProductionModel.discarded_quantity).desc())
        )
        if filters:
            if filters.date_range:
                query = query.join(DimDateModel).where(
                    DimDateModel.full_date >= filters.date_range.start_date,
                    DimDateModel.full_date <= filters.date_range.end_date,
                )
            if filters.product_id:
                query = query.where(DimProductModel.id == filters.product_id)
        rows = self.session.execute(query).all()
        return [
            ProductionWaste(
                product_id=r.id,
                product_name=r.name,
                produced=r.produced,
                sold=r.sold,
                discarded=r.discarded,
                waste_rate=calculate_waste_rate(r.discarded, r.produced),
            )
            for r in rows
        ]


class DimensionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_create_product(self, name: str, category: str) -> DimProductModel:
        normalized = name.strip().lower()
        product = self.session.scalar(
            select(DimProductModel).where(DimProductModel.normalized_name == normalized)
        )
        if product is None:
            product = DimProductModel(name=name.strip(), normalized_name=normalized, category=category.strip())
            self.session.add(product)
            self.session.flush()
        return product

    def get_or_create_date(self, d: date) -> DimDateModel:
        dm = self.session.scalar(select(DimDateModel).where(DimDateModel.full_date == d))
        if dm is None:
            month_names = [
                "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
            ]
            weekday_names = [
                "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
                "Sexta-feira", "Sábado", "Domingo",
            ]
            dm = DimDateModel(
                full_date=d,
                day=d.day,
                month=d.month,
                month_name=month_names[d.month - 1],
                quarter=(d.month - 1) // 3 + 1,
                year=d.year,
                weekday_number=d.weekday(),
                weekday_name=weekday_names[d.weekday()],
                is_weekend=d.weekday() >= 5,
            )
            self.session.add(dm)
            self.session.flush()
        return dm

    def get_or_create_channel(self, name: str) -> DimChannelModel:
        normalized = name.strip().lower()
        channel = self.session.scalar(
            select(DimChannelModel).where(DimChannelModel.normalized_name == normalized)
        )
        if channel is None:
            channel = DimChannelModel(name=name.strip(), normalized_name=normalized)
            self.session.add(channel)
            self.session.flush()
        return channel

    def list_categories(self) -> list[str]:
        return list(self.session.scalars(select(DimProductModel.category).distinct().order_by(DimProductModel.category)).all())

    def list_products(self) -> list[DimProductModel]:
        return list(self.session.scalars(select(DimProductModel).order_by(DimProductModel.name)).all())

    def list_channels(self) -> list[DimChannelModel]:
        return list(self.session.scalars(select(DimChannelModel).order_by(DimChannelModel.name)).all())
