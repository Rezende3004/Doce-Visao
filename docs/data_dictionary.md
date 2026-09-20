# Dicionario de Dados — DoceVisao

Este documento descreve todas as tabelas do banco de dados DoceVisao, seus campos, tipos e regras.

O banco segue o padrao **Star Schema**: tabelas de dimensao (reference) e tabelas de fato (eventos), mais tabelas de suporte para operacao de importacao.

---

## 1. import_batches

Registra cada lote de importacao de dados realizado no sistema.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|:-----------:|-----------|
| `id` | INTEGER | Sim | Chave primaria, auto-incremento. |
| `import_type` | VARCHAR(50) | Sim | Tipo da importacao: `"sales"` ou `"production"`. |
| `original_filename` | VARCHAR(255) | Sim | Nome original do arquivo enviado pelo usuario. |
| `file_hash` | VARCHAR(64) | Sim | Hash SHA-256 do conteudo do arquivo. Valor unico — usado para deteccao de duplicatas. |
| `status` | VARCHAR(50) | Sim | Status do lote: `"pending"`, `"processing"`, `"completed"` ou `"failed"`. |
| `total_rows` | INTEGER | Sim | Numero total de linhas de dados no arquivo (excluindo cabecalho). |
| `accepted_rows` | INTEGER | Sim | Numero de linhas aceitas e persistidas com sucesso. |
| `rejected_rows` | INTEGER | Sim | Numero de linhas rejeitadas por erro de validacao. |
| `error_message` | TEXT | Nao | Mensagem de erro geral, preenchida em caso de falha total do lote. |
| `created_at` | DATETIME | Sim | Data e hora de criacao do lote (preenchido automaticamente pelo banco). |
| `completed_at` | DATETIME | Nao | Data e hora de conclusao do processamento. Nulo enquanto em processamento. |

**Relacionamentos:**
- `import_errors.import_batch_id` -> `import_batches.id` (1:N)
- `fact_sales.import_batch_id` -> `import_batches.id` (1:N)
- `fact_production.import_batch_id` -> `import_batches.id` (1:N)

---

## 2. import_errors

Registra os erros individuais de cada linha rejeitada durante uma importacao.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|:-----------:|-----------|
| `id` | INTEGER | Sim | Chave primaria, auto-incremento. |
| `import_batch_id` | INTEGER | Sim | Chave estrangeira para `import_batches.id`. Identifica o lote da importacao. |
| `row_number` | INTEGER | Sim | Numero da linha no arquivo original (1-indexed, considerando linha 1 como cabecalho). |
| `field_name` | VARCHAR(100) | Nao | Nome do campo com erro, quando aplicavel. Nulo para erros genericos da linha. |
| `error_message` | TEXT | Sim | Descricao do erro encontrado (ex: "Data invalida: 32/13/2025"). |
| `raw_data` | TEXT | Nao | Conteudo bruto da linha com erro, em formato de dicionario stringificado. |

**Relacionamentos:**
- `import_errors.import_batch_id` -> `import_batches.id` (N:1)

---

## 3. dim_products

Tabela de dimensao contendo os produtos comercializados pela doceria. Populada automaticamente durante a importacao.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|:-----------:|-----------|
| `id` | INTEGER | Sim | Chave primaria, auto-incremento. |
| `name` | VARCHAR(255) | Sim | Nome original do produto conforme informado na primeira importacao (ex: "Bolo de Chocolate"). |
| `normalized_name` | VARCHAR(255) | Sim | Nome normalizado (trim + lowercase) para deteccao de duplicatas. Valor unico. |
| `category` | VARCHAR(100) | Sim | Categoria do produto (ex: "Bolos", "Doces", "Salgados", "Tortas"). |
| `active` | BOOLEAN | Sim | Indica se o produto esta ativo. Padrao: `true`. |
| `created_at` | DATETIME | Sim | Data e hora de criacao do registro. |
| `updated_at` | DATETIME | Sim | Data e hora da ultima atualizacao. Atualizado automaticamente. |

**Relacionamentos:**
- `fact_sales.product_id` -> `dim_products.id` (N:1)
- `fact_production.product_id` -> `dim_products.id` (N:1)

**Indices:**
- `normalized_name` — UNIQUE

---

## 4. dim_dates

Tabela de dimensao contendo as datas referenciadas nas vendas e producao. Populada automaticamente durante a importacao conforme novas datas aparecem.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|:-----------:|-----------|
| `id` | INTEGER | Sim | Chave primaria, auto-incremento. |
| `full_date` | DATE | Sim | Data completa (ex: 2025-03-15). Valor unico. |
| `day` | INTEGER | Sim | Dia do mes (1-31). |
| `month` | INTEGER | Sim | Mes do ano (1-12). |
| `month_name` | VARCHAR(50) | Sim | Nome do mes em portugues (ex: "Janeiro", "Fevereiro"). |
| `quarter` | INTEGER | Sim | Trimestre do ano (1-4). |
| `year` | INTEGER | Sim | Ano (ex: 2025). |
| `weekday_number` | INTEGER | Sim | Dia da semana como numero (0=Segunda, 6=Domingo). |
| `weekday_name` | VARCHAR(50) | Sim | Nome do dia da semana em portugues (ex: "Segunda-feira"). |
| `is_weekend` | BOOLEAN | Sim | Indica se e fim de semana (sabado ou domingo). |

**Relacionamentos:**
- `fact_sales.date_id` -> `dim_dates.id` (N:1)
- `fact_production.date_id` -> `dim_dates.id` (N:1)

**Indices:**
- `full_date` — UNIQUE

---

## 5. dim_channels

Tabela de dimensao contendo os canais de venda. Populada automaticamente durante a importacao de vendas.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|:-----------:|-----------|
| `id` | INTEGER | Sim | Chave primaria, auto-incremento. |
| `name` | VARCHAR(255) | Sim | Nome original do canal (ex: "Balcão", "WhatsApp", "iFood"). |
| `normalized_name` | VARCHAR(255) | Sim | Nome normalizado (trim + lowercase) para deteccao de duplicatas. Valor unico. |

**Relacionamentos:**
- `fact_sales.channel_id` -> `dim_channels.id` (N:1, opcional)

**Indices:**
- `normalized_name` — UNIQUE

---

## 6. fact_sales

Tabela de fatos contendo os registros individuais de venda. Cada linha representa um item de um pedido.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|:-----------:|-----------|
| `id` | INTEGER | Sim | Chave primaria, auto-incremento. |
| `external_order_id` | VARCHAR(100) | Sim | Identificador externo do pedido conforme informado no arquivo (ex: "PED-1000"). |
| `external_item_id` | VARCHAR(200) | Sim | Identificador externo do item. Se nao fornecido, e gerado automaticamente via hash MD5. |
| `product_id` | INTEGER | Sim | Chave estrangeira para `dim_products.id`. |
| `date_id` | INTEGER | Sim | Chave estrangeira para `dim_dates.id`. |
| `channel_id` | INTEGER | Nao | Chave estrangeira para `dim_channels.id`. Nulo se o canal nao foi informado. |
| `payment_method` | VARCHAR(100) | Nao | Forma de pagamento (ex: "PIX", "Dinheiro", "Cartao Credito"). |
| `quantity` | INTEGER | Sim | Quantidade de unidades vendidas do produto neste item. |
| `unit_price_cents` | INTEGER | Sim | Preco unitario em centavos (ex: 2500 = R$ 25,00). |
| `discount_cents` | INTEGER | Sim | Desconto aplicado em centavos. Padrao: 0. |
| `unit_cost_cents` | INTEGER | Nao | Custo unitario em centavos. Nulo se nao informado. Usado para calculo de margem. |
| `total_cents` | INTEGER | Sim | Valor total do item em centavos, calculado como `(quantity * unit_price_cents) - discount_cents`. |
| `status` | VARCHAR(50) | Sim | Status normalizado da venda: `"completed"`, `"cancelled"` ou `"pending"`. |
| `import_batch_id` | INTEGER | Sim | Chave estrangeira para `import_batches.id`. Identifica o lote de importacao. |
| `created_at` | DATETIME | Sim | Data e hora de criacao do registro. |

**Relacionamentos:**
- `fact_sales.product_id` -> `dim_products.id` (N:1)
- `fact_sales.date_id` -> `dim_dates.id` (N:1)
- `fact_sales.channel_id` -> `dim_channels.id` (N:1, opcional)
- `fact_sales.import_batch_id` -> `import_batches.id` (N:1)

**Constraints:**
- UNIQUE(`external_order_id`, `external_item_id`) — Garante que um item de pedido nao seja duplicado.

**Indices:**
- `ix_sale_date` — `date_id`
- `ix_sale_product` — `product_id`
- `ix_sale_channel` — `channel_id`
- `ix_sale_status` — `status`
- `ix_sale_batch` — `import_batch_id`

---

## 7. fact_production

Tabela de fatos contendo os registros diarios de producao. Cada linha representa a producao de um produto em um dia.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|:-----------:|-----------|
| `id` | INTEGER | Sim | Chave primaria, auto-incremento. |
| `product_id` | INTEGER | Sim | Chave estrangeira para `dim_products.id`. |
| `date_id` | INTEGER | Sim | Chave estrangeira para `dim_dates.id`. |
| `produced_quantity` | INTEGER | Sim | Quantidade de unidades produzidas no dia. |
| `sold_quantity` | INTEGER | Sim | Quantidade de unidades vendidas no dia. |
| `discarded_quantity` | INTEGER | Sim | Quantidade de unidades descartadas no dia. |
| `discard_reason` | VARCHAR(255) | Nao | Motivo do descarte (ex: "Validade", "Qualidade", "Excedente"). |
| `import_batch_id` | INTEGER | Sim | Chave estrangeira para `import_batches.id`. |
| `created_at` | DATETIME | Sim | Data e hora de criacao do registro. |

**Relacionamentos:**
- `fact_production.product_id` -> `dim_products.id` (N:1)
- `fact_production.date_id` -> `dim_dates.id` (N:1)
- `fact_production.import_batch_id` -> `import_batches.id` (N:1)

**Indices:**
- `ix_prod_date` — `date_id`
- `ix_prod_product` — `product_id`
- `ix_prod_batch` — `import_batch_id`

---

## Diagrama Entidade-Relacionamento

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  dim_products   │       │   dim_dates     │       │  dim_channels   │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ name            │       │ full_date (UQ)  │       │ name            │
│ normalized_name │       │ day             │       │ normalized_name │
│ category        │       │ month           │       └────────┬────────┘
│ active          │       │ month_name      │                │
│ created_at      │       │ quarter         │                │
│ updated_at      │       │ year            │                │
└───────┬─────────┘       │ weekday_number  │                │
        │                 │ weekday_name    │                │
        │                 │ is_weekend      │                │
        │                 └────────┬────────┘                │
        │                          │                         │
        │         ┌────────────────┴─────────────────┐       │
        │         │          fact_sales              │       │
        │         ├──────────────────────────────────┤       │
        ├────────>│ product_id (FK)                  │       │
                  │ date_id (FK)       <─────────────┤       │
                  │ channel_id (FK, nullable) ───────┼───────┘
                  │ id (PK)                          │
                  │ external_order_id                │
                  │ external_item_id                 │
                  │ payment_method                   │
                  │ quantity                         │
                  │ unit_price_cents                 │
                  │ discount_cents                   │
                  │ unit_cost_cents                  │
                  │ total_cents                      │
                  │ status                           │
                  │ import_batch_id (FK) ──┐         │
                  │ created_at             │         │
                  └────────────────────────┼─────────┘
                                           │
        ┌──────────────────────────────────┼─────────────────────────────┐
        │                                  │                             │
        │         ┌────────────────────────┴──────────────┐              │
        │         │          fact_production              │              │
        │         ├───────────────────────────────────────┤              │
        │         │ id (PK)                               │              │
        │         │ product_id (FK) ──────────────────────┼── (dim_products)
        │         │ date_id (FK) ─────────────────────────┼── (dim_dates)
        │         │ produced_quantity                     │
        │         │ sold_quantity                         │
        │         │ discarded_quantity                    │
        │         │ discard_reason                        │
        │         │ import_batch_id (FK) ─┐               │
        │         │ created_at            │               │
        │         └───────────────────────┼───────────────┘
        │                                 │
        │         ┌───────────────────────┴───────────────┐
        │         │         import_batches                │
        │         ├───────────────────────────────────────┤
        └────────>│ id (PK)                               │
                  │ import_type                           │
                  │ original_filename                     │
                  │ file_hash (UQ)                        │
                  │ status                                │
                  │ total_rows                            │
                  │ accepted_rows                         │
                  │ rejected_rows                         │
                  │ error_message                         │
                  │ created_at                            │
                  │ completed_at                          │
                  └───────────────────┬───────────────────┘
                                      │
                  ┌───────────────────┴───────────────────┐
                  │         import_errors                 │
                  ├───────────────────────────────────────┤
                  │ id (PK)                               │
                  │ import_batch_id (FK)                  │
                  │ row_number                            │
                  │ field_name                            │
                  │ error_message                         │
                  │ raw_data                              │
                  └───────────────────────────────────────┘
```
