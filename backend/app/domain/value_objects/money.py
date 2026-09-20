"""Money value object — all monetary values in cents (int)."""
from __future__ import annotations

from app.domain.exceptions.errors import NegativeValueError


class Money:
    __slots__ = ("cents",)

    def __init__(self, cents: int) -> None:
        if cents < 0:
            raise NegativeValueError(f"Monetary value cannot be negative: {cents}")
        self.cents = cents

    @classmethod
    def from_brl_string(cls, value: str) -> Money:
        cleaned = value.strip().replace("R$", "").replace(" ", "")
        cleaned = cleaned.replace(".", "").replace(",", ".")
        brl = float(cleaned)
        return cls(int(round(brl * 100)))

    @classmethod
    def zero(cls) -> Money:
        return cls(0)

    def __add__(self, other: Money) -> Money:
        return Money(self.cents + other.cents)

    def __mul__(self, factor: int) -> Money:
        return Money(self.cents * factor)

    def __sub__(self, other: Money) -> Money:
        result = self.cents - other.cents
        if result < 0:
            raise NegativeValueError("Resulting monetary value would be negative")
        return Money(result)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.cents == other.cents

    def __lt__(self, other: Money) -> bool:
        return self.cents < other.cents

    def __repr__(self) -> str:
        return f"Money({self.cents})"

    def to_brl_float(self) -> float:
        return self.cents / 100.0

    def format_brl(self) -> str:
        return f"R$ {self.cents / 100:.2f}".replace(".", ",")
