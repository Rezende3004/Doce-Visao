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

# --- State management ---
if "sales_upload_data" not in st.session_state:
    st.session_state.sales_upload_data = None
if "prod_upload_data" not in st.session_state:
    st.session_state.prod_upload_data = None
if "sales_preview_result" not in st.session_state:
    st.session_state.sales_preview_result = None
if "prod_preview_result" not in st.session_state:
    st.session_state.prod_preview_result = None


def handle_sales_preview():
    uploaded = st.session_state.get("_sales_upload_widget")
    if uploaded and st.session_state.sales_upload_data is None:
        content = uploaded.read()
        st.session_state.sales_upload_data = (content, uploaded.name)
        try:
            preview = api_client.preview_sales(content, uploaded.name)
            st.session_state.sales_preview_result = preview
        except Exception as e:
            st.session_state.sales_preview_result = {"error": str(e)}


def handle_prod_preview():
    uploaded = st.session_state.get("_prod_upload_widget")
    if uploaded and st.session_state.prod_upload_data is None:
        content = uploaded.read()
        st.session_state.prod_upload_data = (content, uploaded.name)
        try:
            preview = api_client.preview_production(content, uploaded.name)
            st.session_state.prod_preview_result = preview
        except Exception as e:
            st.session_state.prod_preview_result = {"error": str(e)}


with tab[0]:
    st.subheader("Importar Vendas")
    st.markdown("Baixe o modelo: [modelo_vendas.csv](http://localhost:8000/api/v1/imports/templates/sales)")

    # File uploader with unique key to avoid stale data
    uploaded = st.file_uploader(
        "Selecione o arquivo CSV ou Excel",
        type=["csv", "xlsx"],
        key="sales_upload",
    )

    # Store widget value
    st.session_state["_sales_upload_widget"] = uploaded

    if uploaded:
        if st.button("Prévia", key="sales_preview_btn"):
            handle_sales_preview()

        # Persisted preview display
        preview_result = st.session_state.sales_preview_result
        if preview_result and "error" not in preview_result:
            st.success(f"Total: {preview_result['total_rows']} linhas | Válidas: {preview_result['valid_rows']} | Inválidas: {preview_result['invalid_rows']}")
            if preview_result["errors"]:
                st.warning("Erros encontrados:")
                st.dataframe(preview_result["errors"][:20], use_container_width=True)

            # Confirm button always visible when preview exists
            if st.session_state.sales_upload_data and preview_result["valid_rows"] > 0:
                if st.button("Confirmar Importação", key="sales_confirm_btn", type="primary", use_container_width=True):
                    content, fname = st.session_state.sales_upload_data
                    try:
                        result = api_client.confirm_sales(content, fname)
                        st.success(
                            f"Importação concluída! Lote #{result['batch_id']}: {result['accepted_rows']} aceitas, {result['rejected_rows']} rejeitadas."
                        )
                        # Clear state after success
                        st.session_state.sales_upload_data = None
                        st.session_state.sales_preview_result = None
                    except Exception as e:
                        st.error(f"Erro na confirmação: {e}")
            elif preview_result["valid_rows"] == 0:
                st.warning("Nenhuma linha válida para importar.")
        elif preview_result and "error" in preview_result:
            st.error(f"Erro na prévia: {preview_result['error']}")

with tab[1]:
    st.subheader("Importar Produção")
    st.markdown("Baixe o modelo: [modelo_producao.csv](http://localhost:8000/api/v1/imports/templates/production)")

    uploaded_p = st.file_uploader(
        "Selecione o arquivo CSV ou Excel",
        type=["csv", "xlsx"],
        key="prod_upload",
    )

    st.session_state["_prod_upload_widget"] = uploaded_p

    if uploaded_p:
        if st.button("Prévia", key="prod_preview_btn"):
            handle_prod_preview()

        preview_result = st.session_state.prod_preview_result
        if preview_result and "error" not in preview_result:
            st.success(f"Total: {preview_result['total_rows']} linhas | Válidas: {preview_result['valid_rows']} | Inválidas: {preview_result['invalid_rows']}")
            if preview_result["errors"]:
                st.warning("Erros encontrados:")
                st.dataframe(preview_result["errors"][:20], use_container_width=True)

            if st.session_state.prod_upload_data and preview_result["valid_rows"] > 0:
                if st.button("Confirmar Importação", key="prod_confirm_btn", type="primary", use_container_width=True):
                    content, fname = st.session_state.prod_upload_data
                    try:
                        result = api_client.confirm_production(content, fname)
                        st.success(
                            f"Importação concluída! Lote #{result['batch_id']}: {result['accepted_rows']} aceitas, {result['rejected_rows']} rejeitadas."
                        )
                        st.session_state.prod_upload_data = None
                        st.session_state.prod_preview_result = None
                    except Exception as e:
                        st.error(f"Erro na confirmação: {e}")
            elif preview_result["valid_rows"] == 0:
                st.warning("Nenhuma linha válida para importar.")
        elif preview_result and "error" in preview_result:
            st.error(f"Erro na prévia: {preview_result['error']}")

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
