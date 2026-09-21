"""Pydantic schemas for API request/response."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class DateRangeSchema(BaseModel):
    start_date: date
    end_date: date


class FilterParams(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    product_id: int | None = None
    category: str | None = None
    channel_id: int | None = None


class DashboardSummaryResponse(BaseModel):
    faturamento: str
    faturamento_cents: int
    num_pedidos: int
    ticket_medio: str
    ticket_medio_cents: int
    itens_vendidos: int
    faturamento_anterior: str | None = None
    crescimento_percentual: float | None = None


class ProductRankingResponse(BaseModel):
    product_id: int
    product_name: str
    category: str
    quantity: int
    faturamento: str
    faturamento_cents: int
    margem: str | None = None
    margem_percentual: float | None = None


class CategoryPerformanceResponse(BaseModel):
    category: str
    quantity: int
    faturamento: str
    faturamento_cents: int
    share_percentual: float


class WeekdaySalesResponse(BaseModel):
    weekday: str
    weekday_number: int
    faturamento: str
    faturamento_cents: int
    num_pedidos: int


class ChannelSalesResponse(BaseModel):
    channel_id: int
    channel_name: str
    faturamento: str
    faturamento_cents: int
    num_pedidos: int


class TimelinePointResponse(BaseModel):
    date: date
    faturamento: str
    faturamento_cents: int
    num_pedidos: int


class ProductionWasteResponse(BaseModel):
    product_id: int
    product_name: str
    produced: int
    sold: int
    discarded: int
    waste_rate: float


class MarginResponse(BaseModel):
    faturamento: str
    faturamento_cents: int
    custo_total: str
    custo_total_cents: int
    margem: str
    margem_cents: int
    margem_percentual: float
    coverage_percentual: float


class ImportPreviewResponse(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    sample_valid: list[dict]
    sample_invalid: list[dict]
    errors: list[dict]


class ImportConfirmResponse(BaseModel):
    batch_id: int
    status: str
    total_rows: int
    accepted_rows: int
    rejected_rows: int


class ImportBatchResponse(BaseModel):
    id: int
    import_type: str
    original_filename: str
    file_hash: str
    status: str
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class ImportErrorResponse(BaseModel):
    row_number: int
    field_name: str | None = None
    error_message: str
    raw_data: str | None = None


class InsightResponse(BaseModel):
    title: str
    description: str
    evidence: str
    recommendation: str
    level: str
    metric_value: float | None = None


class FilterOptionsResponse(BaseModel):
    categories: list[str]
    products: list[dict]
    channels: list[dict]


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Mensagem de erro em português")
