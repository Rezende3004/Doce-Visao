# KPIs e Indicadores — DoceVisao

Este documento descreve todos os indicadores calculados pelo DoceVisao, suas formulas, proposito e limitacoes.

---

## 1. Faturamento

**Formula:**
```
faturamento = SUM(total_cents) WHERE status = 'completed'
```

Soma dos valores totais de todos os itens de venda com status "concluido" no periodo selecionado. O valor total de cada item e calculado como:
```
total_cents = (quantity * unit_price_cents) - discount_cents
```

**Proposito:**
Indicador principal de receita da doceria. Permite acompanhar o volume de dinheiro entrando no negocio ao longo do tempo e comparar periodos.

**Limitacoes:**
- Nao desconta custos operacionais (aluguel, funcionarios, utilities). Para lucro real, e necessario cruzar com dados de custo.
- Inclui vendas com desconto, mas nao diferencia promocoes de descontos pontuais.
- Depende da qualidade dos dados importados — valores incorretos no arquivo geram faturamento incorreto.
- Valores em centavos (inteiros) evitam erros de ponto flutuante, mas a precisao depende da exatidao do dado de entrada.

---

## 2. Pedidos

**Formula:**
```
num_pedidos = COUNT(DISTINCT external_order_id) WHERE status = 'completed'
```

Conta o numero de pedidos unicos (identificados por `external_order_id`) que possuem pelo menos um item com status "concluido".

**Proposito:**
Volume de transacoes da doceria. Util para dimensionar capacidade operacional (atendimento, producao) e avaliar frequencia de clientes.

**Limitacoes:**
- Um pedido e contado uma unica vez, independente do numero de itens.
- Se um pedido tem itens "completed" e "cancelled", ele conta como um pedido valido (pelo menos um item concluido).
- O identificador de pedido vem do arquivo importado — se o sistema de origem do usuario gera IDs duplicados ou inconsistentes, a contagem sera afetada.

---

## 3. Ticket Medio

**Formula:**
```
ticket_medio = faturamento // num_pedidos
```

Divisao inteira do faturamento total pelo numero de pedidos. Resultado em centavos.

**Proposito:**
Valor medio gasto por pedido. Indica o poder de compra dos clientes e ajuda a avaliar estrategias de upsell e cross-sell.

**Limitacoes:**
- E uma media aritmetica simples — nao considera distribuicao. Um ticket medio de R$ 30,00 pode esconder uma mistura de pedidos de R$ 5,00 e R$ 200,00.
- Sensivel a pedidos extremos (muito altos ou muito baixos).
- Nao diferencia canais — o ticket medio do balcão pode ser muito diferente do iFood, mas o KPI agrega tudo.

---

## 4. Itens Vendidos

**Formula:**
```
itens_vendidos = SUM(quantity) WHERE status = 'completed'
```

Soma das quantidades de todos os itens de venda com status "concluido".

**Proposito:**
Volume total de unidades vendidas. Util para planejamento de producao e reposicao de insumos.

**Limitacoes:**
- Nao diferencia produtos — 100 unidades pode ser 100 brigadeiros (baratos) ou 100 bolos (caros).
- Nao considera devolucoes posteriores a venda.
- Depende da granularidade do dado — se o arquivo agrupa itens, a contagem sera imprecisa.

---

## 5. Margem de Lucro

**Formula:**
```
margem_cents = faturamento_cents - custo_total_cents
margem_percentual = (margem_cents / faturamento_cents) * 100
```

Onde:
```
custo_total_cents = SUM(unit_cost_cents * quantity) WHERE unit_cost_cents IS NOT NULL AND status = 'completed'
```

**Proposito:**
Indicador de rentabilidade. Mostra quanto do faturamento sobra apos cobrir o custo direto dos produtos vendidos.

**Limitacoes:**
- **Cobertura de custos:** O calculo considera apenas vendas que possuem `unit_cost_cents` preenchido. Se apenas 60% das vendas tem custo informado, a margem e calculada sobre esse subconjunto, nao sobre o total.
- **Custo incompleto:** O `unit_cost_cents` representa apenas o custo direto do produto. Nao inclui custos fixos (aluguel, funcionarios) nem variaveis indiretos (embalagem, entrega).
- **Margem real vs. marginal:** O indicador mostra margem contribuitiva, nao margem liquida.
- O sistema exibe o **coverage_percentual** para alertar quando a cobertura de custos e insuficiente (< 50%).

---

## 6. Desperdicio

**Formula:**
```
waste_rate = (discarded_quantity / produced_quantity) * 100
```

Calculado por produto, somando todas as entradas de producao no periodo filtrado.

**Proposito:**
Identificar quais produtos geram mais desperdicio e em que proporcao. Essencial para docerias, onde produtos pereiveis nao vendidos sao perdidos.

**Limitacoes:**
- Depende da importacao de dados de producao — sem eles, o indicador nao esta disponivel.
- Nao diferencia motivos de descarte no calculo da taxa agregada (embora o motivo seja registrado por linha).
- Nao considera desperdicio de insumos, apenas de produto final.
- Se `produced_quantity` for zero para um produto, a taxa e definida como 0% (evita divisao por zero).

---

## 7. Crescimento Periodico

**Formula:**
```
crescimento_percentual = ((faturamento_atual - faturamento_anterior) / faturamento_anterior) * 100
```

Onde:
- `faturamento_atual` = faturamento no periodo selecionado (start_date ate end_date)
- `faturamento_anterior` = faturamento no periodo de mesma duracao imediatamente anterior

O periodo anterior e calculado como:
```
duracao = end_date - start_date + 1 (em dias)
prev_end = start_date - 1 dia
prev_start = prev_end - (duracao - 1) dias
```

**Proposito:**
Avaliar a tendencia do faturamento comparando o periodo atual com o anterior de mesma duracao. Permite identificar crescimento, estagnacao ou queda.

**Limitacoes:**
- **Sazonalidade:** Comparar com o periodo imediatamente anterior nao captura sazonalidade anual. Comparar janeiro com dezembro pode mostrar queda que e apenas sazonal.
- **Sem dados anteriores:** Se nao ha dados no periodo anterior, o crescimento e `null` (nao exibido).
- **Periodos curtos:** Em periodos muito curtos (1-2 dias), a variabilidade natural e alta e o indicador pode ser enganoso.
- **Casos extremos:** Se o faturamento anterior foi zero e o atual e positivo, o resultado e `inf` (infinito). Se ambos sao zero, o resultado e `null`.
- **Nao ajusta calendario:** Nao considera diferencias entre dias uteis e fins de semana nos periodos comparados.

---

## 8. Participacao de Categoria (Share)

**Formula:**
```
share_percentual = (faturamento_categoria / faturamento_total) * 100
```

**Proposito:**
Mostrar a contribuicao de cada categoria de produto para o faturamento total. Identificar concentracao de receita.

**Limitacoes:**
- Soma todas as vendas do periodo — nao diferencia canais ou tendencias temporais dentro da categoria.
- Se uma categoria representa > 50% do faturamento, o sistema gera um insight de atencao sobre concentracao de risco.

---

## 9. Cobertura de Custos

**Formula:**
```
coverage_percentual = (vendas_com_custo / total_vendas) * 100
```

Onde `vendas_com_custo` e a quantidade de registros em `fact_sales` que possuem `unit_cost_cents` nao nulo.

**Proposito:**
Indicador de qualidade dos dados. Mostra qual percentual das vendas possui informacao de custo, permitindo avaliar a confiabilidade da analise de margem.

**Limitacoes:**
- E um meta-indicador — nao mede o negocio, mede a qualidade da base de dados.
- Cobertura baixa (< 50%) significa que a margem calculada pode nao ser representativa.

---

## Resumo Visual

| KPI | Formula Simplificada | Unidade | Disponibilidade |
|-----|---------------------|---------|-----------------|
| Faturamento | SUM(total) | R$ | Sempre (com dados de vendas) |
| Pedidos | COUNT(DISTINCT pedido) | Inteiro | Sempre (com dados de vendas) |
| Ticket Medio | Faturamento / Pedidos | R$ | Sempre (com dados de vendas) |
| Itens Vendidos | SUM(quantidade) | Inteiro | Sempre (com dados de vendas) |
| Margem | Faturamento - Custo | R$ / % | Apenas com custo unitario |
| Desperdicio | Descartado / Produzido | % | Apenas com dados de producao |
| Crescimento | (Atual - Anterior) / Anterior | % | Apenas com filtro de data |
| Share Categoria | Fat. Categoria / Fat. Total | % | Sempre (com dados de vendas) |
| Cobertura Custos | Vendas c/ custo / Total | % | Sempre (com dados de vendas) |

---

## Filtros Globais

Todos os KPIs podem ser filtrados por:

| Filtro | Descricao |
|--------|-----------|
| `start_date` / `end_date` | Periodo de referencia (baseado em `dim_dates.full_date`) |
| `product_id` | Produto especifico |
| `category` | Categoria de produto |
| `channel_id` | Canal de venda |

Os filtros sao aplicados antes do calculo dos KPIs, permitindo analises segmentadas.
