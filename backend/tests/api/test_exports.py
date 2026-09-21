"""Tests for export endpoint."""

from __future__ import annotations

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


class TestExports:
    """Test export routes."""

    def test_export_sales_template(self, client):
        response = client.get("/api/v1/exports/sales")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "attachment" in response.headers["content-disposition"]

    def test_export_sales_with_filter(self, client):
        response = client.get("/api/v1/exports/sales?start_date=2025-01-01&end_date=2025-12-31")
        assert response.status_code == 200
