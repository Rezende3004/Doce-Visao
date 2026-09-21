"""Integration tests for repositories."""

from __future__ import annotations

from datetime import date

import pytest
from app.infrastructure.database.connection import Base
from app.infrastructure.repositories.implementations import (
    DimensionRepository,
    ImportRepository,
    ProductRepository,
    SalesRepository,
)
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


class TestDimensionRepository:
    def test_create_product(self, db_session):
        repo = DimensionRepository(db_session)
        product = repo.get_or_create_product("Bolo de Chocolate", "Bolos")
        assert product.id is not None
        assert product.name == "Bolo de Chocolate"
        assert product.normalized_name == "bolo de chocolate"
        assert product.category == "Bolos"

    def test_get_existing_product(self, db_session):
        repo = DimensionRepository(db_session)
        p1 = repo.get_or_create_product("Bolo", "Bolos")
        p2 = repo.get_or_create_product("bolo", "Bolos")
        assert p1.id == p2.id

    def test_create_date(self, db_session):
        repo = DimensionRepository(db_session)
        d = date(2025, 3, 15)
        date_dim = repo.get_or_create_date(d)
        assert date_dim.full_date == d
        assert date_dim.day == 15
        assert date_dim.month == 3
        assert date_dim.year == 2025
        assert date_dim.weekday_name == "Sábado"
        assert date_dim.is_weekend is True

    def test_get_existing_date(self, db_session):
        repo = DimensionRepository(db_session)
        d = date(2025, 1, 1)
        d1 = repo.get_or_create_date(d)
        d2 = repo.get_or_create_date(d)
        assert d1.id == d2.id


class TestImportRepository:
    def test_create_batch(self, db_session):
        repo = ImportRepository(db_session)
        batch = repo.create_batch("sales", "test.csv", "abc123", 100)
        assert batch.id is not None
        assert batch.status == "processing"
        assert batch.total_rows == 100

    def test_check_duplicate(self, db_session):
        repo = ImportRepository(db_session)
        repo.create_batch("sales", "test.csv", "hash123", 50)
        db_session.commit()
        dup = repo.check_duplicate("hash123")
        assert dup is not None
        assert dup.file_hash == "hash123"

    def test_no_duplicate(self, db_session):
        repo = ImportRepository(db_session)
        assert repo.check_duplicate("nonexistent") is None


class TestSalesRepository:
    def test_get_summary_empty(self, db_session):
        repo = SalesRepository(db_session)
        summary = repo.get_summary(None)
        assert summary.faturamento_cents == 0
        assert summary.num_pedidos == 0
        assert summary.ticket_medio_cents == 0

    def test_get_timeline_empty(self, db_session):
        repo = SalesRepository(db_session)
        assert repo.get_timeline(None) == []

    def test_get_by_weekday_empty(self, db_session):
        repo = SalesRepository(db_session)
        assert repo.get_by_weekday(None) == []


class TestProductRepository:
    def test_get_ranking_empty(self, db_session):
        repo = ProductRepository(db_session)
        assert repo.get_ranking_by_quantity(None) == []
        assert repo.get_ranking_by_revenue(None) == []

    def test_get_category_performance_empty(self, db_session):
        repo = ProductRepository(db_session)
        assert repo.get_category_performance(None) == []

    def test_get_margin_empty(self, db_session):
        repo = ProductRepository(db_session)
        margin = repo.get_margin_info(None)
        assert margin.faturamento_cents == 0
        assert margin.coverage_percentual == 0.0
