"""Substitui dados locais de demonstração pelo catálogo vegetal, com backup."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path

from app.domain.value_objects.plant_sweets import PLANT_SWEETS
from app.infrastructure.database.connection import Base
from app.infrastructure.importers.file_importer import (
    compute_file_hash,
    confirm_production_import,
    confirm_sales_import,
    read_upload,
)
from app.infrastructure.repositories.implementations import DimensionRepository, ImportRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "docevisao.db"
SAMPLES = ROOT / "sample_data"


def main() -> None:
    if not DB.exists():
        raise FileNotFoundError(f"Banco local não encontrado: {DB}")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / f"docevisao.backup_{stamp}.db"
    staged = ROOT / f"docevisao.stage_{stamp}.db"

    with sqlite3.connect(DB) as source, sqlite3.connect(backup) as target:
        source.backup(target)
    try:
        engine = create_engine(f"sqlite:///{staged}")
        try:
            Base.metadata.create_all(engine)
            with sqlite3.connect(backup) as source, sqlite3.connect(staged) as target:
                version = source.execute("SELECT version_num FROM alembic_version").fetchone()
                target.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)")
                if version:
                    target.execute("INSERT INTO alembic_version (version_num) VALUES (?)", version)
            with sessionmaker(bind=engine, expire_on_commit=False)() as session:
                imports = ImportRepository(session)
                dimensions = DimensionRepository(session)
                for filename, confirm in (
                    ("vendas_sinteticas.csv", confirm_sales_import),
                    ("producao_sintetica.csv", confirm_production_import),
                ):
                    path = SAMPLES / filename
                    content = path.read_bytes()
                    result = confirm(read_upload(content, filename), imports, dimensions, filename, compute_file_hash(content))
                    if result.rejected_rows or not result.accepted_rows:
                        raise RuntimeError(f"Importação de {filename} falhou: {result.rejected_rows} linhas rejeitadas")
                names = {product.name.casefold() for product in dimensions.list_products()}
                if not names or not names.issubset(PLANT_SWEETS):
                    raise RuntimeError("O banco gerado contém produtos fora do catálogo vegetal")
        finally:
            engine.dispose()

        os.replace(staged, DB)
    finally:
        staged.unlink(missing_ok=True)
        Path(f"{staged}-wal").unlink(missing_ok=True)
        Path(f"{staged}-shm").unlink(missing_ok=True)

    print(f"Banco atualizado com {len(names)} doces vegetais. Backup: {backup}")


if __name__ == "__main__":
    main()
