"""Domain entities for DoceVisão.

These are pure Python dataclasses — no ORM dependencies.
Infrastructure layer maps these to/from SQLAlchemy models.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Product:
    id: int
    name: str
    normalized_name: str
    category: str
    active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class DateDimension:
    id: int
    full_date: date
    day: int
    month: int
    month_name: str
    quarter: int
    year: int
    weekday_number: int
    weekday_name: str
    is_weekend: bool


@dataclass
class Channel:
    id: int
    name: str
    normalized_name: str


@dataclass
class SaleRecord:
    id: int
    external_order_id: str
    external_item_id: str
    product_id: int
    date_id: int
    channel_id: int | None
    payment_method: str | None
    quantity: int
    unit_price_cents: int
    discount_cents: int
    unit_cost_cents: int | None
    total_cents: int
    status: str
    import_batch_id: int
    created_at: datetime | None = None


@dataclass
class ProductionRecord:
    id: int
    product_id: int
    date_id: int
    produced_quantity: int
    sold_quantity: int
    discarded_quantity: int
    discard_reason: str | None
    import_batch_id: int
    created_at: datetime | None = None


@dataclass
class ImportBatch:
    id: int
    import_type: str
    original_filename: str
    file_hash: str
    status: str
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None


@dataclass
class ImportErrorDetail:
    id: int
    import_batch_id: int
    row_number: int
    field_name: str | None
    error_message: str
    raw_data: str | None
