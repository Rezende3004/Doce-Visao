"""Produtos — Rankings, categorias e margem."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date

import plotly.graph_objects as go
import streamlit as st
from services.api_client import get_category_performance, get_margin, get_ranking

st.set_page_config(page_title="Produtos — DoceVisão", page_icon="🍰", layout="wide")
st.title("🍰 Produtos")

c1, c2 = st.columns(2)
with c1:
    start_date = st.date_input("Data inicial", value=date(2025, 1, 1), key="prod_start")
with c2:
    end_date = st.date_input("Data final", value=date(2025, 7, 31), key="prod_end")

sd, ed = start_date.isoformat(), end_date.isoformat()

st.subheader("Ranking por Quantidade Vendida")
try:
    ranking_qty = get_ranking(sort_by="quantity", limit=15, start_date=sd, end_date=ed)
    if ranking_qty:
        fig = go.Figure(
            go.Bar(
                x=[p["product_name"] for p in ranking_qty],
                y=[p["quantity"] for p in ranking_qty],
                marker_color="#D4577B",
                orientation="v",
            )
        )
        fig.update_layout(yaxis_title="Quantidade", height=350, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(ranking_qty, use_container_width=True, hide_index=True)
    else:
        st.info("Sem dados de vendas no período.")
except Exception as e:
    st.error(f"Erro: {e}")

st.subheader("Ranking por Faturamento")
try:
    ranking_rev = get_ranking(sort_by="revenue", limit=15, start_date=sd, end_date=ed)
    if ranking_rev:
        fig2 = go.Figure(
            go.Bar(
                x=[p["product_name"] for p in ranking_rev],
                y=[p["faturamento_cents"] / 100 for p in ranking_rev],
                marker_color="#8B5CF6",
            )
        )
        fig2.update_layout(yaxis_title="Faturamento (R$)", height=350, xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem dados.")
except Exception as e:
    st.error(f"Erro: {e}")

st.subheader("Desempenho por Categoria")
try:
    cats = get_category_performance(start_date=sd, end_date=ed)
    if cats:
        fig3 = go.Figure(
            go.Bar(
                x=[c["category"] for c in cats],
                y=[c["faturamento_cents"] / 100 for c in cats],
                marker_color="#F59E0B",
            )
        )
        fig3.update_layout(yaxis_title="Faturamento (R$)", height=300)
        st.plotly_chart(fig3, use_container_width=True)
        st.dataframe(cats, use_container_width=True, hide_index=True)
    else:
        st.info("Sem dados.")
except Exception as e:
    st.error(f"Erro: {e}")

st.subheader("Margem Estimada")
try:
    margin = get_margin(start_date=sd, end_date=ed)
    if margin["coverage_percentual"] < 50:
        st.warning(
            f"Cobertura de custos: apenas {margin['coverage_percentual']:.0f}% das vendas possuem dados de custo. "
            "A margem calculada pode não ser representativa."
        )
    st.metric("Faturamento", margin["faturamento"])
    st.metric("Custo Total", margin["custo_total"])
    st.metric("Margem", margin["margem"], delta=f"{margin['margem_percentual']:.1f}%")
except Exception as e:
    st.info(f"Margem indisponível: {e}")
