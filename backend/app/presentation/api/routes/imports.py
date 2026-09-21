"""Import routes — upload, preview, confirm, list, errors."""

from __future__ import annotations

import io

import pandas as pd
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse

from app.config import settings
from app.infrastructure.importers.file_importer import (
    compute_file_hash,
    confirm_production_import,
    confirm_sales_import,
    preview_production,
    preview_sales,
    read_upload,
)
from app.infrastructure.repositories.implementations import DimensionRepository, ImportRepository
from app.presentation.api.dependencies import get_dim_repo, get_import_repo
from app.presentation.api.schemas.schemas import (
    ImportBatchResponse,
    ImportConfirmResponse,
    ImportErrorResponse,
    ImportPreviewResponse,
)

router = APIRouter()


def _validate_upload(file: UploadFile) -> bytes:
    if not file.filename:
        raise ValueError("Nome do arquivo ausente.")
    lower = file.filename.lower()
    if not lower.endswith((".csv", ".xlsx")):
        raise ValueError("Formato não suportado. Use CSV (.csv) ou Excel (.xlsx).")
    content = file.file.read()
    if len(content) > settings.max_upload_bytes:
        raise ValueError(f"Arquivo excede o tamanho máximo de {settings.max_upload_size_mb}MB.")
    return content


@router.get("/templates/sales")
def sales_template():
    columns = [
        "data_venda",
        "id_pedido",
        "id_item",
        "produto",
        "categoria",
        "quantidade",
        "valor_unitario",
        "desconto",
        "canal",
        "forma_pagamento",
        "custo_unitario",
        "status",
    ]
    df = pd.DataFrame(columns=columns)
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(buf, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=modelo_vendas.csv"})


@router.get("/templates/production")
def production_template():
    columns = ["data", "produto", "categoria", "quantidade_produzida", "quantidade_vendida", "quantidade_descartada", "motivo_descarte"]
    df = pd.DataFrame(columns=columns)
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(buf, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=modelo_producao.csv"})


@router.post("/sales/preview", response_model=ImportPreviewResponse)
async def sales_preview(file: UploadFile = File(...)):
    content = _validate_upload(file)
    df = read_upload(content, file.filename)
    preview = preview_sales(df)
    return ImportPreviewResponse(**preview.__dict__)


@router.post("/sales/confirm", response_model=ImportConfirmResponse)
async def sales_confirm(
    file: UploadFile = File(...),
    import_repo: ImportRepository = Depends(get_import_repo),
    dim_repo: DimensionRepository = Depends(get_dim_repo),
):
    content = _validate_upload(file)
    file_hash = compute_file_hash(content)
    df = read_upload(content, file.filename)
    result = confirm_sales_import(df, import_repo, dim_repo, file.filename, file_hash)
    return ImportConfirmResponse(
        batch_id=result.batch_id,
        status=result.status,
        total_rows=result.total_rows,
        accepted_rows=result.accepted_rows,
        rejected_rows=result.rejected_rows,
    )


@router.post("/production/preview", response_model=ImportPreviewResponse)
async def production_preview(file: UploadFile = File(...)):
    content = _validate_upload(file)
    df = read_upload(content, file.filename)
    preview = preview_production(df)
    return ImportPreviewResponse(**preview.__dict__)


@router.post("/production/confirm", response_model=ImportConfirmResponse)
async def production_confirm(
    file: UploadFile = File(...),
    import_repo: ImportRepository = Depends(get_import_repo),
    dim_repo: DimensionRepository = Depends(get_dim_repo),
):
    content = _validate_upload(file)
    file_hash = compute_file_hash(content)
    df = read_upload(content, file.filename)
    result = confirm_production_import(df, import_repo, dim_repo, file.filename, file_hash)
    return ImportConfirmResponse(
        batch_id=result.batch_id,
        status=result.status,
        total_rows=result.total_rows,
        accepted_rows=result.accepted_rows,
        rejected_rows=result.rejected_rows,
    )


@router.get("", response_model=list[ImportBatchResponse])
def list_imports(
    limit: int = 50,
    offset: int = 0,
    import_repo: ImportRepository = Depends(get_import_repo),
):
    batches = import_repo.list_batches(limit, offset)
    return [
        ImportBatchResponse(
            id=b.id,
            import_type=b.import_type,
            original_filename=b.original_filename,
            file_hash=b.file_hash,
            status=b.status,
            total_rows=b.total_rows,
            accepted_rows=b.accepted_rows,
            rejected_rows=b.rejected_rows,
            error_message=b.error_message,
            created_at=b.created_at,
            completed_at=b.completed_at,
        )
        for b in batches
    ]


@router.get("/{batch_id}", response_model=ImportBatchResponse)
def get_import(batch_id: int, import_repo: ImportRepository = Depends(get_import_repo)):
    batch = import_repo.get_batch(batch_id)
    if not batch:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Lote de importação não encontrado.")
    return ImportBatchResponse(
        id=batch.id,
        import_type=batch.import_type,
        original_filename=batch.original_filename,
        file_hash=batch.file_hash,
        status=batch.status,
        total_rows=batch.total_rows,
        accepted_rows=batch.accepted_rows,
        rejected_rows=batch.rejected_rows,
        error_message=batch.error_message,
        created_at=batch.created_at,
        completed_at=batch.completed_at,
    )


@router.get("/{batch_id}/errors", response_model=list[ImportErrorResponse])
def get_import_errors(batch_id: int, import_repo: ImportRepository = Depends(get_import_repo)):
    errors = import_repo.get_errors(batch_id)
    return [
        ImportErrorResponse(
            row_number=e.row_number,
            field_name=e.field_name,
            error_message=e.error_message,
            raw_data=e.raw_data,
        )
        for e in errors
    ]
