"""Data Transfer Objects for import operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ImportPreview:
    total_rows: int
    valid_rows: int
    invalid_rows: int
    sample_valid: list[dict]
    sample_invalid: list[dict]
    errors: list[dict]


@dataclass
class ImportResult:
    batch_id: int
    status: str
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    errors: list[ImportErrorRow]


@dataclass
class ImportErrorRow:
    row_number: int
    field_name: str | None
    error_message: str
    raw_data: str | None


@dataclass
class ImportBatchSummary:
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
