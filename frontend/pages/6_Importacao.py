"""Importação de dados."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from services import api_client

st.set_page_config(page_title="Importação — DoceVisão", page_icon="📥", layout="wide")
st.title("📥 Importação de Dados")

tab = st.tabs(["Vendas", "Produção", "Histórico"])

with tab[0]:
    st.subheader("Importar Vendas")
    st.markdown("Baixe o modelo: [modelo_vendas.csv](http://localhost:8000/api/v1/imports/templates/sales)")
    uploaded = st.file_uploader("Selecione o arquivo CSV ou Excel", type=["csv", "xlsx", "xls"], key="sales_upload")
    if uploaded and st.button("Prévia", key="sales_preview"):
        content = uploaded.read()
        try:
            preview = api_client.preview_sales(content, uploaded.name)
            st.success(f"Total: {preview['total_rows']} linhas | Válidas: {preview['valid_rows']} | Inválidas: {preview['invalid_rows']}")
            if preview["errors"]:
                st.warning("Erros encontrados:")
                st.dataframe(preview["errors"][:20], use_container_width=True)
            if st.button("Confirmar Importação", key="sales_confirm", type="primary"):
                result = api_client.confirm_sales(content, uploaded.name)
                st.success(f"Importação concluída! Lote #{result['batch_id']}: {result['accepted_rows']} aceitas, {result['rejected_rows']} rejeitadas.")
        except Exception as e:
            st.error(f"Erro: {e}")

with tab[1]:
    st.subheader("Importar Produção")
    st.markdown("Baixe o modelo: [modelo_producao.csv](http://localhost:8000/api/v1/imports/templates/production)")
    uploaded_p = st.file_uploader("Selecione o arquivo CSV ou Excel", type=["csv", "xlsx", "xls"], key="prod_upload")
    if uploaded_p and st.button("Prévia", key="prod_preview"):
        content = uploaded_p.read()
        try:
            preview = api_client.preview_production(content, uploaded_p.name)
            st.success(f"Total: {preview['total_rows']} linhas | Válidas: {preview['valid_rows']} | Inválidas: {preview['invalid_rows']}")
            if preview["errors"]:
                st.warning("Erros encontrados:")
                st.dataframe(preview["errors"][:20], use_container_width=True)
            if st.button("Confirmar Importação", key="prod_confirm", type="primary"):
                result = api_client.confirm_production(content, uploaded_p.name)
                st.success(f"Importação concluída! Lote #{result['batch_id']}: {result['accepted_rows']} aceitas, {result['rejected_rows']} rejeitadas.")
        except Exception as e:
            st.error(f"Erro: {e}")

with tab[2]:
    st.subheader("Histórico de Importações")
    try:
        imports = api_client.get_imports()
        if imports:
            st.dataframe(imports, use_container_width=True, hide_index=True)
            for imp in imports:
                if imp["rejected_rows"] > 0:
                    with st.expander(f"Erros do lote #{imp['id']} ({imp['original_filename']})"):
                        errors = api_client.get_import_errors(imp["id"])
                        st.dataframe(errors[:50], use_container_width=True)
        else:
            st.info("Nenhuma importação realizada.")
    except Exception as e:
        st.error(f"Erro: {e}")
