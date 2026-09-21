"""Visão Geral — KPIs e resumo do período."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date

import plotly.graph_objects as go
import streamlit as st
from services.api_client import get_by_weekday, get_insights, get_summary, get_timeline

st.set_page_config(page_title="Visão Geral — DoceVisão", page_icon="📊", layout="wide")
st.title("📊 Visão Geral")

col1, col2 = st.columns([3, 1])
with col1:
    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input("Data inicial", value=date(2025, 1, 1))
    with c2:
        end_date = st.date_input("Data final", value=date(2025, 7, 31))
with col2:
    st.write("")
    st.write("")
    if st.button("Aplicar filtros", use_container_width=True):
        st.rerun()

sd = start_date.isoformat()
ed = end_date.isoformat()

try:
    summary = get_summary(start_date=sd, end_date=ed)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Faturamento", summary["faturamento"], delta=f"{summary['crescimento_percentual']:.1f}%" if summary.get("crescimento_percentual") is not None else None
)
c2.metric("Pedidos", summary["num_pedidos"])
c3.metric("Ticket Médio", summary["ticket_medio"])
c4.metric("Itens Vendidos", summary["itens_vendidos"])

if summary.get("faturamento_anterior"):
    st.caption(f"Período anterior: {summary['faturamento_anterior']}")

st.subheader("Evolução do Faturamento")
try:
    timeline = get_timeline(start_date=sd, end_date=ed)
    if timeline:
        fig = go.Figure(
            go.Scatter(
                x=[p["date"] for p in timeline],
                y=[p["faturamento_cents"] / 100 for p in timeline],
                mode="lines",
                fill="tozeroy",
                line=dict(color="#D4577B"),
            )
        )
        fig.update_layout(yaxis_title="Faturamento (R$)", xaxis_title="Data", height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados de vendas no período selecionado.")
except Exception:
    st.info("Sem dados para exibir.")

st.subheader("Vendas por Dia da Semana")
try:
    weekdays = get_by_weekday(start_date=sd, end_date=ed)
    if weekdays:
        fig2 = go.Figure(
            go.Bar(
                x=[w["weekday"] for w in weekdays],
                y=[w["faturamento_cents"] / 100 for w in weekdays],
                marker_color="#D4577B",
            )
        )
        fig2.update_layout(yaxis_title="Faturamento (R$)", height=300)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem dados para exibir.")
except Exception:
    st.info("Sem dados para exibir.")

st.subheader("Resumo Narrativo")
try:
    insights = get_insights(start_date=sd, end_date=ed)
    if insights:
        for ins in insights[:5]:
            level_icon = {"informativo": "ℹ️", "atencao": "⚠️", "oportunidade": "💡"}.get(ins["level"], "ℹ️")
            st.markdown(f"{level_icon} **{ins['title']}**")
            st.markdown(f"> {ins['description']}")
    else:
        st.info("Nenhum insight disponível para o período.")
except Exception:
    st.info("Insights indisponíveis.")
