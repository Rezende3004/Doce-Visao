# Documentacao da API — DoceVisao

Base URL: `http://localhost:8000`

Documentacao interativa disponivel em: `http://localhost:8000/docs` (Swagger UI)

---

## Sumario de Endpoints

| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| GET | `/health` | Health check |
| GET | `/api/v1/filters/options` | Opcoes de filtros globais |
| GET | `/api/v1/dashboard/summary` | KPIs do dashboard |
| GET | `/api/v1/sales/timeline` | Evolucao temporal do faturamento |
| GET | `/api/v1/sales/by-weekday` | Vendas por dia da semana |
| GET | `/api/v1/sales/by-channel` | Vendas por canal |
| GET | `/api/v1/products/ranking` | Ranking de produtos |
| GET | `/api/v1/products/categories/performance` | Desempenho por categoria |
| GET | `/api/v1/products/margin` | Margem de lucro |
| GET | `/api/v1/products/filters/options` | Opcoes de filtros (produtos) |
| GET | `/api/v1/production/waste` | Analise de desperdicio |
| GET | `/api/v1/insights` | Insights automaticos |
| GET | `/api/v1/imports` | Listar lotes de importacao |
| GET | `/api/v1/imports/{batch_id}` | Detalhe de um lote |
| GET | `/api/v1/imports/{batch_id}/errors` | Erros de um lote |
| POST | `/api/v1/imports/sales/preview` | Preview de importacao de vendas |
| POST | `/api/v1/imports/sales/confirm` | Confirmar importacao de vendas |
| POST | `/api/v1/imports/production/preview` | Preview de importacao de producao |
| POST | `/api/v1/imports/production/confirm` | Confirmar importacao de producao |
| GET | `/api/v1/imports/templates/sales` | Download modelo de vendas |
| GET | `/api/v1/imports/templates/production` | Download modelo de producao |
| GET | `/api/v1/exports/sales` | Exportar vendas em CSV |

---

## Filtros Globais

A maioria dos endpoints de consulta aceita os seguintes query parameters opcionais:

| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `start_date` | string (YYYY-MM-DD) | Data inicial do periodo |
| `end_date` | string (YYYY-MM-DD) | Data final do periodo |
| `product_id` | integer | ID do produto |
| `category` | string | Nome da categoria |
| `channel_id` | integer | ID do canal de venda |

---

## Endpoints

### Health Check

```
GET /health
```

**Resposta:**
```json
{
  "status": "ok"
}
```

---

### Opcoes de Filtros

```
GET /api/v1/filters/options
```

Retorna as opcoes disponiveis para filtros globais (categorias, produtos e canais).

**Resposta:**
```json
{
  "categories": ["Bolos", "Doces", "Salgados", "Tortas"],
  "products": [
    {"id": 1, "name": "Bolo de Chocolate", "category": "Bolos"},
    {"id": 2, "name": "Brigadeiro", "category": "Doces"}
  ],
  "channels": [
    {"id": 1, "name": "Balcão"},
    {"id": 2, "name": "WhatsApp"}
  ]
}
```

---

### Dashboard Summary

```
GET /api/v1/dashboard/summary
```

Retorna os KPIs principais do dashboard.

**Query Parameters:** Filtros globais opcionais.

**Resposta:**
```json
{
  "faturamento": "R$ 45.230,50",
  "faturamento_cents": 4523050,
  "num_pedidos": 892,
  "ticket_medio": "R$ 50,70",
  "ticket_medio_cents": 5070,
  "itens_vendidos": 2341,
  "faturamento_anterior": "R$ 41.000,00",
  "crescimento_percentual": 10.3
}
```

**Campos:**
- `faturamento` / `faturamento_cents` — Faturamento total formatado e em centavos.
- `num_pedidos` — Numero de pedidos unicos.
- `ticket_medio` / `ticket_medio_cents` — Ticket medio formatado e em centavos.
- `itens_vendidos` — Total de unidades vendidas.
- `faturamento_anterior` — Faturamento do periodo anterior (mesma duracao). Nulo se nao ha dados.
- `crescimento_percentual` — Percentual de crescimento vs. periodo anterior. Nulo se nao ha dados.

---

### Timeline de Vendas

```
GET /api/v1/sales/timeline
```

Retorna a evolucao diaria do faturamento.

**Query Parameters:** Filtros globais opcionais.

**Resposta:**
```json
[
  {
    "date": "2025-01-01",
    "faturamento": "R$ 1.230,00",
    "faturamento_cents": 123000,
    "num_pedidos": 15
  },
  {
    "date": "2025-01-02",
    "faturamento": "R$ 980,50",
    "faturamento_cents": 98050,
    "num_pedidos": 12
  }
]
```

---

### Vendas por Dia da Semana

```
GET /api/v1/sales/by-weekday
```

Retorna a distribuicao do faturamento por dia da semana.

**Query Parameters:** Filtros globais opcionais.

**Resposta:**
```json
[
  {
    "weekday": "Segunda-feira",
    "weekday_number": 0,
    "faturamento": "R$ 5.200,00",
    "faturamento_cents": 520000,
    "num_pedidos": 98
  },
  {
    "weekday": "Terca-feira",
    "weekday_number": 1,
    "faturamento": "R$ 4.800,00",
    "faturamento_cents": 480000,
    "num_pedidos": 91
  }
]
```

---

### Vendas por Canal

```
GET /api/v1/sales/by-channel
```

Retorna a distribuicao do faturamento por canal de venda.

**Query Parameters:** Filtros globais opcionais.

**Resposta:**
```json
[
  {
    "channel_id": 1,
    "channel_name": "Balcão",
    "faturamento": "R$ 18.500,00",
    "faturamento_cents": 1850000,
    "num_pedidos": 420
  },
  {
    "channel_id": 2,
    "channel_name": "WhatsApp",
    "faturamento": "R$ 12.300,00",
    "faturamento_cents": 1230000,
    "num_pedidos": 280
  }
]
```

---

### Ranking de Produtos

```
GET /api/v1/products/ranking
```

Retorna o ranking de produtos por quantidade vendida ou faturamento.

**Query Parameters:**

| Parametro | Tipo | Padrao | Descricao |
|-----------|------|--------|-----------|
| `sort_by` | string | `"quantity"` | Ordenacao: `"quantity"` ou `"revenue"` |
| `limit` | integer | `20` | Numero maximo de resultados (1-100) |
| — | — | — | Filtros globais opcionais |

**Resposta:**
```json
[
  {
    "product_id": 4,
    "product_name": "Brigadeiro",
    "category": "Doces",
    "quantity": 450,
    "faturamento": "R$ 6.750,00",
    "faturamento_cents": 675000
  },
  {
    "product_id": 1,
    "product_name": "Bolo de Chocolate",
    "category": "Bolos",
    "quantity": 320,
    "faturamento": "R$ 9.600,00",
    "faturamento_cents": 960000
  }
]
```

---

### Desempenho por Categoria

```
GET /api/v1/products/categories/performance
```

Retorna o faturamento e participacao de cada categoria.

**Query Parameters:** Filtros globais opcionais.

**Resposta:**
```json
[
  {
    "category": "Bolos",
    "quantity": 800,
    "faturamento": "R$ 24.000,00",
    "faturamento_cents": 2400000,
    "share_percentual": 53.1
  },
  {
    "category": "Doces",
    "quantity": 1200,
    "faturamento": "R$ 15.000,00",
    "faturamento_cents": 1500000,
    "share_percentual": 33.2
  }
]
```

---

### Margem de Lucro

```
GET /api/v1/products/margin
```

Retorna a analise de margem de lucro.

**Query Parameters:** Filtros globais opcionais.

**Resposta:**
```json
{
  "faturamento": "R$ 30.000,00",
  "faturamento_cents": 3000000,
  "custo_total": "R$ 12.000,00",
  "custo_total_cents": 1200000,
  "margem": "R$ 18.000,00",
  "margem_cents": 1800000,
  "margem_percentual": 60.0,
  "coverage_percentual": 65.0
}
```

**Campos:**
- `faturamento` / `faturamento_cents` — Faturamento das vendas com custo informado.
- `custo_total` / `custo_total_cents` — Custo total dessas vendas.
- `margem` / `margem_cents` — Margem absoluta (faturamento - custo).
- `margem_percentual` — Margem como percentual do faturamento.
- `coverage_percentual` — Percentual de vendas que possuem dado de custo.

---

### Analise de Desperdicio

```
GET /api/v1/production/waste
```

Retorna a analise de desperdicio por produto.

**Query Parameters:**

| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `start_date` | string (YYYY-MM-DD) | Data inicial |
| `end_date` | string (YYYY-MM-DD) | Data final |
| `product_id` | integer | ID do produto (opcional) |

**Resposta:**
```json
[
  {
    "product_id": 1,
    "product_name": "Bolo de Chocolate",
    "produced": 500,
    "sold": 420,
    "discarded": 80,
    "waste_rate": 16.0
  },
  {
    "product_id": 8,
    "product_name": "Pão de Queijo",
    "produced": 800,
    "sold": 720,
    "discarded": 80,
    "waste_rate": 10.0
  }
]
```

---

### Insights Automaticos

```
GET /api/v1/insights
```

Retorna insights narrativos gerados automaticamente com base nos dados.

**Query Parameters:** Filtros globais opcionais.

**Resposta:**
```json
[
  {
    "title": "Dia de maior faturamento: Sexta-feira",
    "description": "As dados indicam que Sexta-feira concentra o maior faturamento.",
    "evidence": "Faturamento de R$ 8.500,00 em 180 pedidos.",
    "recommendation": "Vale investigar se ha sazonalidade e planejar producao e equipe para este dia.",
    "level": "informativo",
    "metric_value": 8500.0
  },
  {
    "title": "Taxa de desperdicio elevada",
    "description": "A taxa de desperdicio geral e de 15.2%.",
    "evidence": "320 unidades descartadas de 2100 produzidas.",
    "recommendation": "Revise o planejamento de producao e as causas do desperdicio.",
    "level": "atencao",
    "metric_value": 15.2
  }
]
```

**Niveis de insight:**
- `informativo` — Informacao relevante sem acao urgente.
- `atencao` — Situacao que merece investigacao.
- `oportunidade` — Oportunidade identificada para explorar.

---

### Listar Importacoes

```
GET /api/v1/imports
```

Retorna os lotes de importacao realizados.

**Query Parameters:**

| Parametro | Tipo | Padrao | Descricao |
|-----------|------|--------|-----------|
| `limit` | integer | `50` | Numero maximo de resultados |
| `offset` | integer | `0` | Offset para paginacao |

**Resposta:**
```json
[
  {
    "id": 1,
    "import_type": "sales",
    "original_filename": "vendas_janeiro.csv",
    "file_hash": "a1b2c3d4e5f6...",
    "status": "completed",
    "total_rows": 1500,
    "accepted_rows": 1480,
    "rejected_rows": 20,
    "error_message": null,
    "created_at": "2025-02-01T10:30:00",
    "completed_at": "2025-02-01T10:30:05"
  }
]
```

---

### Detalhe de Importacao

```
GET /api/v1/imports/{batch_id}
```

Retorna os detalhes de um lote especifico.

**Resposta:** Mesmo formato do endpoint de listagem.

**Erros:**
- `404` — Lote nao encontrado.

---

### Erros de Importacao

```
GET /api/v1/imports/{batch_id}/errors
```

Retorna os erros de validacao de um lote especifico.

**Resposta:**
```json
[
  {
    "row_number": 42,
    "field_name": "data_venda",
    "error_message": "Data invalida: 32/13/2025",
    "raw_data": "{'data_venda': '32/13/2025', 'id_pedido': 'ERR-1', ...}"
  }
]
```

---

### Preview de Importacao de Vendas

```
POST /api/v1/imports/sales/preview
Content-Type: multipart/form-data
```

Valida o arquivo e retorna um preview sem persistir dados.

**Body:**
- `file` — Arquivo CSV ou Excel (.xlsx/.xls)

**Resposta:**
```json
{
  "total_rows": 100,
  "valid_rows": 95,
  "invalid_rows": 5,
  "sample_valid": [
    {"data_venda": "01/01/2025", "id_pedido": "PED-1000", "produto": "Bolo de Chocolate", ...}
  ],
  "sample_invalid": [
    {"data_venda": "32/13/2025", "id_pedido": "ERR-1", ...}
  ],
  "errors": [
    {"row": 42, "field": "data_venda", "message": "Data invalida: 32/13/2025"}
  ]
}
```

---

### Confirmar Importacao de Vendas

```
POST /api/v1/imports/sales/confirm
Content-Type: multipart/form-data
```

Importa os dados do arquivo para o banco.

**Body:**
- `file` — Mesmo arquivo enviado no preview

**Resposta:**
```json
{
  "batch_id": 1,
  "status": "completed",
  "total_rows": 100,
  "accepted_rows": 95,
  "rejected_rows": 5
}
```

**Erros:**
- `400` — Arquivo invalido (formato, tamanho, nome ausente)
- `409` — Arquivo ja importado (duplicata detectada pelo hash)
- `422` — Erro de validacao de dominio

---

### Preview de Importacao de Producao

```
POST /api/v1/imports/production/preview
Content-Type: multipart/form-data
```

**Body:**
- `file` — Arquivo CSV ou Excel (.xlsx/.xls)

**Resposta:** Mesmo formato do preview de vendas.

---

### Confirmar Importacao de Producao

```
POST /api/v1/imports/production/confirm
Content-Type: multipart/form-data
```

**Body:**
- `file` — Mesmo arquivo enviado no preview

**Resposta:** Mesmo formato da confirmacao de vendas.

---

### Download de Modelos

```
GET /api/v1/imports/templates/sales
GET /api/v1/imports/templates/production
```

Retorna arquivos CSV vazios com os cabecalhos esperados para importacao.

**Colunas do modelo de vendas:**
`data_venda`, `id_pedido`, `id_item`, `produto`, `categoria`, `quantidade`, `valor_unitario`, `desconto`, `canal`, `forma_pagamento`, `custo_unitario`, `status`

**Colunas do modelo de producao:**
`data`, `produto`, `categoria`, `quantidade_produzida`, `quantidade_vendida`, `quantidade_descartada`, `motivo_descarte`

---

### Exportar Vendas

```
GET /api/v1/exports/sales
```

Exporta dados de vendas filtrados em formato CSV.

**Query Parameters:** Filtros globais opcionais.

**Resposta:** Arquivo CSV com as colunas:
`data`, `pedido`, `produto`, `categoria`, `canal`, `quantidade`, `valor_unitario`, `desconto`, `total`, `status`

**Content-Type:** `text/csv`
**Content-Disposition:** `attachment; filename=export_vendas.csv`

---

## Codigos de Erro

| Codigo | Significado | Causa comum |
|--------|-------------|-------------|
| `400` | Bad Request | Arquivo invalido, formato nao suportado, tamanho excedido |
| `404` | Not Found | Lote de importacao nao encontrado |
| `409` | Conflict | Arquivo ja importado (duplicata) |
| `422` | Unprocessable Entity | Erro de validacao de dominio (status invalido, valor negativo) |
| `500` | Internal Server Error | Erro inesperado no servidor |

**Formato de erro:**
```json
{
  "detail": "Mensagem de erro em portugues"
}
```

---

## Formato de Valores Monetarios

A API retorna valores monetarios em dois formatos:

1. **Formatado** (string): `"R$ 1.234,56"` — Para exibicao direta na interface.
2. **Em centavos** (integer): `123456` — Para processamento e calculos sem erro de ponto flutuante.

Os campos com sufixo `_cents` sao sempre inteiros. Os campos sem sufixo sao strings formatadas em Reais.
