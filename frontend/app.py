"""DoceVisão — Dashboard de Business Intelligence para docerias."""
import os

import streamlit as st

API_URL = os.environ.get("DOCEVISAO_API_URL", "http://localhost:8000")

st.set_page_config(page_title="DoceVisão", page_icon="🧁", layout="wide")

st.title("🧁 DoceVisão")
st.caption("Sistema de Business Intelligence para docerias")

st.markdown("""
Bem-vindo ao **DoceVisão**! Utilize o menu lateral para navegar entre as páginas:

- **Visão Geral** — KPIs principais e resumo do período
- **Produtos** — Ranking, categorias e margem
- **Canais e Períodos** — Análise temporal e por canal
- **Produção e Desperdício** — Indicadores de produção
- **Insights** — Análises automáticas baseadas nos dados
- **Importação** — Importe dados de vendas e produção
- **Sobre os Indicadores** — Glossário de KPIs

Para começar, importe seus dados na página de **Importação** ou use os dados sintéticos de demonstração.
""")
