"""Canais e Períodos — Análise temporal e por canal."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date

import plotly.graph_objects as go
import streamlit as st
from services.api_client import get_by_channel, get_by_weekday, get_timeline

st.set_page_config(page_title="Canais e Períodos — DoceVisão", page_icon="📅", layout="wide")
st.title("📅 Canais e Períodos")

c1, c2 = st.columns(2)
with c1:
    start_date = st.date_input("Data inicial", value=date(2025, 1, 1), key="ch_start")
with c2:
    end_date = st.date_input("Data final", value=date(2025, 7, 31), key="ch_end")

sd, ed = start_date.isoformat(), end_date.isoformat()

st.subheader("Vendas por Canal")
try:
    channels = get_by_channel(start_date=sd, end_date=ed)
    if channels:
        fig = go.Figure(go.Bar(
            x=[c["channel_name"] for c in channels],
            y=[c["faturamento_cents"] / 100 for c in channels],
            marker_color="#D4577B",
        ))
        fig.update_layout(yaxis_title="Faturamento (R$)", height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(channels, use_container_width=True, hide_index=True)
    else:
        st.info("Sem dados de canais.")
except Exception as e:
    st.error(f"Erro: {e}")

st.subheader("Desempenho por Dia da Semana")
try:
    weekdays = get_by_weekday(start_date=sd, end_date=ed)
    if weekdays:
        fig2 = go.Figure(go.Bar(
            x=[w["weekday"] for w in weekdays],
            y=[w["faturamento_cents"] / 100 for w in weekdays],
            marker_color="#8B5CF6",
        ))
        fig2.update_layout(yaxis_title="Faturamento (R$)", height=300)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem dados.")
except Exception as e:
    st.error(f"Erro: {e}")

st.subheader("Evolução Temporal")
try:
    timeline = get_timeline(start_date=sd, end_date=ed)
    if timeline:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=[p["date"] for p in timeline],
            y=[p["faturamento_cents"] / 100 for p in timeline],
            mode="lines",
            name="Faturamento",
            line=dict(color="#D4577B"),
        ))
        fig3.add_trace(go.Scatter(
            x=[p["date"] for p in timeline],
            y=[p["num_pedidos"] for p in timeline],
            mode="lines",
            name="Pedidos",
            yaxis="y2",
            line=dict(color="#F59E0B"),
        ))
        fig3.update_layout(
            yaxis=dict(title="Faturamento (R$)"),
            yaxis2=dict(title="Pedidos", overlaying="y", side="right"),
            height=400,
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Sem dados.")
except Exception as e:
    st.error(f"Erro: {e}")
