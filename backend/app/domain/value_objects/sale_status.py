"""Sale status normalization."""

from __future__ import annotations

from enum import Enum

from app.domain.exceptions.errors import InvalidSaleStatusError


class SaleStatus(str, Enum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PENDING = "pending"


_STATUS_MAP: dict[str, SaleStatus] = {
    "concluido": SaleStatus.COMPLETED,
    "concluído": SaleStatus.COMPLETED,
    "finalizado": SaleStatus.COMPLETED,
    "completed": SaleStatus.COMPLETED,
    "complete": SaleStatus.COMPLETED,
    "done": SaleStatus.COMPLETED,
    "pago": SaleStatus.COMPLETED,
    "efetivado": SaleStatus.COMPLETED,
    "cancelado": SaleStatus.CANCELLED,
    "cancelled": SaleStatus.CANCELLED,
    "canceled": SaleStatus.CANCELLED,
    "anulado": SaleStatus.CANCELLED,
    "pendente": SaleStatus.PENDING,
    "pending": SaleStatus.PENDING,
    "aguardando": SaleStatus.PENDING,
}


def normalize_status(raw: str) -> SaleStatus:
    key = raw.strip().lower()
    status = _STATUS_MAP.get(key)
    if status is None:
        raise InvalidSaleStatusError(f"Status não reconhecido: '{raw}'")
    return status


COMPLETED_STATUSES = {SaleStatus.COMPLETED}
EXCLUDED_FROM_KPIS = {SaleStatus.CANCELLED}
