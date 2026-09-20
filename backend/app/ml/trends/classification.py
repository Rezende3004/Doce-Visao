"""Trend classification using linear regression and statistical analysis."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)


def classify_product_trend(
    sales_data: list[dict],
    product_id: int,
    min_periods: int = 7,
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
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        daily_sales = df.groupby("date")["quantity"].sum().reset_index()

        if len(daily_sales) < min_periods:
            return {
                "success": False,
                "message": "Períodos insuficientes",
                "trend": "insufficient_data",
            }

        X = np.arange(len(daily_sales)).reshape(-1, 1)
        y = daily_sales["quantity"].values

        model = LinearRegression()
        model.fit(X, y)

        slope = model.coef_[0]
        r_squared = model.score(X, y)

        trend, confidence = _classify_trend(slope, r_squared, y)

        avg_sales = float(np.mean(y))
        recent_avg = float(np.mean(y[-7:])) if len(y) >= 7 else float(np.mean(y))
        variation = ((recent_avg - avg_sales) / avg_sales * 100) if avg_sales > 0 else 0

        return {
            "success": True,
            "product_id": product_id,
            "trend": trend,
            "confidence": confidence,
            "metrics": {
                "slope": float(slope),
                "r_squared": float(r_squared),
                "avg_sales": avg_sales,
                "recent_avg": recent_avg,
                "variation_percent": variation,
                "data_points": len(daily_sales),
            },
            "description": _generate_trend_description(trend, variation, confidence),
        }

    except Exception as e:
        logger.exception(f"Erro na classificação de tendência do produto {product_id}")
        return {
            "success": False,
            "message": str(e),
            "trend": "error",
        }


def _classify_trend(slope: float, r_squared: float, values: np.ndarray) -> tuple[str, str]:
    """
    Classify trend based on slope and R².
    
    Returns:
        Tuple of (trend_label, confidence_level)
    """
    mean_val = np.mean(values)
    relative_slope = slope / mean_val if mean_val > 0 else 0

    if r_squared < 0.3:
        confidence = "baixa"
    elif r_squared < 0.6:
        confidence = "média"
    else:
        confidence = "alta"

    if abs(relative_slope) < 0.01:
        trend = "estável"
    elif relative_slope > 0.05:
        trend = "crescente"
    elif relative_slope > 0.02:
        trend = "levemente crescente"
    elif relative_slope < -0.05:
        trend = "decrescente"
    elif relative_slope < -0.02:
        trend = "levemente decrescente"
    else:
        trend = "estável"

    return trend, confidence


def _generate_trend_description(trend: str, variation: float, confidence: str) -> str:
    """Generate human-readable trend description."""
    if trend == "estável":
        return f"Vendas estáveis com variação de {variation:.1f}% nos últimos períodos."
    elif "crescente" in trend:
        return f"Tendência de crescimento com variação de +{variation:.1f}%. Confiança: {confidence}."
    elif "decrescente" in trend:
        return f"Tendência de queda com variação de {variation:.1f}%. Confiança: {confidence}."
    else:
        return f"Tendência: {trend}."


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
    for sale in sales_data:
        pid = sale.get("product_id")
        if pid not in products:
            products[pid] = []
        products[pid].append(sale)

    results = {}
    for pid, product_sales in products.items():
        result = classify_product_trend(product_sales, pid, min_periods)
        results[pid] = result

    growing = sum(1 for r in results.values() if "crescente" in r.get("trend", ""))
    declining = sum(1 for r in results.values() if "decrescente" in r.get("trend", ""))
    stable = sum(1 for r in results.values() if r.get("trend") == "estável")

    return {
        "success": True,
        "products_analyzed": len(products),
        "summary": {
            "growing": growing,
            "declining": declining,
            "stable": stable,
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
