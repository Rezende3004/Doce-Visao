"""Trend classification with calendar time and weekday adjustment."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import statsmodels.api as sm

logger = logging.getLogger(__name__)


def classify_product_trend(
    sales_data: list[dict],
    product_id: int,
    min_periods: int = 7,
    product_name: str | None = None,
) -> dict:
    """
    Classify sales trend for a specific product.

    Args:
        sales_data: List of sales records
        product_id: Product to analyze
        min_periods: Minimum data points required

    Returns:
        Dict with trend classification and metrics
    """
    product_sales = [s for s in sales_data if s.get("product_id") == product_id]
    if len(product_sales) < min_periods:
        return {
            "success": False,
            "message": f"Dados insuficientes (mínimo {min_periods} períodos)",
            "trend": "insufficient_data",
        }

    try:
        df = pd.DataFrame(product_sales)
        df["date"] = pd.to_datetime(df["date"], errors="raise").dt.normalize()
        df["quantity"] = pd.to_numeric(df["quantity"], errors="raise")
        if df["quantity"].isna().any() or (df["quantity"] < 0).any():
            raise ValueError("Quantidades inválidas na série de vendas")
        observed = df.groupby("date")["quantity"].sum().sort_index()
        dates = pd.date_range(observed.index.min(), observed.index.max(), freq="D")
        y = observed.reindex(dates, fill_value=0).to_numpy(dtype=float)
        n = len(y)
        if len(observed) < min_periods or n < max(14, min_periods):
            return {
                "success": False,
                "message": f"Dados insuficientes: são necessários {min_periods} dias com vendas e ao menos 14 dias corridos",
                "trend": "insufficient_data",
            }
        if np.ptp(y) == 0:
            value = float(y[0])
            result = {
                "success": True,
                "product_id": product_id,
                "trend": "estável" if value > 0 else "inconclusiva",
                "confidence": ("alta" if n >= 56 else "média") if value > 0 else "baixa",
                "metrics": {
                    "slope": 0.0,
                    "r_squared": 1.0,
                    "avg_sales": value,
                    "recent_avg": value,
                    "previous_avg": value,
                    "variation_percent": 0.0,
                    "data_points": n,
                    "days_with_sales": len(observed),
                    "coverage_percent": len(observed) / n * 100,
                    "p_value": 1.0,
                    "effect_percent": 0.0,
                    "effect_ci_95_percent": [0.0, 0.0],
                    "comparison_window_days": min(28, n // 2),
                },
                "description": (
                    f"Vendas constantes em {n} dias: {value:.1f} unidades/dia."
                    if value > 0 else "Sem unidades vendidas no período; não há tendência de demanda para classificar."
                ),
                "recommendation": None,
            }
            if product_name:
                result["product_name"] = product_name
            return result
        # Weekday controls separate a persistent trend from weekly demand cycles.
        weekdays = np.eye(7, dtype=float)[dates.dayofweek][:, 1:]
        design = np.column_stack((np.ones(n), np.arange(n, dtype=float), weekdays))
        model = sm.OLS(y, design).fit(cov_type="HAC", cov_kwds={"maxlags": min(7, n // 4)})
        slope = float(model.params[1])
        p_value = float(model.pvalues[1])
        ci_low, ci_high = (float(v) for v in model.conf_int()[1])
        avg_sales = float(np.mean(y))
        span_effect = slope * (n - 1) / avg_sales * 100 if avg_sales else 0.0
        ci_effect = [v * (n - 1) / avg_sales * 100 if avg_sales else 0.0 for v in (ci_low, ci_high)]
        window = min(28, n // 2)
        previous_avg = float(np.mean(y[-2 * window:-window]))
        recent_avg = float(np.mean(y[-window:]))
        variation = (recent_avg - previous_avg) / previous_avg * 100 if previous_avg else None
        coverage = len(observed) / n

        if coverage < 0.35 or avg_sales == 0:
            trend, confidence = "inconclusiva", "baixa"
        elif p_value < 0.05 and ci_effect[0] > 10:
            trend, confidence = "crescente", "alta" if n >= 56 else "média"
        elif p_value < 0.05 and ci_effect[1] < -10:
            trend, confidence = "decrescente", "alta" if n >= 56 else "média"
        elif n >= 28 and ci_effect[0] > -10 and ci_effect[1] < 10:
            trend, confidence = "estável", "alta" if n >= 56 else "média"
        else:
            trend, confidence = "inconclusiva", "baixa"

        if trend == "inconclusiva":
            description = "Dados insuficientes para concluir crescimento, queda ou estabilidade. Amplie o período ou revise dias sem vendas."
        else:
            description = (
                f"Tendência {trend}: mudança estimada de {span_effect:+.1f}% ao longo de {n} dias "
                f"(intervalo de 95%: {ci_effect[0]:+.1f}% a {ci_effect[1]:+.1f}%), "
                "com ajuste para dia da semana."
            )

        result = {
            "success": True,
            "product_id": product_id,
            "trend": trend,
            "confidence": confidence,
            "metrics": {
                "slope": float(slope),
                "r_squared": float(model.rsquared),
                "avg_sales": avg_sales,
                "recent_avg": recent_avg,
                "previous_avg": previous_avg,
                "variation_percent": variation,
                "data_points": n,
                "days_with_sales": len(observed),
                "coverage_percent": coverage * 100,
                "p_value": p_value,
                "effect_percent": span_effect,
                "effect_ci_95_percent": ci_effect,
                "comparison_window_days": window,
            },
        }
        if product_name:
            result["product_name"] = product_name

        result["recommendation"] = None if confidence == "baixa" else description
        result["description"] = description

        return result

    except Exception as e:
        logger.exception(f"Erro na classificação de tendência do produto {product_id}")
        return {
            "success": False,
            "message": str(e),
            "trend": "error",
        }


def classify_all_products_trends(
    sales_data: list[dict],
    min_periods: int = 7,
) -> dict:
    """
    Classify trends for all products.

    Returns:
        Dict with trends for all products
    """
    products = {}
    product_names = {}
    for sale in sales_data:
        pid = sale.get("product_id")
        if pid not in products:
            products[pid] = []
        products[pid].append(sale)
        name = sale.get("product_name")
        if name:
            product_names[pid] = name

    results = {}
    for pid, product_sales in products.items():
        result = classify_product_trend(product_sales, pid, min_periods, product_name=product_names.get(pid))
        results[pid] = result

    growing = sum(1 for r in results.values() if "crescente" in r.get("trend", ""))
    declining = sum(1 for r in results.values() if "decrescente" in r.get("trend", ""))
    stable = sum(1 for r in results.values() if r.get("trend") == "estável")
    inconclusive = sum(1 for r in results.values() if r.get("trend") in ("inconclusiva", "insufficient_data", "error"))

    return {
        "success": True,
        "products_analyzed": len(products),
        "summary": {
            "growing": growing,
            "declining": declining,
            "stable": stable,
            "inconclusive": inconclusive,
        },
        "by_product": results,
    }


def detect_seasonality(
    sales_data: list[dict],
    period: str = "weekly",
) -> dict:
    """
    Detect seasonality patterns in sales data.

    Args:
        sales_data: Sales records
        period: 'weekly', 'monthly', or 'quarterly'

    Returns:
        Dict with seasonality analysis
    """
    if len(sales_data) < 30:
        return {
            "success": False,
            "message": "Dados insuficientes para análise de sazonalidade",
            "seasonality": {},
        }

    try:
        df = pd.DataFrame(sales_data)
        df["date"] = pd.to_datetime(df["date"])

        if period == "weekly":
            df["period"] = df["date"].dt.dayofweek
            period_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        elif period == "monthly":
            df["period"] = df["date"].dt.month
            period_names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        else:
            df["period"] = df["date"].dt.quarter
            period_names = ["T1", "T2", "T3", "T4"]

        period_sales = df.groupby("period")["quantity"].sum()

        avg_sales = period_sales.mean()
        deviation = ((period_sales - avg_sales) / avg_sales * 100).to_dict()

        seasonality = {
            period_names[i]: {
                "total_sales": int(period_sales.get(i, 0)),
                "deviation_from_avg": float(deviation.get(i, 0)),
            }
            for i in range(len(period_names))
        }

        max_period = max(deviation, key=deviation.get)
        min_period = min(deviation, key=deviation.get)

        return {
            "success": True,
            "period": period,
            "seasonality": seasonality,
            "peak_period": period_names[max_period],
            "low_period": period_names[min_period],
            "max_deviation": float(deviation[max_period]),
            "min_deviation": float(deviation[min_period]),
        }

    except Exception as e:
        logger.exception("Erro na análise de sazonalidade")
        return {
            "success": False,
            "message": str(e),
            "seasonality": {},
        }
