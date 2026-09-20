"""Sobre os Indicadores — Glossário de KPIs."""
import streamlit as st

st.set_page_config(page_title="Sobre os Indicadores — DoceVisão", page_icon="📖", layout="wide")
st.title("📖 Sobre os Indicadores")

st.markdown("""
### Faturamento
- **Definição:** Soma do valor total das vendas concluídas no período.
- **Fórmula:** `total = quantidade × valor_unitário - desconto`
- **Utilidade:** Mede o volume de receita gerado.
- **Limitações:** Não considera custos nem devoluções posteriores.

### Quantidade de Pedidos
- **Definição:** Contagem de pedidos distintos com status concluído.
- **Utilidade:** Indica o volume de transações.
- **Limitações:** Um pedido pode conter múltiplos itens.

### Ticket Médio
- **Definição:** Faturamento dividido pela quantidade de pedidos.
- **Fórmula:** `ticket médio = faturamento / pedidos`
- **Utilidade:** Valor médio gasto por pedido.
- **Limitações:** Se não houver pedidos, retorna zero.

### Itens Vendidos
- **Definição:** Soma das quantidades de todas as vendas concluídas.
- **Utilidade:** Volume físico de produtos vendidos.

### Margem Estimada
- **Definição:** Diferença entre faturamento e custo total.
- **Fórmula:** `margem = faturamento - custo_total`
- **Utilidade:** Rentabilidade dos produtos.
- **Limitações:** Calculada apenas para registros com custo unitário informado. A cobertura indica quanto dos dados possui custo.

### Taxa de Desperdício
- **Definição:** Proporção da produção que foi descartada.
- **Fórmula:** `desperdício = descartado / produzido × 100`
- **Utilidade:** Eficiência da produção.
- **Limitações:** Requer dados de produção importados.

### Crescimento entre Períodos
- **Definição:** Comparação do período selecionado com o período anterior de mesma duração.
- **Utilidade:** Tendência de vendas.
- **Limitações:** Se não houver dados suficientes, exibe "dados insuficientes".

### Cancelamentos
- Vendas com status cancelado **não** entram nos KPIs de faturamento, pedidos e itens vendidos.
- Status reconhecidos: Concluído, Finalizado, Pago, Cancelado, Pendente.
""")
