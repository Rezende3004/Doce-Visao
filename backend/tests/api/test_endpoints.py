"""API tests."""

from __future__ import annotations

import pytest
from app.infrastructure.database import connection
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(autouse=True, scope="module")
def isolated_database(tmp_path_factory):
    """Keep API tests independent from the local development database."""
    db_path = tmp_path_factory.mktemp("api") / "test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    connection.Base.metadata.create_all(engine)
    original_session_factory = connection.SessionLocal
    connection.SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    yield
    connection.SessionLocal = original_session_factory
    engine.dispose()


@pytest.fixture
def client():
    return TestClient(app)


class TestHealth:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestImports:
    def test_sales_template(self, client):
        response = client.get("/api/v1/imports/templates/sales")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    def test_production_template(self, client):
        response = client.get("/api/v1/imports/templates/production")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    def test_list_imports_returns_list(self, client):
        response = client.get("/api/v1/imports")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestDashboard:
    def test_summary_rejects_incomplete_date_range(self, client):
        response = client.get("/api/v1/dashboard/summary?start_date=2025-01-01")
        assert response.status_code == 422

    def test_summary_empty(self, client):
        response = client.get("/api/v1/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["faturamento_cents"] == 0
        assert data["num_pedidos"] == 0

    def test_summary_with_filters(self, client):
        response = client.get("/api/v1/dashboard/summary?start_date=2025-01-01&end_date=2025-12-31")
        assert response.status_code == 200


class TestSales:
    def test_timeline_empty(self, client):
        response = client.get("/api/v1/sales/timeline")
        assert response.status_code == 200
        assert response.json() == []

    def test_by_weekday_empty(self, client):
        response = client.get("/api/v1/sales/by-weekday")
        assert response.status_code == 200
        assert response.json() == []

    def test_by_channel_empty(self, client):
        response = client.get("/api/v1/sales/by-channel")
        assert response.status_code == 200
        assert response.json() == []


class TestProducts:
    def test_ranking_empty(self, client):
        response = client.get("/api/v1/products/ranking")
        assert response.status_code == 200
        assert response.json() == []

    def test_category_performance_empty(self, client):
        response = client.get("/api/v1/products/categories/performance")
        assert response.status_code == 200
        assert response.json() == []

    def test_margin_empty(self, client):
        response = client.get("/api/v1/products/margin")
        assert response.status_code == 200
        data = response.json()
        assert data["faturamento_cents"] == 0

    def test_filter_options_empty(self, client):
        response = client.get("/api/v1/filters/options")
        assert response.status_code == 200
        data = response.json()
        assert data["categories"] == []
        assert data["products"] == []
        assert data["channels"] == []


class TestProduction:
    def test_waste_empty(self, client):
        response = client.get("/api/v1/production/waste")
        assert response.status_code == 200
        assert response.json() == []


class TestInsights:
    def test_insights_empty(self, client):
        response = client.get("/api/v1/insights")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["title"] == "Sem dados de vendas"


class TestExports:
    def test_export_sales_empty(self, client):
        response = client.get("/api/v1/exports/sales")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]


class TestImportUpload:
    def test_sales_preview_valid(self, client):
        csv_content = (
            b"data_venda;id_pedido;produto;categoria;quantidade;valor_unitario;status\n"
            b"01/01/2025;PED-1;Cocada Branca;Doces de Coco;1;50,00;Concluido\n"
        )
        response = client.post(
            "/api/v1/imports/sales/preview",
            files={"file": ("test.csv", csv_content, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_rows"] >= 1

    def test_sales_confirm_valid(self, client):
        import time

        ts = int(time.time() * 1000)
        csv = f"data_venda;id_pedido;produto;categoria;quantidade;valor_unitario;status\n01/01/2025;PED-{ts};Cocada Branca;Doces de Coco;1;50,00;Concluido\n"
        response = client.post(
            "/api/v1/imports/sales/confirm",
            files={"file": ("test_confirm.csv", csv.encode(), "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["batch_id"] > 0

    def test_production_preview_valid(self, client):
        csv_content = b"data;produto;categoria;quantidade_produzida;quantidade_vendida;quantidade_descartada\n06/01/2025;Cocada Branca;Doces de Coco;20;15;5\n"
        response = client.post(
            "/api/v1/imports/production/preview",
            files={"file": ("prod.csv", csv_content, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid_rows"] == 1

    def test_upload_invalid_extension(self, client):
        response = client.post(
            "/api/v1/imports/sales/preview",
            files={"file": ("test.json", b"{}", "application/json")},
        )
        assert response.status_code == 400

    def test_list_imports_after_confirm(self, client):
        import time

        ts = int(time.time() * 1000)
        csv = f"data_venda;id_pedido;produto;categoria;quantidade;valor_unitario;status\n01/01/2025;PED-{ts};Cocada Branca;Doces de Coco;1;50,00;Concluido\n"
        client.post(
            "/api/v1/imports/sales/confirm",
            files={"file": ("list_test.csv", csv.encode(), "text/csv")},
        )
        response = client.get("/api/v1/imports")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_import_by_id(self, client):
        import time

        ts = int(time.time() * 1000)
        csv = f"data_venda;id_pedido;produto;categoria;quantidade;valor_unitario;status\n01/01/2025;PED-{ts};Cocada Branca;Doces de Coco;1;50,00;Concluido\n"
        confirm = client.post(
            "/api/v1/imports/sales/confirm",
            files={"file": ("by_id.csv", csv.encode(), "text/csv")},
        )
        batch_id = confirm.json()["batch_id"]
        response = client.get(f"/api/v1/imports/{batch_id}")
        assert response.status_code == 200
        assert response.json()["id"] == batch_id

    def test_get_import_not_found(self, client):
        response = client.get("/api/v1/imports/99999")
        assert response.status_code == 404
