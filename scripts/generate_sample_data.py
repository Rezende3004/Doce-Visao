"""Generate reproducible synthetic data for DoceVisão demo."""
from __future__ import annotations

import csv
import os
import random
from datetime import date, timedelta

SEED = 42
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_data")

PRODUCTS = [
    ("Bolo de Chocolate", "Bolos"),
    ("Bolo de Cenoura", "Bolos"),
    ("Bolo Red Velvet", "Bolos"),
    ("Brigadeiro", "Doces"),
    ("Brigadeiro Gourmet", "Doces"),
    ("Trufa de Maracujá", "Doces"),
    ("Trufa de Morango", "Doces"),
    ("Coxinha", "Salgados"),
    ("Empada de Frango", "Salgados"),
    ("Pão de Queijo", "Salgados"),
    ("Torta de Limão", "Tortas"),
    ("Torta Holandesa", "Tortas"),
]

CHANNELS = ["Balcão", "WhatsApp", "iFood", "Encomenda"]
PAYMENTS = ["Dinheiro", "PIX", "Cartão Débito", "Cartão Crédito"]
STATUSES = ["Concluído", "Concluído", "Concluído", "Concluído", "Cancelado"]

random.seed(SEED)


def random_price(base: int) -> str:
    return f"{base + random.randint(-200, 500) / 100:.2f}".replace(".", ",")


def generate_sales():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    start = date(2025, 1, 1)
    end = date(2025, 7, 31)
    rows = []
    order_counter = 1000

    current = start
    while current <= end:
        num_orders = random.randint(3, 15) if current.weekday() < 5 else random.randint(5, 20)
        if random.random() < 0.1:
            num_orders = 0
        for _ in range(num_orders):
            order_id = f"PED-{order_counter}"
            order_counter += 1
            num_items = random.randint(1, 4)
            items = random.sample(PRODUCTS, min(num_items, len(PRODUCTS)))
            for pos, (product, category) in enumerate(items, 1):
                base_price = random.randint(500, 3500)
                qty = random.randint(1, 5)
                discount = random.choice([0, 0, 0, random.randint(50, 300)])
                has_cost = random.random() < 0.6
                cost = int(base_price * random.uniform(0.3, 0.5)) if has_cost else ""
                channel = random.choice(CHANNELS)
                payment = random.choice(PAYMENTS)
                status = random.choice(STATUSES)
                rows.append({
                    "data_venda": current.strftime("%d/%m/%Y"),
                    "id_pedido": order_id,
                    "id_item": "",
                    "produto": product,
                    "categoria": category,
                    "quantidade": qty,
                    "valor_unitario": f"{base_price / 100:.2f}".replace(".", ","),
                    "desconto": f"{discount / 100:.2f}".replace(".", ",") if discount else "",
                    "canal": channel,
                    "forma_pagamento": payment,
                    "custo_unitario": f"{cost / 100:.2f}".replace(".", ",") if cost != "" else "",
                    "status": status,
                })
        current += timedelta(days=1)

    path = os.path.join(OUTPUT_DIR, "vendas_sinteticas.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} sales rows -> {path}")


def generate_production():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    start = date(2025, 1, 1)
    end = date(2025, 7, 31)
    rows = []

    current = start
    while current <= end:
        if current.weekday() >= 5:
            current += timedelta(days=1)
            continue
        for product, category in PRODUCTS[:8]:
            produced = random.randint(10, 40)
            sold = random.randint(int(produced * 0.6), produced)
            discarded = produced - sold
            reason = random.choice(["Validade", "Qualidade", "Excedente", ""]) if discarded > 0 else ""
            rows.append({
                "data": current.strftime("%d/%m/%Y"),
                "produto": product,
                "categoria": category,
                "quantidade_produzida": produced,
                "quantidade_vendida": sold,
                "quantidade_descartada": discarded,
                "motivo_descarte": reason,
            })
        current += timedelta(days=1)

    path = os.path.join(OUTPUT_DIR, "producao_sintetica.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} production rows -> {path}")


def generate_invalid():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rows = [
        {"data_venda": "32/13/2025", "id_pedido": "ERR-1", "produto": "Bolo", "categoria": "Bolos",
         "quantidade": "1", "valor_unitario": "10,00", "status": "Concluído"},
        {"data_venda": "01/02/2025", "id_pedido": "ERR-2", "produto": "Brigadeiro", "categoria": "Doces",
         "quantidade": "-5", "valor_unitario": "5,00", "status": "Concluído"},
        {"data_venda": "01/02/2025", "id_pedido": "ERR-3", "produto": "Trufa", "categoria": "Doces",
         "quantidade": "1", "valor_unitario": "-10,00", "status": "Concluído"},
        {"data_venda": "01/02/2025", "id_pedido": "", "produto": "Bolo", "categoria": "Bolos",
         "quantidade": "1", "valor_unitario": "10,00", "status": "Concluído"},
        {"data_venda": "01/02/2025", "id_pedido": "ERR-5", "produto": "Bolo", "categoria": "Bolos",
         "quantidade": "1", "valor_unitario": "abc", "status": "Concluído"},
        {"data_venda": "01/02/2025", "id_pedido": "ERR-6", "produto": "Bolo", "categoria": "Bolos",
         "quantidade": "1", "valor_unitario": "10,00", "status": "Inválido"},
    ]
    path = os.path.join(OUTPUT_DIR, "vendas_com_erros.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} invalid rows -> {path}")


if __name__ == "__main__":
    generate_sales()
    generate_production()
    generate_invalid()
    print("Done. All files in sample_data/ are synthetic demo data.")
