"""Unit tests for domain calculations."""

from __future__ import annotations

from datetime import date

import pytest
from app.domain.exceptions.errors import InvalidSaleStatusError, NegativeValueError
from app.domain.services.calculations import (
    calculate_growth,
    calculate_margin,
    calculate_ticket_medio,
    calculate_total_cents,
    calculate_waste_rate,
    is_valid_sale_date,
)
from app.domain.value_objects.money import Money
from app.domain.value_objects.sale_status import SaleStatus, normalize_status


class TestCalculations:
    def test_calculate_total_cents_basic(self):
        assert calculate_total_cents(2, 1000, 200) == 1800

    def test_calculate_total_cents_no_discount(self):
        assert calculate_total_cents(3, 500, 0) == 1500

    def test_calculate_total_cents_discount_capped(self):
        assert calculate_total_cents(1, 500, 1000) == 0

    def test_calculate_ticket_medio_normal(self):
        assert calculate_ticket_medio(10000, 5) == 2000

    def test_calculate_ticket_medio_zero_pedidos(self):
        assert calculate_ticket_medio(10000, 0) == 0

    def test_calculate_margin_positive(self):
        margem, perc = calculate_margin(10000, 6000)
        assert margem == 4000
        assert perc == 40.0

    def test_calculate_margin_zero_faturamento(self):
        margem, perc = calculate_margin(0, 0)
        assert margem == 0
        assert perc == 0.0

    def test_calculate_waste_rate_normal(self):
        assert calculate_waste_rate(10, 100) == 10.0

    def test_calculate_waste_rate_zero_produced(self):
        assert calculate_waste_rate(10, 0) == 0.0

    def test_calculate_growth_positive(self):
        result = calculate_growth(150, 100)
        assert result == 50.0

    def test_calculate_growth_zero_previous(self):
        assert calculate_growth(100, 0) is None

    def test_calculate_growth_both_zero(self):
        assert calculate_growth(0, 0) is None

    def test_is_valid_sale_date_valid(self):
        assert is_valid_sale_date(date(2025, 1, 15)) is True

    def test_is_valid_sale_date_too_old(self):
        assert is_valid_sale_date(date(1999, 1, 1)) is False

    def test_is_valid_sale_date_future(self):
        assert is_valid_sale_date(date(2030, 1, 1)) is False


class TestMoney:
    def test_money_creation(self):
        m = Money(1000)
        assert m.cents == 1000

    def test_money_negative_raises(self):
        with pytest.raises(NegativeValueError):
            Money(-100)

    def test_money_from_brl_string(self):
        m = Money.from_brl_string("R$ 10,50")
        assert m.cents == 1050

    def test_money_add(self):
        assert (Money(500) + Money(300)).cents == 800

    def test_money_sub(self):
        assert (Money(1000) - Money(300)).cents == 700

    def test_money_sub_negative_raises(self):
        with pytest.raises(NegativeValueError):
            Money(300) - Money(1000)

    def test_money_format_brl(self):
        assert Money(1234).format_brl() == "R$ 12,34"


class TestSaleStatus:
    def test_normalize_status_completed(self):
        assert normalize_status("Concluído") == SaleStatus.COMPLETED
        assert normalize_status("concluido") == SaleStatus.COMPLETED
        assert normalize_status("Finalizado") == SaleStatus.COMPLETED

    def test_normalize_status_cancelled(self):
        assert normalize_status("Cancelado") == SaleStatus.CANCELLED
        assert normalize_status("cancelado") == SaleStatus.CANCELLED

    def test_normalize_status_pending(self):
        assert normalize_status("Pendente") == SaleStatus.PENDING

    def test_normalize_status_invalid(self):
        with pytest.raises(InvalidSaleStatusError):
            normalize_status("Inválido")


class TestDomainEntities:
    """Test domain entity dataclasses."""

    def test_product_entity(self):
        from app.domain.entities.models import Product

        p = Product(id=1, name="Bolo", normalized_name="bolo", category="Bolos")
        assert p.id == 1 and p.name == "Bolo" and p.category == "Bolos"

    def test_sale_record_entity(self):
        from app.domain.entities.models import SaleRecord

        s = SaleRecord(
            id=1,
            external_order_id="PED-001",
            external_item_id="",
            product_id=1,
            date_id=1,
            channel_id=None,
            payment_method=None,
            quantity=2,
            unit_price_cents=1000,
            discount_cents=0,
            unit_cost_cents=500,
            total_cents=1500,
            status="Concluído",
            import_batch_id=1,
        )
        assert s.quantity == 2 and s.total_cents == 1500

    def test_production_record_entity(self):
        from app.domain.entities.models import ProductionRecord

        r = ProductionRecord(
            id=1,
            product_id=1,
            date_id=1,
            produced_quantity=50,
            sold_quantity=40,
            discarded_quantity=5,
            discard_reason=None,
            import_batch_id=1,
        )
        assert r.produced_quantity == 50 and r.discarded_quantity == 5

    def test_channel_entity(self):
        from app.domain.entities.models import Channel

        c = Channel(id=1, name="Balcao", normalized_name="balcao")
        assert c.id == 1

    def test_import_batch_entity(self):
        from datetime import datetime

        from app.domain.entities.models import ImportBatch

        b = ImportBatch(
            id=1,
            import_type="sales",
            original_filename="vendas.csv",
            file_hash="abc123",
            status="completed",
            total_rows=100,
            accepted_rows=98,
            rejected_rows=2,
            error_message=None,
            created_at=datetime.now(),
            completed_at=datetime.now(),
        )
        assert b.import_type == "sales"

    def test_import_error_detail_entity(self):
        from app.domain.entities.models import ImportErrorDetail

        e = ImportErrorDetail(
            id=1,
            import_batch_id=1,
            row_number=5,
            field_name="data_venda",
            error_message="Data inválida",
            raw_data="erroneo|data",
        )
        assert e.row_number == 5
