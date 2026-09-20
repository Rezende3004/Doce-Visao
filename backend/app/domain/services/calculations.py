"""Domain services — pure business logic, no I/O."""
from __future__ import annotations

from datetime import date


def calculate_total_cents(quantity: int, unit_price_cents: int, discount_cents: int) -> int:
    raw = quantity * unit_price_cents
    discount = min(discount_cents, raw)
    return max(raw - discount, 0)


def calculate_margin(faturamento_cents: int, custo_total_cents: int) -> tuple[int, float]:
    margem = faturamento_cents - custo_total_cents
    if faturamento_cents == 0:
        return margem, 0.0
    percentual = (margem / faturamento_cents) * 100
    return margem, percentual


def calculate_waste_rate(discarded: int, produced: int) -> float:
    if produced == 0:
        return 0.0
    return (discarded / produced) * 100


def calculate_ticket_medio(faturamento_cents: int, num_pedidos: int) -> int:
    if num_pedidos == 0:
        return 0
    return faturamento_cents // num_pedidos


def calculate_growth(current: float, previous: float) -> float | None:
    if previous == 0:
        return None if current == 0 else float("inf")
    return ((current - previous) / previous) * 100


def is_valid_sale_date(d: date) -> bool:
    today = date.today()
    return date(2000, 1, 1) <= d <= today
