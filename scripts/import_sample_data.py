#!/usr/bin/env python3
"""Script para importar dados sintéticos automaticamente."""
import sys
from pathlib import Path

import httpx

API_URL = "http://localhost:8002"
SAMPLE_DATA_DIR = Path(__file__).parent.parent / "sample_data"


def import_file(endpoint: str, file_path: Path) -> dict:
    """Importa um arquivo via API."""
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f, "text/csv")}
        response = httpx.post(f"{API_URL}{endpoint}", files=files, timeout=60.0)
        response.raise_for_status()
        return response.json()


def main():
    """Importa todos os dados sintéticos."""
    print("Importando dados sintéticos...")

    sales_file = SAMPLE_DATA_DIR / "vendas_sinteticas.csv"
    if sales_file.exists():
        print(f"Importando {sales_file.name}...")
        result = import_file("/api/v1/imports/sales/confirm", sales_file)
        print(f"  ✓ Lote #{result['batch_id']}: {result['accepted_rows']} aceitas, {result['rejected_rows']} rejeitadas")
    else:
        print(f"  ✗ Arquivo não encontrado: {sales_file}")

    production_file = SAMPLE_DATA_DIR / "producao_sintetica.csv"
    if production_file.exists():
        print(f"Importando {production_file.name}...")
        result = import_file("/api/v1/imports/production/confirm", production_file)
        print(f"  ✓ Lote #{result['batch_id']}: {result['accepted_rows']} aceitas, {result['rejected_rows']} rejeitadas")
    else:
        print(f"  ✗ Arquivo não encontrado: {production_file}")

    print("\nImportação concluída!")


if __name__ == "__main__":
    main()
