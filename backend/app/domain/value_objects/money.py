"""Money value object — all monetary values in cents (int). Uses integer arithmetic."""

from __future__ import annotations

import re

from app.domain.exceptions.errors import NegativeValueError


class Money:
    __slots__ = ("cents",)

    def __init__(self, cents: int) -> None:
        if cents < 0:
            raise NegativeValueError(f"Monetary value cannot be negative: {cents}")
        self.cents = cents

    @classmethod
    def from_brl_string(cls, value: str) -> Money:
        """Parse Brazilian currency string to cents using pure integer math.

        Accepts: 10 | 10,00 | 10.00 | R$ 10,00 | 1.234,56
        Raises ValueError on invalid formats.
        """
        cleaned = value.strip().replace("R$", "").strip()
        if not cleaned:
            return cls(0)

        # Validate format: only digits, dots, commas allowed
        if not re.fullmatch(r"[.\d,]+", cleaned):
            raise ValueError(f"Valor monetário inválido: {value}")

        # Brazilian number parsing (no float involved):
        # - dot = thousands separator
        # - comma = decimal separator
        if "," in cleaned:
            integer_part, decimal_part = cleaned.rsplit(",", 1)
            integer_part = integer_part.replace(".", "").strip()
            decimal_part = decimal_part.strip()[:2].ljust(2, "0")
            total_cents_str = f"{integer_part}{decimal_part}"
        else:
            # No comma — dots are thousands separators
            total_cents_str = cleaned.replace(".", "").strip()

        if not total_cents_str.isdigit():
            raise ValueError(f"Valor monetário inválido: {value}")

        return cls(int(total_cents_str))

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
