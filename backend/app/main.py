from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.presentation.api.exception_handlers import register_exception_handlers
from app.presentation.api.routes import (
    dashboard,
    exports,
    imports,
    insights,
    ml,
    production,
    products,
    sales,
)

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(
    title="DoceVisão API",
    description="Sistema de Business Intelligence para docerias",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(imports.router, prefix="/api/v1/imports", tags=["Importações"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(sales.router, prefix="/api/v1/sales", tags=["Vendas"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Produtos"])
app.include_router(production.router, prefix="/api/v1/production", tags=["Produção"])
app.include_router(exports.router, prefix="/api/v1/exports", tags=["Exportações"])
app.include_router(insights.router, prefix="/api/v1/insights", tags=["Insights"])
app.include_router(ml.router, prefix="/api/v1/ml", tags=["Machine Learning"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.get("/api/v1/filters/options", tags=["Filtros"])
def get_filter_options():
    from app.infrastructure.database.connection import get_session
    from app.infrastructure.repositories.implementations import DimensionRepository
    session = get_session()
    try:
        repo = DimensionRepository(session)
        categories = repo.list_categories()
        products_list = [{"id": p.id, "name": p.name, "category": p.category} for p in repo.list_products()]
        channels = [{"id": c.id, "name": c.name} for c in repo.list_channels()]
        return {"categories": categories, "products": products_list, "channels": channels}
    finally:
        session.close()
