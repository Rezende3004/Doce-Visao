"""Product clustering using K-means and feature engineering."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


def cluster_products(
    product_metrics: list[dict],
    n_clusters: int = 3,
) -> dict:
    """
    Cluster products based on sales metrics using K-means.
    
    Args:
        product_metrics: List of dicts with product_id, name, quantity, revenue, margin, etc.
        n_clusters: Number of clusters (2-5 recommended)
    
    Returns:
        Dict with cluster assignments and characteristics
    """
    if len(product_metrics) < n_clusters:
        return {
            "success": False,
            "message": f"Produtos insuficientes para {n_clusters} clusters",
            "clusters": [],
        }

    try:
        df = pd.DataFrame(product_metrics)

        features = ["quantity", "faturamento_cents"]
        if "margem_cents" in df.columns and df["margem_cents"].notna().any():
            features.append("margem_cents")
        if "num_orders" in df.columns:
            features.append("num_orders")

        X = df[features].fillna(0)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X_scaled)

        df["cluster"] = cluster_labels

        clusters = []
        for cluster_id in range(n_clusters):
            cluster_data = df[df["cluster"] == cluster_id]

            cluster_info = {
                "cluster_id": cluster_id,
                "size": len(cluster_data),
                "products": cluster_data["product_name"].tolist() if "product_name" in df.columns else [],
                "product_ids": cluster_data["product_id"].tolist(),
                "characteristics": {
                    "avg_quantity": float(cluster_data["quantity"].mean()),
                    "avg_revenue": float(cluster_data["faturamento_cents"].mean()),
                    "total_quantity": int(cluster_data["quantity"].sum()),
                    "total_revenue": int(cluster_data["faturamento_cents"].sum()),
                },
            }

            if "margem_cents" in features:
                cluster_info["characteristics"]["avg_margin"] = float(cluster_data["margem_cents"].mean())

            clusters.append(cluster_info)

        cluster_summary = _interpret_clusters(clusters)

        return {
            "success": True,
            "clusters": clusters,
            "summary": cluster_summary,
            "metrics": {
                "n_clusters": n_clusters,
                "inertia": float(kmeans.inertia_),
                "products_clustered": len(product_metrics),
            },
        }

    except Exception as e:
        logger.exception("Erro na clusterização")
        return {
            "success": False,
            "message": str(e),
            "clusters": [],
        }


def _interpret_clusters(clusters: list[dict]) -> dict:
    """
    Interpret cluster characteristics and assign meaningful labels.
    
    Returns:
        Dict with cluster interpretations
    """
    if not clusters:
        return {}

    sorted_by_revenue = sorted(clusters, key=lambda c: c["characteristics"]["avg_revenue"], reverse=True)

    interpretations = {}
    for cluster in sorted_by_revenue:
        cid = cluster["cluster_id"]
        avg_rev = cluster["characteristics"]["avg_revenue"]
        avg_qty = cluster["characteristics"]["avg_quantity"]

        if avg_rev > np.median([c["characteristics"]["avg_revenue"] for c in clusters]) * 1.5:
            label = "Alto Faturamento"
        elif avg_qty > np.median([c["characteristics"]["avg_quantity"] for c in clusters]) * 1.5:
            label = "Alto Volume"
        else:
            label = "Padrão"

        interpretations[cid] = {
            "label": label,
            "description": _generate_cluster_description(cluster),
        }

    return interpretations


def _generate_cluster_description(cluster: dict) -> str:
    """Generate human-readable description of cluster characteristics."""
    chars = cluster["characteristics"]
    size = cluster["size"]

    desc = f"Cluster com {size} produto(s). "
    desc += f"Faturamento médio: R$ {chars['avg_revenue'] / 100:.2f}. "
    desc += f"Quantidade média: {chars['avg_quantity']:.0f} unidades."

    if "avg_margin" in chars:
        desc += f" Margem média: R$ {chars['avg_margin'] / 100:.2f}."

    return desc


def optimal_number_of_clusters(
    product_metrics: list[dict],
    max_clusters: int = 10,
) -> dict:
    """
    Find optimal number of clusters using elbow method.
    
    Returns:
        Dict with inertia values for different k
    """
    if len(product_metrics) < 4:
        return {
            "success": False,
            "message": "Produtos insuficientes para análise",
            "elbow_data": [],
        }

    try:
        df = pd.DataFrame(product_metrics)
        features = ["quantity", "faturamento_cents"]
        X = df[features].fillna(0)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        inertias = []
        K_range = range(2, min(max_clusters + 1, len(product_metrics)))

        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X_scaled)
            inertias.append({
                "k": k,
                "inertia": float(kmeans.inertia_),
            })

        return {
            "success": True,
            "elbow_data": inertias,
            "recommended_k": _find_elbow_point(inertias),
        }

    except Exception as e:
        logger.exception("Erro na análise de clusters")
        return {
            "success": False,
            "message": str(e),
            "elbow_data": [],
        }


def _find_elbow_point(inertia_data: list[dict]) -> int:
    """
    Find elbow point in inertia curve (simplified method).
    """
    if len(inertia_data) < 3:
        return 2

    inertias = [d["inertia"] for d in inertia_data]

    diffs = np.diff(inertias)
    diff_ratios = diffs[1:] / diffs[:-1]

    elbow_idx = np.argmax(diff_ratios) + 2

    return inertia_data[min(elbow_idx, len(inertia_data) - 1)]["k"]
