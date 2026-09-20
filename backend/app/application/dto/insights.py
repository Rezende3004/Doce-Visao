"""Data Transfer Object for insights."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class InsightLevel(str, Enum):
    INFORMATIVO = "informativo"
    ATENCAO = "atencao"
    OPORTUNIDADE = "oportunidade"


@dataclass
class Insight:
    title: str
    description: str
    evidence: str
    recommendation: str
    level: InsightLevel
    metric_value: float | None = None
