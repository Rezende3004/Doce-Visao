"""Produção e Desperdício."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date

import plotly.graph_objects as go
import streamlit as st
from services.api_client import get_waste

st.set_page_config(page_title="Produção — DoceVisão", page_icon="🏭", layout="wide")
st.title("🏭 Produção e Desperdício")

c1, c2 = st.columns(2)
with c1:
    start_date = st.date_input("Data inicial", value=date(2025, 1, 1), key="waste_start")
with c2:
    end_date = st.date_input("Data final", value=date(2025, 7, 31), key="waste_end")

sd, ed = start_date.isoformat(), end_date.isoformat()

try:
    waste = get_waste(start_date=sd, end_date=ed)
except Exception:
    waste = []

if not waste:
    st.info("Sem dados de produção importados. Importe dados de produção na página de Importação para habilitar esta análise.")
    st.stop()

total_produced = sum(w["produced"] for w in waste)
total_sold = sum(w["sold"] for w in waste)
total_discarded = sum(w["discarded"] for w in waste)
overall_rate = (total_discarded / total_produced * 100) if total_produced > 0 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Produzido", total_produced)
c2.metric("Vendido", total_sold)
c3.metric("Descartado", total_discarded)
c4.metric("Taxa de Desperdício", f"{overall_rate:.1f}%")

st.subheader("Desperdício por Produto")
fig = go.Figure(go.Bar(
    x=[w["product_name"] for w in waste],
    y=[w["discarded"] for w in waste],
    marker_color="#EF4444",
    name="Descartado",
))
fig.add_trace(go.Bar(
    x=[w["product_name"] for w in waste],
    y=[w["sold"] for w in waste],
    marker_color="#22C55E",
    name="Vendido",
))
fig.update_layout(barmode="group", yaxis_title="Quantidade", height=400, xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Detalhamento")
st.dataframe(waste, use_container_width=True, hide_index=True)
