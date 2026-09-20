"""API client for the Streamlit frontend."""
from __future__ import annotations

import os

import httpx

API_URL = os.environ.get("DOCEVISAO_API_URL", "http://localhost:8000")
_client = httpx.Client(base_url=API_URL, timeout=30.0)


def _params(**kwargs) -> dict:
    return {k: v for k, v in kwargs.items() if v is not None}


def health() -> dict:
    return _client.get("/health").json()


def get_summary(start_date=None, end_date=None, product_id=None, category=None, channel_id=None) -> dict:
    r = _client.get("/api/v1/dashboard/summary", params=_params(
        start_date=start_date, end_date=end_date, product_id=product_id, category=category, channel_id=channel_id))
    r.raise_for_status()
    return r.json()


def get_timeline(start_date=None, end_date=None, **kw) -> list[dict]:
    r = _client.get("/api/v1/sales/timeline", params=_params(start_date=start_date, end_date=end_date, **kw))
    r.raise_for_status()
    return r.json()


def get_by_weekday(start_date=None, end_date=None, **kw) -> list[dict]:
    r = _client.get("/api/v1/sales/by-weekday", params=_params(start_date=start_date, end_date=end_date, **kw))
    r.raise_for_status()
    return r.json()


def get_by_channel(start_date=None, end_date=None, **kw) -> list[dict]:
    r = _client.get("/api/v1/sales/by-channel", params=_params(start_date=start_date, end_date=end_date, **kw))
    r.raise_for_status()
    return r.json()


def get_ranking(sort_by="quantity", limit=20, start_date=None, end_date=None, **kw) -> list[dict]:
    r = _client.get("/api/v1/products/ranking", params=_params(
        sort_by=sort_by, limit=limit, start_date=start_date, end_date=end_date, **kw))
    r.raise_for_status()
    return r.json()


def get_category_performance(start_date=None, end_date=None, **kw) -> list[dict]:
    r = _client.get("/api/v1/products/categories/performance", params=_params(start_date=start_date, end_date=end_date, **kw))
    r.raise_for_status()
    return r.json()


def get_margin(start_date=None, end_date=None, **kw) -> dict:
    r = _client.get("/api/v1/products/margin", params=_params(start_date=start_date, end_date=end_date, **kw))
    r.raise_for_status()
    return r.json()


def get_waste(start_date=None, end_date=None, **kw) -> list[dict]:
    r = _client.get("/api/v1/production/waste", params=_params(start_date=start_date, end_date=end_date, **kw))
    r.raise_for_status()
    return r.json()


def get_insights(start_date=None, end_date=None, **kw) -> list[dict]:
    r = _client.get("/api/v1/insights", params=_params(start_date=start_date, end_date=end_date, **kw))
    r.raise_for_status()
    return r.json()


def get_filter_options() -> dict:
    r = _client.get("/api/v1/filters/options")
    r.raise_for_status()
    return r.json()


def get_imports(limit=50, offset=0) -> list[dict]:
    r = _client.get("/api/v1/imports", params={"limit": limit, "offset": offset})
    r.raise_for_status()
    return r.json()


def preview_sales(file_content: bytes, filename: str) -> dict:
    r = _client.post("/api/v1/imports/sales/preview", files={"file": (filename, file_content)})
    r.raise_for_status()
    return r.json()


def confirm_sales(file_content: bytes, filename: str) -> dict:
    r = _client.post("/api/v1/imports/sales/confirm", files={"file": (filename, file_content)})
    r.raise_for_status()
    return r.json()


def preview_production(file_content: bytes, filename: str) -> dict:
    r = _client.post("/api/v1/imports/production/preview", files={"file": (filename, file_content)})
    r.raise_for_status()
    return r.json()


def confirm_production(file_content: bytes, filename: str) -> dict:
    r = _client.post("/api/v1/imports/production/confirm", files={"file": (filename, file_content)})
    r.raise_for_status()
    return r.json()


def get_import_errors(batch_id: int) -> list[dict]:
    r = _client.get(f"/api/v1/imports/{batch_id}/errors")
    r.raise_for_status()
    return r.json()
