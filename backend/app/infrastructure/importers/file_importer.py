"""File import logic — CSV/Excel parsing, validation, and persistence."""
from __future__ import annotations

import hashlib
import io
import re
from datetime import date, datetime

import pandas as pd

from app.application.dto.imports import ImportErrorRow, ImportPreview, ImportResult
from app.domain.exceptions.errors import DuplicateImportError
from app.domain.services.calculations import calculate_total_cents, is_valid_sale_date
from app.domain.value_objects.sale_status import normalize_status
from app.infrastructure.database.models import FactProductionModel, FactSaleModel
from app.infrastructure.repositories.implementations import DimensionRepository, ImportRepository


def compute_file_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _detect_separator(content: str) -> str:
    sample = content[:4096]
    if ";" in sample and "," not in sample:
        return ";"
    return ","


def _parse_brl_money(value) -> int:
    if pd.isna(value) or value is None:
        return 0
    s = str(value).strip().replace("R$", "").replace(" ", "")
    s = s.replace(".", "").replace(",", ".")
    try:
        return int(round(float(s) * 100))
    except (ValueError, TypeError):
        raise ValueError(f"Valor monetário inválido: {value}")


def _parse_date(value) -> date:
    if pd.isna(value) or value is None:
        raise ValueError("Data ausente")
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    s = str(value).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            d = datetime.strptime(s, fmt).date()
            if not is_valid_sale_date(d):
                raise ValueError(f"Data fora do intervalo válido: {s}")
            return d
        except ValueError:
            continue
    raise ValueError(f"Data inválida: {s}")


def _parse_int(value, field_name: str) -> int:
    if pd.isna(value) or value is None:
        raise ValueError(f"{field_name} ausente")
    try:
        v = int(float(str(value).strip()))
        if v < 0:
            raise ValueError(f"{field_name} não pode ser negativo: {v}")
        return v
    except (ValueError, TypeError):
        raise ValueError(f"{field_name} inválido: {value}")


def _generate_item_id(order_id: str, product: str, position: int) -> str:
    raw = f"{order_id}|{product.strip().lower()}|{position}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


SALES_REQUIRED = ["data_venda", "id_pedido", "produto", "categoria", "quantidade", "valor_unitario", "status"]
SALES_OPTIONAL = ["id_item", "desconto", "canal", "forma_pagamento", "custo_unitario"]

PRODUCTION_REQUIRED = ["data", "produto", "categoria", "quantidade_produzida", "quantidade_vendida", "quantidade_descartada"]


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [re.sub(r"\s+", "_", str(c).strip().lower()) for c in df.columns]
    return df


def read_upload(content: bytes, filename: str) -> pd.DataFrame:
    lower = filename.lower()
    if lower.endswith(".csv"):
        text = content.decode("utf-8-sig")
        sep = _detect_separator(text)
        return pd.read_csv(io.StringIO(text), sep=sep, dtype=str, keep_default_na=False)
    elif lower.endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(content), dtype=str, keep_default_na=False)
    else:
        raise ValueError(f"Formato não suportado: {filename}")


def preview_sales(df: pd.DataFrame) -> ImportPreview:
    df = _normalize_columns(df)
    missing = [c for c in SALES_REQUIRED if c not in df.columns]
    if missing:
        return ImportPreview(
            total_rows=len(df),
            valid_rows=0,
            invalid_rows=len(df),
            sample_valid=[],
            sample_invalid=df.head(5).to_dict("records"),
            errors=[{"row": 0, "field": ",".join(missing), "message": f"Colunas obrigatórias ausentes: {missing}"}],
        )

    valid, invalid, errors = [], [], []
    for idx, (_, row) in enumerate(df.iterrows()):
        row_errors = _validate_sales_row(row, idx + 2)
        if row_errors:
            invalid.append(row.to_dict())
            errors.extend(row_errors)
        else:
            valid.append(row.to_dict())

    return ImportPreview(
        total_rows=len(df),
        valid_rows=len(valid),
        invalid_rows=len(invalid),
        sample_valid=valid[:5],
        sample_invalid=invalid[:5],
        errors=errors[:50],
    )


def _validate_sales_row(row: pd.Series, row_num: int) -> list[dict]:
    errs = []
    for field in SALES_REQUIRED:
        val = row.get(field, "")
        if pd.isna(val) or str(val).strip() == "":
            errs.append({"row": row_num, "field": field, "message": f"Campo obrigatório '{field}' ausente"})

    if not errs:
        try:
            _parse_date(row["data_venda"])
        except ValueError as e:
            errs.append({"row": row_num, "field": "data_venda", "message": str(e)})
        try:
            _parse_int(row["quantidade"], "quantidade")
        except ValueError as e:
            errs.append({"row": row_num, "field": "quantidade", "message": str(e)})
        try:
            _parse_brl_money(row["valor_unitario"])
        except ValueError as e:
            errs.append({"row": row_num, "field": "valor_unitario", "message": str(e)})
        try:
            normalize_status(str(row["status"]))
        except Exception as e:
            errs.append({"row": row_num, "field": "status", "message": str(e)})
    return errs


def confirm_sales_import(
    df: pd.DataFrame,
    import_repo: ImportRepository,
    dim_repo: DimensionRepository,
    filename: str,
    file_hash: str,
) -> ImportResult:
    dup = import_repo.check_duplicate(file_hash)
    if dup:
        raise DuplicateImportError(f"Arquivo já importado no lote #{dup.id}")

    df = _normalize_columns(df)
    batch = import_repo.create_batch("sales", filename, file_hash, len(df))
    accepted, rejected = 0, 0
    errors_list: list[ImportErrorRow] = []

    try:
        for idx, (_, row) in enumerate(df.iterrows()):
            row_num = idx + 2
            try:
                d = _parse_date(row["data_venda"])
                qty = _parse_int(row["quantidade"], "quantidade")
                unit_price = _parse_brl_money(row["valor_unitario"])
                discount = _parse_brl_money(row.get("desconto", 0)) if pd.notna(row.get("desconto")) else 0
                cost = _parse_brl_money(row["custo_unitario"]) if pd.notna(row.get("custo_unitario")) and str(row.get("custo_unitario", "")).strip() else None
                status = normalize_status(str(row["status"]))
                product = dim_repo.get_or_create_product(str(row["produto"]), str(row["categoria"]))
                date_dim = dim_repo.get_or_create_date(d)
                channel = dim_repo.get_or_create_channel(str(row["canal"])) if pd.notna(row.get("canal")) and str(row.get("canal", "")).strip() else None

                item_id = str(row.get("id_item", "")).strip()
                if not item_id:
                    item_id = _generate_item_id(str(row["id_pedido"]), str(row["produto"]), idx)

                total = calculate_total_cents(qty, unit_price, discount)

                sale = FactSaleModel(
                    external_order_id=str(row["id_pedido"]).strip(),
                    external_item_id=item_id,
                    product_id=product.id,
                    date_id=date_dim.id,
                    channel_id=channel.id if channel else None,
                    payment_method=str(row["forma_pagamento"]).strip() if pd.notna(row.get("forma_pagamento")) else None,
                    quantity=qty,
                    unit_price_cents=unit_price,
                    discount_cents=discount,
                    unit_cost_cents=cost,
                    total_cents=total,
                    status=status.value,
                    import_batch_id=batch.id,
                )
                import_repo.session.add(sale)
                accepted += 1
            except Exception as e:
                rejected += 1
                err = ImportErrorRow(row_number=row_num, field_name=None, error_message=str(e), raw_data=str(row.to_dict()))
                errors_list.append(err)
                import_repo.add_error(batch.id, row_num, None, str(e), str(row.to_dict()))

        import_repo.finalize_batch(batch, accepted, rejected)
        import_repo.session.commit()
    except Exception:
        import_repo.session.rollback()
        import_repo.finalize_batch(batch, 0, len(df), "failed")
        import_repo.session.commit()
        raise

    return ImportResult(
        batch_id=batch.id,
        status=batch.status,
        total_rows=len(df),
        accepted_rows=accepted,
        rejected_rows=rejected,
        errors=errors_list,
    )


def preview_production(df: pd.DataFrame) -> ImportPreview:
    df = _normalize_columns(df)
    missing = [c for c in PRODUCTION_REQUIRED if c not in df.columns]
    if missing:
        return ImportPreview(
            total_rows=len(df),
            valid_rows=0,
            invalid_rows=len(df),
            sample_valid=[],
            sample_invalid=df.head(5).to_dict("records"),
            errors=[{"row": 0, "field": ",".join(missing), "message": f"Colunas obrigatórias ausentes: {missing}"}],
        )

    valid, invalid, errors = [], [], []
    for idx, (_, row) in enumerate(df.iterrows()):
        row_errors = _validate_production_row(row, idx + 2)
        if row_errors:
            invalid.append(row.to_dict())
            errors.extend(row_errors)
        else:
            valid.append(row.to_dict())

    return ImportPreview(
        total_rows=len(df),
        valid_rows=len(valid),
        invalid_rows=len(invalid),
        sample_valid=valid[:5],
        sample_invalid=invalid[:5],
        errors=errors[:50],
    )


def _validate_production_row(row: pd.Series, row_num: int) -> list[dict]:
    errs = []
    for field in PRODUCTION_REQUIRED:
        val = row.get(field, "")
        if pd.isna(val) or str(val).strip() == "":
            errs.append({"row": row_num, "field": field, "message": f"Campo obrigatório '{field}' ausente"})
    if not errs:
        try:
            _parse_date(row["data"])
        except ValueError as e:
            errs.append({"row": row_num, "field": "data", "message": str(e)})
        for f in ["quantidade_produzida", "quantidade_vendida", "quantidade_descartada"]:
            try:
                _parse_int(row[f], f)
            except ValueError as e:
                errs.append({"row": row_num, "field": f, "message": str(e)})
    return errs


def confirm_production_import(
    df: pd.DataFrame,
    import_repo: ImportRepository,
    dim_repo: DimensionRepository,
    filename: str,
    file_hash: str,
) -> ImportResult:
    dup = import_repo.check_duplicate(file_hash)
    if dup:
        raise DuplicateImportError(f"Arquivo já importado no lote #{dup.id}")

    df = _normalize_columns(df)
    batch = import_repo.create_batch("production", filename, file_hash, len(df))
    accepted, rejected = 0, 0
    errors_list: list[ImportErrorRow] = []

    try:
        for idx, (_, row) in enumerate(df.iterrows()):
            row_num = idx + 2
            try:
                d = _parse_date(row["data"])
                produced = _parse_int(row["quantidade_produzida"], "quantidade_produzida")
                sold = _parse_int(row["quantidade_vendida"], "quantidade_vendida")
                discarded = _parse_int(row["quantidade_descartada"], "quantidade_descartada")
                product = dim_repo.get_or_create_product(str(row["produto"]), str(row["categoria"]))
                date_dim = dim_repo.get_or_create_date(d)

                rec = FactProductionModel(
                    product_id=product.id,
                    date_id=date_dim.id,
                    produced_quantity=produced,
                    sold_quantity=sold,
                    discarded_quantity=discarded,
                    discard_reason=str(row.get("motivo_descarte", "")).strip() or None,
                    import_batch_id=batch.id,
                )
                import_repo.session.add(rec)
                accepted += 1
            except Exception as e:
                rejected += 1
                err = ImportErrorRow(row_number=row_num, field_name=None, error_message=str(e), raw_data=str(row.to_dict()))
                errors_list.append(err)
                import_repo.add_error(batch.id, row_num, None, str(e), str(row.to_dict()))

        import_repo.finalize_batch(batch, accepted, rejected)
        import_repo.session.commit()
    except Exception:
        import_repo.session.rollback()
        import_repo.finalize_batch(batch, 0, len(df), "failed")
        import_repo.session.commit()
        raise

    return ImportResult(
        batch_id=batch.id,
        status=batch.status,
        total_rows=len(df),
        accepted_rows=accepted,
        rejected_rows=rejected,
        errors=errors_list,
    )
