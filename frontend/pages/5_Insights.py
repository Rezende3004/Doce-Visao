"""Insights — Análises automáticas."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date

import streamlit as st
from services.api_client import get_insights

st.set_page_config(page_title="Insights — DoceVisão", page_icon="💡", layout="wide")
st.title("💡 Insights")

c1, c2 = st.columns(2)
with c1:
    start_date = st.date_input("Data inicial", value=date(2025, 1, 1), key="ins_start")
with c2:
    end_date = st.date_input("Data final", value=date(2025, 7, 31), key="ins_end")

st.caption(f"Período analisado: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")

sd, ed = start_date.isoformat(), end_date.isoformat()

try:
    insights = get_insights(start_date=sd, end_date=ed)
except Exception as e:
    st.error(f"Erro ao carregar insights: {e}")
    st.stop()

if not insights:
    st.info("Nenhum insight disponível para o período selecionado.")
    st.stop()

levels = {"atencao": "⚠️ Atenção", "oportunidade": "💡 Oportunidade", "informativo": "ℹ️ Informativo"}

for level_key, label in levels.items():
    group = [i for i in insights if i["level"] == level_key]
    if group:
        st.subheader(label)
        for ins in group:
            with st.container(border=True):
                st.markdown(f"**{ins['title']}**")
                st.markdown(ins["description"])
                st.caption(f"Evidência: {ins['evidence']}")
                st.success(f"Recomendação: {ins['recommendation']}")
