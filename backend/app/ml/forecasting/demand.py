"""Demand forecasting using Prophet for time series with seasonality."""
from __future__ import annotations

import logging

import pandas as pd
from prophet import Prophet

logger = logging.getLogger(__name__)


def forecast_demand(
    timeline_data: list[dict],
    days_to_forecast: int = 30,
    include_history: bool = True,
) -> dict:
    """
    Forecast future demand based on historical sales data.
    
    Args:
        timeline_data: List of dicts with 'date' and 'faturamento_cents' or 'num_pedidos'
        days_to_forecast: Number of days to forecast into the future
        include_history: Whether to include historical data in the response
    
    Returns:
        Dict with forecast data and metrics
    """
    if len(timeline_data) < 30:
        return {
            "success": False,
            "message": "Dados insuficientes para previsão (mínimo 30 dias necessários)",
            "forecast": [],
        }

    try:
        df = pd.DataFrame(timeline_data)
        df["ds"] = pd.to_datetime(df["date"])
        df["y"] = df.get("faturamento_cents", df.get("num_pedidos", 0))
        df = df[["ds", "y"]].sort_values("ds")

        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
        )
        model.fit(df)

        future = model.make_future_dataframe(periods=days_to_forecast)
        forecast = model.predict(future)

        forecast_data = []
        for _, row in forecast.iterrows():
            forecast_data.append({
                "date": row["ds"].strftime("%Y-%m-%d"),
                "predicted": float(row["yhat"]),
                "lower_bound": float(row["yhat_lower"]),
                "upper_bound": float(row["yhat_upper"]),
                "is_historical": row["ds"] <= df["ds"].max(),
            })

        future_only = [f for f in forecast_data if not f["is_historical"]]
        avg_forecast = sum(f["predicted"] for f in future_only) / len(future_only) if future_only else 0
        max_forecast = max(f["predicted"] for f in future_only) if future_only else 0

        return {
            "success": True,
            "forecast": forecast_data if include_history else future_only,
            "metrics": {
                "avg_predicted": avg_forecast,
                "max_predicted": max_forecast,
                "forecast_days": days_to_forecast,
            },
        }

    except Exception as e:
        logger.exception("Erro na previsão de demanda")
        return {
            "success": False,
            "message": f"Erro na previsão: {str(e)}",
            "forecast": [],
        }


def forecast_by_product(
    sales_data: list[dict],
    product_id: int,
    days_to_forecast: int = 30,
) -> dict:
    """
    Forecast demand for a specific product.
    
    Args:
        sales_data: List of sales records with product_id, date, quantity
        product_id: Product ID to forecast
        days_to_forecast: Days to forecast
    
    Returns:
        Forecast dict for the product
    """
    product_sales = [s for s in sales_data if s.get("product_id") == product_id]

    if len(product_sales) < 30:
        return {
            "success": False,
            "message": "Dados insuficientes para este produto",
            "forecast": [],
        }

    df = pd.DataFrame(product_sales)
    df["ds"] = pd.to_datetime(df["date"])
    df["y"] = df["quantity"]
    df = df.groupby("ds")["y"].sum().reset_index()

    try:
        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=False,
        )
        model.fit(df)

        future = model.make_future_dataframe(periods=days_to_forecast)
        forecast = model.predict(future)

        forecast_data = [
            {
                "date": row["ds"].strftime("%Y-%m-%d"),
                "predicted": float(row["yhat"]),
                "lower_bound": float(row["yhat_lower"]),
                "upper_bound": float(row["yhat_upper"]),
            }
            for _, row in forecast.iterrows()
        ]

        return {
            "success": True,
            "product_id": product_id,
            "forecast": forecast_data,
        }

    except Exception as e:
        logger.exception(f"Erro na previsão do produto {product_id}")
        return {
            "success": False,
            "message": str(e),
            "forecast": [],
        }
