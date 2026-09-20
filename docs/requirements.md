# Especificacao de Requisitos — DoceVisao

Este documento lista os requisitos funcionais, nao funcionais e regras de negocio do sistema DoceVisao.

---

## 1. Requisitos Funcionais

### RF001 — Importacao de dados de vendas
O sistema deve permitir a importacao de dados de vendas a partir de arquivos CSV ou Excel (.xlsx/.xls), contendo no minimo: data da venda, identificador do pedido, nome do produto, categoria, quantidade, valor unitario e status.

### RF002 — Importacao de dados de producao
O sistema deve permitir a importacao de dados de producao a partir de arquivos CSV ou Excel, contendo no minimo: data, nome do produto, categoria, quantidade produzida, quantidade vendida e quantidade descartada.

### RF003 — Preview de importacao
Antes de confirmar a importacao, o sistema deve apresentar um preview com a quantidade de linhas validas, invalidas e os erros encontrados, permitindo que o usuario decida se prossegue.

### RF004 — Deteccao de duplicatas
O sistema deve impedir a importacao de um arquivo ja processado, utilizando hash SHA-256 do conteudo para identificacao.

### RF005 — Validacao linha a linha
O sistema deve validar cada linha do arquivo individualmente, aceitando linhas validas e rejeitando apenas as invalidas, registrando os erros de cada linha rejeitada.

### RF006 — Normalizacao de status de venda
O sistema deve reconhecer e normalizar diferentes representacoes de status (ex: "Concluido", "concluído", "finalizado", "completed", "pago") para um valor canonico.

### RF007 — Registro de erros de importacao
O sistema deve armazenar todos os erros de importacao com numero da linha, campo afetado, mensagem de erro e dados brutos da linha, permitindo consulta posterior.

### RF008 — Exibicao de KPIs do dashboard
O sistema deve exibir os seguintes indicadores no dashboard principal: faturamento total, numero de pedidos, ticket medio e total de itens vendidos, todos filtraveis por periodo.

### RF009 — Calculo de crescimento periodico
O sistema deve calcular automaticamente o percentual de crescimento do faturamento em relacao ao periodo anterior de mesma duracao.

### RF010 — Ranking de produtos
O sistema deve apresentar o ranking de produtos ordenaveis por quantidade vendida ou faturamento, com limite configuravel (padrao: 20).

### RF011 — Desempenho por categoria
O sistema deve apresentar o faturamento e participacao percentual de cada categoria de produto.

### RF012 — Analise de margem
O sistema deve calcular a margem de lucro (faturamento menos custo) e o percentual de cobertura de custos (quantidade de vendas com dado de custo versus total).

### RF013 — Evolucao temporal do faturamento
O sistema deve apresentar um grafico de linha com a evolucao diaria do faturamento no periodo selecionado.

### RF014 — Vendas por dia da semana
O sistema deve apresentar a distribuicao do faturamento e numero de pedidos por dia da semana (segunda a domingo).

### RF015 — Vendas por canal
O sistema deve apresentar a distribuicao do faturamento e numero de pedidos por canal de venda (Balcão, WhatsApp, iFood, etc.).

### RF016 — Analise de desperdicio
O sistema deve apresentar, por produto, as quantidades produzidas, vendidas e descartadas, com a taxa de desperdicio percentual.

### RF017 — Geracao de insights automaticos
O sistema deve gerar insights narrativos baseados em regras deterministicas, cobrindo: dia de maior faturamento, produto mais vendido, maior faturamento, concentracao de categoria, canal principal, crescimento/queda, cobertura de custos e desperdicio.

### RF018 — Exportacao de dados
O sistema deve permitir a exportacao dos dados de vendas filtrados em formato CSV.

### RF019 — Download de modelos de importacao
O sistema deve disponibilizar templates CSV com as colunas esperadas para download, facilitando a preparacao dos dados pelo usuario.

### RF020 — Geracao de dados sinteticos
O sistema deve incluir um script para geracao de dados de demonstracao (vendas, producao e dados com erros) para fins de teste e apresentacao.

---

## 2. Requisitos Nao Funcionais

### RNF001 — Linguagem
Todo o sistema deve ser desenvolvido em Python 3.11 ou superior.

### RNF002 — Interface web
O frontend deve ser uma aplicacao web acessivel via navegador, sem necessidade de instalacao de software no cliente.

### RNF003 — API REST
O backend deve expor uma API REST com respostas em formato JSON, documentada via OpenAPI/Swagger.

### RNF004 — Formato monetario
Todos os valores monetarios devem ser armazenados em centavos (inteiros) para evitar erros de ponto flutuante. A formatacao em Reais deve ocorrer apenas na camada de apresentacao.

### RNF005 — Persistencia
Os dados devem ser persistidos em banco de dados relacional (SQLite para o cenario atual, com possibilidade de migracao para PostgreSQL).

### RNF006 — Migracoes de banco
Todas as alteracoes de schema devem ser gerenciadas via Alembic, com versionamento das migracoes.

### RNF007 — Tratamento de erros
Todas as excecoes de dominio devem ser mapeadas para respostas HTTP apropriadas com mensagens em portugues.

### RNF008 — Testes automatizados
O sistema deve possuir testes unitarios, de integracao e de API com cobertura minima de 80% do codigo backend.

### RNF009 — Qualidade de codigo
O codigo deve seguir padroes de estilo verificados automaticamente via ruff (lint e formatacao).

### RNF010 — Containerizacao
O sistema deve ser executavel via Docker Compose com um unico comando, incluindo backend, frontend e banco de dados.

---

## 3. Regras de Negocio

### RN001 — Apenas vendas concluidas nos KPIs
Somente vendas com status "completed" (concluido) devem ser consideradas no calculo de KPIs (faturamento, pedidos, ticket medio, itens vendidos).

### RN002 — Canceladas excluidas
Vendas com status "cancelled" (cancelado) devem ser excluidas de todos os calculos de KPIs e dashboards.

### RN003 — Valores nao negativos
Quantidades e valores monetarios nao podem ser negativos. Linhas com valores negativos devem ser rejeitadas na importacao.

### RN004 — Data valida
Datas devem estar no intervalo de 01/01/2000 ate a data atual. Datas fora desse intervalo ou em formato invalido devem ser rejeitadas.

### RN005 — Campos obrigatorios de vendas
Os campos `data_venda`, `id_pedido`, `produto`, `categoria`, `quantidade`, `valor_unitario` e `status` sao obrigatorios para importacao de vendas.

### RN006 — Campos obrigatorios de producao
Os campos `data`, `produto`, `categoria`, `quantidade_produzida`, `quantidade_vendida` e `quantidade_descartada` sao obrigatorios para importacao de producao.

### RN007 — Campos opcionais de vendas
Os campos `id_item`, `desconto`, `canal`, `forma_pagamento` e `custo_unitario` sao opcionais. Valores ausentes devem ser tratados como zero ou nulo conforme o campo.

### RN008 — Identificador de item unico
A combinacao de `external_order_id` e `external_item_id` deve ser unica na tabela `fact_sales`. Se `id_item` nao for fornecido no arquivo, um deve ser gerado automaticamente.

### RN009 — Normalizacao de nomes
Nomes de produtos e canais devem ser normalizados (trim + lowercase) para deteccao de duplicatas, mas o nome original deve ser preservado na primeira ocorrencia.

### RN010 — Tamanho maximo de upload
Arquivos de importacao nao podem exceder 50MB. Arquivos maiores devem ser rejeitados com mensagem de erro clara.
