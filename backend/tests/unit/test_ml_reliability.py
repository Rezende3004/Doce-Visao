"""Tests for ML module reliability — visual consistency, unit coherence, and confidence honesty."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from app.ml.trends.classification import classify_all_products_trends, classify_product_trend

PROJECT_ROOT = Path(__file__).resolve().parents[3]
HTML_DIR = PROJECT_ROOT / "frontend-html"


def _collect_sidebar_links(html_file: Path) -> list[str]:
    content = html_file.read_text(encoding="utf-8")
    sidebar_match = re.search(r'<ul class="menu">(.*?)</ul>', content, re.DOTALL)
    if not sidebar_match:
        return []
    return re.findall(r'href="([^"]*)"[^>]*>[^<]*Análise Inteligente', sidebar_match.group(1))


def test_no_duplicate_ml_links_in_html_sidebars():
    html_files = list(HTML_DIR.glob("**/*.html"))
    assert html_files, "No HTML files found"
    for f in html_files:
        links = _collect_sidebar_links(f)
        assert len(links) == 1, f"{f.name}: expected one 'Análise Inteligente' link, found {len(links)}"
        target = (f.parent / links[0]).resolve()
        assert target == HTML_DIR / "pages" / "ml.html", f"{f.name}: broken ML navigation link"


def test_streamlit_has_no_ml_page():
    streamlit_pages = list((PROJECT_ROOT / "frontend" / "pages").glob("*.py"))
    ml_pages = [p for p in streamlit_pages if "ml" in p.stem.lower() or "inteligente" in p.stem.lower()]
    assert len(ml_pages) == 0, f"Streamlit should not have an ML page, found: {ml_pages}"


def test_trend_result_includes_product_name():
    sales_data = [
        {"date": f"2025-01-{d:02d}", "product_id": 1, "product_name": "Bolo de Chocolate", "quantity": 10 + d}
        for d in range(1, 21)
    ]
    result = classify_product_trend(sales_data, product_id=1, min_periods=3, product_name="Bolo de Chocolate")
    assert result["success"] is True
    assert result.get("product_name") == "Bolo de Chocolate"


def test_all_products_trends_include_product_names():
    sales_data = []
    for pid, name in [(1, "Brigadeiro"), (2, "Beijinho")]:
        for d in range(1, 21):
            sales_data.append({"date": f"2025-01-{d:02d}", "product_id": pid, "product_name": name, "quantity": 5 + d})

    result = classify_all_products_trends(sales_data, min_periods=3)
    assert result["success"] is True
    for pid, trend in result["by_product"].items():
        if trend["success"]:
            assert "product_name" in trend, f"Product {pid} missing product_name"
            assert trend["product_name"] in ("Brigadeiro", "Beijinho")


def test_low_confidence_does_not_generate_recommendation():
    np.random.seed(42)
    sales_data = [
        {"date": f"2025-01-{d:02d}", "product_id": 1, "product_name": "Teste", "quantity": int(np.random.randint(1, 100))}
        for d in range(1, 21)
    ]
    result = classify_product_trend(sales_data, product_id=1, min_periods=3, product_name="Teste")
    if result["success"] and result["confidence"] == "baixa":
        assert result["recommendation"] is None
        assert "insuficientes" in result["description"].lower()


def test_insufficient_data_returns_failure():
    sales_data = [
        {"date": "2025-01-01", "product_id": 1, "product_name": "Teste", "quantity": 10},
        {"date": "2025-01-02", "product_id": 1, "product_name": "Teste", "quantity": 20},
    ]
    result = classify_product_trend(sales_data, product_id=1, min_periods=7)
    assert result["success"] is False
    assert "insuficientes" in result["message"].lower() or "insuficientes" in result.get("trend", "").lower()


@pytest.mark.parametrize("direction,expected", [(1, "crescente"), (-1, "decrescente")])
def test_trend_detects_persistent_change_with_weekday_effect(direction, expected):
    dates = pd.date_range("2025-01-01", periods=84)
    sales = [
        {"date": str(day.date()), "product_id": 1, "quantity": 60 + direction * i // 2 + (12 if day.dayofweek >= 5 else 0)}
        for i, day in enumerate(dates)
    ]
    result = classify_product_trend(sales, 1)
    assert result["trend"] == expected
    assert result["confidence"] != "baixa"
    assert result["metrics"]["effect_ci_95_percent"][0] < result["metrics"]["effect_ci_95_percent"][1]


def test_weekday_pattern_without_growth_is_not_called_growing():
    dates = pd.date_range("2025-01-01", periods=84)
    sales = [
        {"date": str(day.date()), "product_id": 1, "quantity": 30 if day.dayofweek < 5 else 65}
        for day in dates
    ]
    result = classify_product_trend(sales, 1)
    assert result["trend"] == "estável"
    assert abs(result["metrics"]["effect_percent"]) < 1


def test_calendar_gaps_are_counted_as_zero_sales():
    dates = pd.date_range("2025-01-01", periods=56)
    sales = [
        {"date": str(day.date()), "product_id": 1, "quantity": 20}
        for i, day in enumerate(dates) if i % 2 == 0 or i == 55
    ]
    result = classify_product_trend(sales, 1)
    assert result["metrics"]["data_points"] == 56
    assert result["metrics"]["days_with_sales"] == len(sales)
    assert result["metrics"]["avg_sales"] < 20


def test_constant_sales_produce_finite_metrics():
    dates = pd.date_range("2025-01-01", periods=60)
    sales = [{"date": str(day.date()), "product_id": 1, "quantity": 10} for day in dates]
    result = classify_product_trend(sales, 1)
    assert result["trend"] == "estável"
    assert np.isfinite(result["metrics"]["r_squared"])
    assert result["metrics"]["effect_percent"] == 0


def test_forecast_units_consistent():
    from app.ml.forecasting.demand import forecast_demand

    timeline = [{"date": f"2025-{m:02d}-{d:02d}", "faturamento_cents": 50000 + d * 1000, "num_pedidos": 10 + d} for m in range(1, 4) for d in range(1, 28)]

    result = forecast_demand(timeline, days_to_forecast=7)
    if not result["success"]:
        pytest.skip("Forecast returned insufficient data")

    assert "metrics" in result
    metrics = result["metrics"]
    forecast_values = [f for f in result["forecast"] if not f["is_historical"]]

    for f in forecast_values:
        assert "predicted" in f
        assert "lower_bound" in f
        assert "upper_bound" in f
        assert f["lower_bound"] <= f["predicted"] <= f["upper_bound"]

    assert metrics["avg_predicted"] > 0
    assert metrics["max_predicted"] >= metrics["avg_predicted"]

    card_avg_reais = metrics["avg_predicted"] / 100
    card_max_reais = metrics["max_predicted"] / 100
    chart_avg_reais = np.mean([f["predicted"] for f in forecast_values]) / 100
    chart_max_reais = max(f["predicted"] for f in forecast_values) / 100

    assert abs(card_avg_reais - chart_avg_reais) < 0.01, f"Card avg ({card_avg_reais}) != chart avg ({chart_avg_reais})"
    assert abs(card_max_reais - chart_max_reais) < 0.01, f"Card max ({card_max_reais}) != chart max ({chart_max_reais})"
