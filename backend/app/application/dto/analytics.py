"""Data Transfer Objects for analytics and KPIs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class DateRange:
    start_date: date
    end_date: date


@dataclass
class SalesFilters:
    date_range: DateRange | None = None
    product_id: int | None = None
    category: str | None = None
    channel_id: int | None = None


@dataclass
class DashboardSummary:
    faturamento_cents: int
    num_pedidos: int
    ticket_medio_cents: int
    itens_vendidos: int
    faturamento_anterior_cents: int | None = None
    crescimento_percentual: float | None = None


@dataclass
class ProductRanking:
    product_id: int
    product_name: str
    category: str
    quantity: int
    faturamento_cents: int
    margem_cents: int | None = None
    margem_percentual: float | None = None


@dataclass
class CategoryPerformance:
    category: str
    quantity: int
    faturamento_cents: int
    share_percentual: float


@dataclass
class WeekdaySales:
    weekday: str
    weekday_number: int
    faturamento_cents: int
    num_pedidos: int


@dataclass
class ChannelSales:
    channel_id: int
    channel_name: str
    faturamento_cents: int
    num_pedidos: int


@dataclass
class TimelinePoint:
    date: date
    faturamento_cents: int
    num_pedidos: int


@dataclass
class ProductionWaste:
    product_id: int
    product_name: str
    produced: int
    sold: int
    discarded: int
    waste_rate: float


@dataclass
class MarginInfo:
    faturamento_cents: int
    custo_total_cents: int
    margem_cents: int
    margem_percentual: float
    coverage_percentual: float


@dataclass
class GrowthInfo:
    current_value: float
    previous_value: float
    growth_percentual: float | None
    has_sufficient_data: bool
