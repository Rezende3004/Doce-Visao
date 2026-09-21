from __future__ import annotations

import os

from pydantic_settings import BaseSettings

# Project root is one level above backend/
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class Settings(BaseSettings):
    database_url: str = f"sqlite:///{os.path.join(_PROJECT_ROOT, 'docevisao.db')}"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:8501"
    max_upload_size_mb: int = 50
    secret_key: str = "change-me-in-production"
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


settings = Settings()
