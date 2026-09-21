"""Anomaly detection using Isolation Forest and statistical methods."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


def detect_anomalies_isolation_forest(
    sales_data: list[dict],
    contamination: float = 0.05,
) -> dict:
    """Detect anomalous sales using Isolation Forest.

    Args:
        sales_data: List of sales records with features
        contamination: Expected proportion of anomalies (0.01 to 0.1)

    Returns:
        Dict with anomalies detected and metrics
    """
    if len(sales_data) < 20:
        return {
            "success": False,
            "message": "Dados insuficientes para detecção de anomalias",
            "anomalies": [],
        }

    try:
        df = pd.DataFrame(sales_data)

        features = ["quantity", "total_cents"]
        if "unit_price_cents" in df.columns:
            features.append("unit_price_cents")

        data_features = df[features].fillna(0)

        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data_features)

        model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
        )
        predictions = model.fit_predict(data_scaled)

        anomalies = []
        for idx, pred in enumerate(predictions):
            if pred == -1:
                row = df.iloc[idx]
                anomalies.append(
                    {
                        "index": idx,
                        "date": row.get("date"),
                        "product": row.get("product_name", "Desconhecido"),
                        "quantity": int(row.get("quantity", 0)),
                        "total_cents": int(row.get("total_cents", 0)),
                        "anomaly_score": float(model.score_samples(data_scaled[idx : idx + 1])[0]),
                    }
                )

        return {
            "success": True,
            "anomalies": anomalies,
            "metrics": {
                "total_records": len(sales_data),
                "anomalies_detected": len(anomalies),
                "anomaly_rate": len(anomalies) / len(sales_data) * 100,
                "contamination_used": contamination,
            },
        }

    except Exception as e:
        logger.exception("Erro na detecção de anomalias")
        return {
            "success": False,
            "message": str(e),
            "anomalies": [],
        }


def detect_anomalies_zscore(
    values: list[float],
    threshold: float = 3.0,
) -> dict:
    """
    Detect anomalies using Z-score method (simpler, for univariate data).

    Args:
        values: List of numerical values
        threshold: Z-score threshold for anomaly detection

    Returns:
        Dict with anomalies and statistics
    """
    if len(values) < 10:
        return {
            "success": False,
            "message": "Dados insuficientes",
            "anomalies": [],
        }

    try:
        arr = np.array(values)
        mean = np.mean(arr)
        std = np.std(arr)

        if std == 0:
            return {
                "success": True,
                "anomalies": [],
                "metrics": {"mean": float(mean), "std": 0},
            }

        z_scores = np.abs((arr - mean) / std)
        anomalies = [{"index": i, "value": float(v), "z_score": float(z)} for i, (v, z) in enumerate(zip(values, z_scores, strict=False)) if z > threshold]

        return {
            "success": True,
            "anomalies": anomalies,
            "metrics": {
                "mean": float(mean),
                "std": float(std),
                "threshold": threshold,
                "anomalies_detected": len(anomalies),
            },
        }

    except Exception as e:
        logger.exception("Erro na detecção Z-score")
        return {
            "success": False,
            "message": str(e),
            "anomalies": [],
        }


def detect_sales_anomalies_by_product(
    sales_data: list[dict],
    method: str = "isolation_forest",
) -> dict:
    """
    Detect anomalies grouped by product.

    Args:
        sales_data: Sales records
        method: 'isolation_forest' or 'zscore'

    Returns:
        Dict with anomalies per product
    """
    products = {}
    for sale in sales_data:
        pid = sale.get("product_id")
        if pid not in products:
            products[pid] = []
        products[pid].append(sale)

    results = {}
    for pid, product_sales in products.items():
        if method == "isolation_forest":
            result = detect_anomalies_isolation_forest(product_sales)
        else:
            values = [s.get("total_cents", 0) for s in product_sales]
            result = detect_anomalies_zscore(values)

        results[pid] = result

    total_anomalies = sum(r.get("metrics", {}).get("anomalies_detected", 0) for r in results.values())

    return {
        "success": True,
        "method": method,
        "products_analyzed": len(products),
        "total_anomalies": total_anomalies,
        "by_product": results,
    }
