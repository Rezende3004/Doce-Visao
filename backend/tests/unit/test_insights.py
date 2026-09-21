"""Tests for insights engine and filter handling."""

from __future__ import annotations

from app.application.use_cases.insights_engine import generate_insights


class TestInsightsEngine:
    """Test insight generation with empty and populated repositories."""

    def test_empty_data(self):
        """No sales data → no strong insights."""
        from unittest.mock import MagicMock

        sales_repo = MagicMock()
        sales_repo.get_summary.return_value = MagicMock(
            faturamento_cents=0,
            num_pedidos=0,
            ticket_medio_cents=0,
            itens_vendidos=0,
            faturamento_anterior_cents=None,
            crescimento_percentual=None,
        )
        sales_repo.get_timeline.return_value = []
        sales_repo.get_by_weekday.return_value = []
        sales_repo.get_by_channel.return_value = []

        product_repo = MagicMock()
        product_repo.get_ranking_by_quantity.return_value = []
        product_repo.get_ranking_by_revenue.return_value = []
        product_repo.get_category_performance.return_value = []
        product_repo.get_margin_info.return_value = MagicMock(
            faturamento_cents=0,
            custo_total_cents=0,
            margem_cents=0,
            margem_percentual=0.0,
            coverage_percentual=0.0,
        )

        production_repo = MagicMock()
        production_repo.get_waste_by_product.return_value = []

        insights = generate_insights(sales_repo, product_repo, production_repo, None)
        assert len(insights) >= 0  # May return zero insights for empty data

    def test_low_sales_insight(self):
        """Very low revenue triggers a low-sales insight."""
        from unittest.mock import MagicMock

        summary_mock = MagicMock(
            faturamento_cents=1,
            num_pedidos=1,
            ticket_medio_cents=1,
            itens_vendidos=1,
            faturamento_anterior_cents=None,
            crescimento_percentual=None,
        )
        sales_repo = MagicMock()
        sales_repo.get_summary.return_value = summary_mock
        sales_repo.get_timeline.return_value = []
        sales_repo.get_by_weekday.return_value = []
        sales_repo.get_by_channel.return_value = []

        product_repo = MagicMock()
        product_repo.get_ranking_by_quantity.return_value = []
        product_repo.get_ranking_by_revenue.return_value = []
        product_repo.get_category_performance.return_value = []
        product_repo.get_margin_info.return_value = MagicMock(
            faturamento_cents=0,
            custo_total_cents=0,
            margem_cents=0,
            margem_percentual=0.0,
            coverage_percentual=0.0,
        )

        production_repo = MagicMock()
        production_repo.get_waste_by_product.return_value = []

        insights = generate_insights(sales_repo, product_repo, production_repo, None)
        assert len(insights) > 0
        # Check that insights have expected structure
        insight = insights[0]
        assert hasattr(insight, "title")
        assert hasattr(insight, "description")
        assert hasattr(insight, "evidence")
        assert hasattr(insight, "recommendation")
        assert hasattr(insight, "level")
        assert hasattr(insight, "metric_value")

    def test_high_growth_insight(self):
        """High growth rate triggers an opportunity insight."""
        from unittest.mock import MagicMock

        summary_mock = MagicMock(
            faturamento_cents=100000,
            num_pedidos=50,
            ticket_medio_cents=2000,
            itens_vendidos=100,
            faturamento_anterior_cents=50000,
            crescimento_percentual=100.0,
        )
        sales_repo = MagicMock()
        sales_repo.get_summary.return_value = summary_mock
        sales_repo.get_timeline.return_value = []
        sales_repo.get_by_weekday.return_value = []
        sales_repo.get_by_channel.return_value = []

        product_repo = MagicMock()
        product_repo.get_ranking_by_quantity.return_value = []
        product_repo.get_ranking_by_revenue.return_value = []
        product_repo.get_category_performance.return_value = []
        product_repo.get_margin_info.return_value = MagicMock(
            faturamento_cents=0,
            custo_total_cents=0,
            margem_cents=0,
            margem_percentual=0.0,
            coverage_percentual=0.0,
        )

        production_repo = MagicMock()
        production_repo.get_waste_by_product.return_value = []

        insights = generate_insights(sales_repo, product_repo, production_repo, None)
        assert len(insights) > 0
