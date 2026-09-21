"""Integration tests for file import operations."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest
from app.domain.exceptions.errors import DuplicateImportError
from app.infrastructure.database.connection import Base
from app.infrastructure.importers.file_importer import (
    _detect_separator,
    _generate_item_id,
    _normalize_columns,
    _parse_brl_money,
    _parse_date,
    _parse_int,
    compute_file_hash,
    confirm_production_import,
    confirm_sales_import,
    preview_production,
    preview_sales,
    read_upload,
)
from app.infrastructure.repositories.implementations import DimensionRepository, ImportRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()


class TestFileParsing:
    def test_compute_hash(self):
        h = compute_file_hash(b"test content")
        assert len(h) == 64

    def test_parse_brl_money_comma(self):
        assert _parse_brl_money("10,50") == 1050

    def test_parse_brl_money_with_dot_thousands(self):
        assert _parse_brl_money("1.234,56") == 123456

    def test_parse_brl_money_with_r_prefix(self):
        assert _parse_brl_money("R$ 50,00") == 5000

    def test_parse_brl_money_zero(self):
        assert _parse_brl_money("0,00") == 0

    def test_parse_brl_money_invalid(self):
        with pytest.raises(ValueError):
            _parse_brl_money("abc")

    def test_parse_date_br_format(self):
        assert _parse_date("15/03/2025") == date(2025, 3, 15)

    def test_parse_date_iso_format(self):
        assert _parse_date("2025-03-15") == date(2025, 3, 15)

    def test_parse_date_invalid(self):
        with pytest.raises(ValueError):
            _parse_date("32/13/2025")

    def test_parse_date_future(self):
        with pytest.raises(ValueError):
            _parse_date("01/01/2030")

    def test_parse_int_valid(self):
        assert _parse_int("5", "qty") == 5

    def test_parse_int_negative(self):
        with pytest.raises(ValueError):
            _parse_int("-1", "qty")

    def test_parse_int_invalid(self):
        with pytest.raises(ValueError):
            _parse_int("abc", "qty")

    def test_generate_item_id_deterministic(self):
        id1 = _generate_item_id("PED-1", "Cocada Branca", 1)
        id2 = _generate_item_id("PED-1", "Cocada Branca", 1)
        assert id1 == id2

    def test_generate_item_id_different(self):
        id1 = _generate_item_id("PED-1", "Cocada Branca", 1)
        id2 = _generate_item_id("PED-1", "Cocada Branca", 2)
        assert id1 != id2

    def test_detect_separator_semicolon(self):
        assert _detect_separator("a;b;c\n1;2;3") == ";"

    def test_detect_separator_comma(self):
        assert _detect_separator("a,b,c\n1,2,3") == ","

    def test_normalize_columns(self):
        df = pd.DataFrame(columns=["Data Venda", "ID  Pedido", "Produto"])
        result = _normalize_columns(df)
        assert list(result.columns) == ["data_venda", "id_pedido", "produto"]


class TestReadUpload:
    def test_read_csv_comma(self):
        content = b"data_venda,id_pedido,produto\n01/01/2025,PED-1,Cocada Branca\n"
        df = read_upload(content, "test.csv")
        assert len(df) == 1
        assert df.iloc[0]["data_venda"] == "01/01/2025"

    def test_read_csv_semicolon(self):
        content = b"data_venda;id_pedido;produto\n01/01/2025;PED-1;Cocada Branca\n"
        df = read_upload(content, "test.csv")
        assert len(df) == 1

    def test_read_unsupported_format(self):
        with pytest.raises(ValueError):
            read_upload(b"test", "test.json")


class TestPreviewSales:
    def test_preview_valid(self):
        df = pd.DataFrame(
            {
                "data_venda": ["01/01/2025"],
                "id_pedido": ["PED-1"],
                "produto": ["Cocada Branca"],
                "categoria": ["Doces de Coco"],
                "quantidade": ["2"],
                "valor_unitario": ["50,00"],
                "status": ["Concluído"],
            }
        )
        preview = preview_sales(df)
        assert preview.total_rows == 1
        assert preview.valid_rows == 1
        assert preview.invalid_rows == 0

    def test_preview_missing_columns(self):
        df = pd.DataFrame({"data_venda": ["01/01/2025"]})
        preview = preview_sales(df)
        assert preview.invalid_rows == 1
        assert len(preview.errors) > 0

    def test_preview_invalid_date(self):
        df = pd.DataFrame(
            {
                "data_venda": ["32/13/2025"],
                "id_pedido": ["PED-1"],
                "produto": ["Cocada Branca"],
                "categoria": ["Doces de Coco"],
                "quantidade": ["1"],
                "valor_unitario": ["10,00"],
                "status": ["Concluído"],
            }
        )
        preview = preview_sales(df)
        assert preview.invalid_rows == 1

    def test_preview_negative_quantity(self):
        df = pd.DataFrame(
            {
                "data_venda": ["01/01/2025"],
                "id_pedido": ["PED-1"],
                "produto": ["Cocada Branca"],
                "categoria": ["Doces de Coco"],
                "quantidade": ["-5"],
                "valor_unitario": ["10,00"],
                "status": ["Concluído"],
            }
        )
        preview = preview_sales(df)
        assert preview.invalid_rows == 1

    def test_preview_invalid_status(self):
        df = pd.DataFrame(
            {
                "data_venda": ["01/01/2025"],
                "id_pedido": ["PED-1"],
                "produto": ["Cocada Branca"],
                "categoria": ["Doces de Coco"],
                "quantidade": ["1"],
                "valor_unitario": ["10,00"],
                "status": ["Inválido"],
            }
        )
        preview = preview_sales(df)
        assert preview.invalid_rows == 1


class TestConfirmSalesImport:
    def test_rejects_product_outside_plant_catalog(self, db_session):
        import_repo = ImportRepository(db_session)
        dim_repo = DimensionRepository(db_session)
        df = pd.DataFrame(
            {
                "data_venda": ["01/01/2025"],
                "id_pedido": ["PED-VEG-1"],
                "produto": ["Bolo de Chocolate"],
                "categoria": ["Bolos"],
                "quantidade": ["1"],
                "valor_unitario": ["10,00"],
                "status": ["Concluído"],
            }
        )
        preview = preview_sales(df.copy())
        result = confirm_sales_import(df, import_repo, dim_repo, "other.csv", "hash_non_plant")
        assert preview.invalid_rows == 1
        assert result.accepted_rows == 0
        assert result.rejected_rows == 1
        assert dim_repo.list_products() == []

    def test_confirm_valid(self, db_session):
        import_repo = ImportRepository(db_session)
        dim_repo = DimensionRepository(db_session)
        df = pd.DataFrame(
            {
                "data_venda": ["01/01/2025"],
                "id_pedido": ["PED-1"],
                "produto": ["Cocada Branca"],
                "categoria": ["Doces de Coco"],
                "quantidade": ["2"],
                "valor_unitario": ["50,00"],
                "status": ["Concluído"],
            }
        )
        content = b"test"
        file_hash = compute_file_hash(content)
        result = confirm_sales_import(df, import_repo, dim_repo, "test.csv", file_hash)
        assert result.accepted_rows == 1
        assert result.rejected_rows == 0
        assert result.status == "completed"

    def test_confirm_with_optional_fields(self, db_session):
        import_repo = ImportRepository(db_session)
        dim_repo = DimensionRepository(db_session)
        df = pd.DataFrame(
            {
                "data_venda": ["15/03/2025"],
                "id_pedido": ["PED-2"],
                "id_item": ["ITEM-1"],
                "produto": ["Pau de Mamão"],
                "categoria": ["Doces de Frutas"],
                "quantidade": ["10"],
                "valor_unitario": ["5,00"],
                "desconto": ["2,00"],
                "canal": ["WhatsApp"],
                "forma_pagamento": ["PIX"],
                "custo_unitario": ["2,50"],
                "status": ["Concluído"],
            }
        )
        result = confirm_sales_import(df, import_repo, dim_repo, "test.csv", "hash2")
        assert result.accepted_rows == 1

    def test_confirm_duplicate(self, db_session):
        import_repo = ImportRepository(db_session)
        dim_repo = DimensionRepository(db_session)
        df = pd.DataFrame(
            {
                "data_venda": ["01/01/2025"],
                "id_pedido": ["PED-1"],
                "produto": ["Cocada Branca"],
                "categoria": ["Doces de Coco"],
                "quantidade": ["1"],
                "valor_unitario": ["10,00"],
                "status": ["Concluído"],
            }
        )
        confirm_sales_import(df, import_repo, dim_repo, "test.csv", "hash_dup")
        with pytest.raises(DuplicateImportError):
            confirm_sales_import(df, import_repo, dim_repo, "test.csv", "hash_dup")

    def test_confirm_mixed_valid_invalid(self, db_session):
        import_repo = ImportRepository(db_session)
        dim_repo = DimensionRepository(db_session)
        df = pd.DataFrame(
            {
                "data_venda": ["01/01/2025", "32/13/2025"],
                "id_pedido": ["PED-1", "PED-2"],
                "produto": ["Cocada Branca", "Cocada Branca"],
                "categoria": ["Doces de Coco", "Doces de Coco"],
                "quantidade": ["1", "1"],
                "valor_unitario": ["10,00", "10,00"],
                "status": ["Concluído", "Concluído"],
            }
        )
        result = confirm_sales_import(df, import_repo, dim_repo, "test.csv", "hash_mixed")
        assert result.accepted_rows == 1
        assert result.rejected_rows == 1


class TestPreviewProduction:
    def test_preview_valid(self):
        df = pd.DataFrame(
            {
                "data": ["01/01/2025"],
                "produto": ["Cocada Branca"],
                "categoria": ["Doces de Coco"],
                "quantidade_produzida": ["20"],
                "quantidade_vendida": ["15"],
                "quantidade_descartada": ["5"],
            }
        )
        preview = preview_production(df)
        assert preview.valid_rows == 1
        assert preview.invalid_rows == 0

    def test_preview_missing_columns(self):
        df = pd.DataFrame({"data": ["01/01/2025"]})
        preview = preview_production(df)
        assert preview.invalid_rows == 1


class TestConfirmProductionImport:
    def test_confirm_valid(self, db_session):
        import_repo = ImportRepository(db_session)
        dim_repo = DimensionRepository(db_session)
        df = pd.DataFrame(
            {
                "data": ["06/01/2025"],
                "produto": ["Cocada Branca"],
                "categoria": ["Doces de Coco"],
                "quantidade_produzida": ["20"],
                "quantidade_vendida": ["15"],
                "quantidade_descartada": ["5"],
            }
        )
        result = confirm_production_import(df, import_repo, dim_repo, "prod.csv", "hash_prod")
        assert result.accepted_rows == 1
        assert result.status == "completed"
