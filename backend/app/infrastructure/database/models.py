"""SQLAlchemy ORM models — these map to database tables."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base


class ImportBatchModel(Base):
    __tablename__ = "import_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    import_type: Mapped[str] = mapped_column(String(50), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accepted_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rejected_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    errors: Mapped[list[ImportErrorModel]] = relationship(back_populates="batch", cascade="all, delete-orphan")


class ImportErrorModel(Base):
    __tablename__ = "import_errors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    import_batch_id: Mapped[int] = mapped_column(ForeignKey("import_batches.id"), nullable=False)
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    field_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    raw_data: Mapped[str | None] = mapped_column(Text, nullable=True)

    batch: Mapped[ImportBatchModel] = relationship(back_populates="errors")


class DimProductModel(Base):
    __tablename__ = "dim_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class DimDateModel(Base):
    __tablename__ = "dim_dates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    month_name: Mapped[str] = mapped_column(String(50), nullable=False)
    quarter: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    weekday_number: Mapped[int] = mapped_column(Integer, nullable=False)
    weekday_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_weekend: Mapped[bool] = mapped_column(Boolean, nullable=False)


class DimChannelModel(Base):
    __tablename__ = "dim_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)


class FactSaleModel(Base):
    __tablename__ = "fact_sales"
    __table_args__ = (
        UniqueConstraint("external_order_id", "external_item_id", name="uq_sale_item"),
        Index("ix_sale_date", "date_id"),
        Index("ix_sale_product", "product_id"),
        Index("ix_sale_channel", "channel_id"),
        Index("ix_sale_status", "status"),
        Index("ix_sale_batch", "import_batch_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_order_id: Mapped[str] = mapped_column(String(100), nullable=False)
    external_item_id: Mapped[str] = mapped_column(String(200), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("dim_products.id"), nullable=False)
    date_id: Mapped[int] = mapped_column(ForeignKey("dim_dates.id"), nullable=False)
    channel_id: Mapped[int | None] = mapped_column(ForeignKey("dim_channels.id"), nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    discount_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unit_cost_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    import_batch_id: Mapped[int] = mapped_column(ForeignKey("import_batches.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class FactProductionModel(Base):
    __tablename__ = "fact_production"
    __table_args__ = (
        Index("ix_prod_date", "date_id"),
        Index("ix_prod_product", "product_id"),
        Index("ix_prod_batch", "import_batch_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("dim_products.id"), nullable=False)
    date_id: Mapped[int] = mapped_column(ForeignKey("dim_dates.id"), nullable=False)
    produced_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    sold_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    discarded_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    discard_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    import_batch_id: Mapped[int] = mapped_column(ForeignKey("import_batches.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
