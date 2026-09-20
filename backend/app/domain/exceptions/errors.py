"""Domain exceptions for DoceVisão."""
from __future__ import annotations


class DomainError(Exception):
    """Base domain exception."""


class InvalidSaleStatusError(DomainError):
    """Raised when a sale status is not recognized."""


class NegativeValueError(DomainError):
    """Raised when a monetary or quantity value is negative."""


class InvalidDateError(DomainError):
    """Raised when a date is impossible or out of range."""


class DuplicateImportError(DomainError):
    """Raised when attempting to import an already-imported file."""


class ImportFailedError(DomainError):
    """Raised when an import operation fails."""


class InsufficientDataError(DomainError):
    """Raised when there's not enough data for a calculation."""
