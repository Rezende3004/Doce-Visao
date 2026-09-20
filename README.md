# DoceVisao

**Sistema de Business Intelligence para docerias de pequeno porte**

---

## Apresentacao do Projeto

O **DoceVisao** e um projeto academico de extensao universitaria desenvolvido para atender uma pequena doceria real (Doceria Catarina). O sistema consolida dados de vendas e producao em um painel interativo de indicadores, permitindo que o proprietario tome decisoes baseadas em dados — sem depender de planilhas manuais ou intuicao.

O projeto foi concebido para demonstrar a aplicacao pratica de conceitos de Engenharia de Software, Ciencia de Dados e Business Intelligence em um cenario real de pequeno negocio, atendendo aos requisitos de avaliacao de extensao universitaria.

## Problema Resolvido

Pequenas docerias operam com registros fragmentados de vendas e producao, geralmente em cadernos ou planilhas simples. Isso gera:

- **Falta de visao sobre faturamento real** — o proprietario nao sabe quanto fatura por periodo, produto ou canal.
- **Desperdicio nao mensurado** — sem controle de producao versus vendas, perdas passam despercebidas.
- **Decisoes no "achismo"** — reposicao de estoque, precificacao e planejamento de producao sao feitos sem base em dados.
- **Impossibilidade de comparar periodos** — sem historico estruturado, nao ha como avaliar crescimento ou sazonalidade.

O DoceVisao resolve esses problemas centralizando dados de vendas e producao em um banco estruturado, calculando KPIs automaticamente e apresentando tudo em um painel visual acessivel.

## Funcionalidades

- **Importacao de dados** — Upload de arquivos CSV/Excel de vendas e producao com validacao linha a linha, preview antes da confirmacao e deteccao de duplicatas.
- **Dashboard de KPIs** — Faturamento, pedidos, ticket medio, itens vendidos e crescimento versus periodo anterior.
- **Analise de produtos** — Ranking por quantidade e faturamento, desempenho por categoria, margem de lucro e cobertura de custos.
- **Analise temporal** — Evolucao diaria do faturamento, vendas por dia da semana e distribuicao por canal de venda.
- **Analise de producao** — Indicadores de desperdicio por produto, taxa de descarte e motivos.
- **Insights automaticos** — Geracao de analises narrativas baseadas em regras deterministicas (sem LLM), com recomendacoes acionaveis.
- **Exportacao de dados** — Download de vendas filtradas em formato CSV.
- **Modelos de importacao** — Templates CSV prontos para download com as colunas esperadas.
- **Dados sinteticos** — Gerador de dados de demonstracao para testes e apresentacoes.

## Arquitetura

O projeto segue um **monorepo** com separacao clara entre backend e frontend:

```
PI-DoceriaCatarina/
├── backend/          # API FastAPI + dominio + infraestrutura
├── frontend/         # Interface Streamlit
├── scripts/          # Scripts auxiliares (gerador de dados)
├── sample_data/      # Dados sinteticos de demonstracao
├── docs/             # Documentacao do projeto
├── docker-compose.yml
├── pyproject.toml
├── alembic.ini
└── Makefile
```

O backend e organizado em camadas (Domain, Application, Infrastructure, Presentation) seguindo principios de Clean Architecture adaptados. O frontend Streamlit consome a API via HTTP. O banco de dados e SQLite para simplicidade operacional.

Para detalhes completos, consulte [docs/architecture.md](docs/architecture.md).

## Stack Tecnologica

| Componente       | Tecnologia                          |
|------------------|-------------------------------------|
| Backend          | Python 3.11+, FastAPI, SQLAlchemy 2 |
| Frontend         | Streamlit, Plotly, httpx            |
| Banco de Dados   | SQLite                              |
| Migracoes        | Alembic                             |
| Validacao        | Pydantic 2, Pandera                 |
| Processamento    | Pandas, openpyxl                    |
| Testes           | pytest, pytest-cov, ruff            |
| Containerizacao  | Docker, Docker Compose              |

## Pre-requisitos

- **Python 3.11+** (para execucao local)
- **Docker e Docker Compose** (para execucao via containers)
- **pip** (gerenciador de pacotes Python)

## Execucao via Docker

A forma mais simples de executar o projeto:

```bash
# Subir todos os servicos
docker compose up --build -d

# Ou via Makefile
make docker-up
```

O backend ficara disponivel em `http://localhost:8000` e o frontend em `http://localhost:8501`.

```bash
# Parar os servicos
docker compose down

# Ou via Makefile
make docker-down
```

## Execucao Local

### 1. Clone o repositorio

```bash
git clone <url-do-repositorio>
cd PI-DoceriaCatarina
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv .venv

# Linux/macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### 3. Instale as dependencias

```bash
pip install -e ".[dev]"

# Ou via Makefile:
make install
```

### 4. Configure as variaveis de ambiente

```bash
cp .env.example .env
# Edite o .env conforme necessario
```

### 5. Execute as migracoes do banco de dados

```bash
alembic upgrade head

# Ou via Makefile:
make migrate
```

### 6. Inicie o backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ou via Makefile:
make run-backend
```

### 7. Inicie o frontend (em outro terminal)

```bash
streamlit run frontend/app.py --server.port 8501

# Ou via Makefile:
make run-frontend
```

Acesse `http://localhost:8501` no navegador.

## Testes

```bash
# Executar todos os testes
pytest backend/tests -v

# Ou via Makefile:
make test

# Com relatorio de cobertura
pytest backend/tests --cov=backend/app --cov-report=term-missing

# Ou via Makefile:
make coverage
```

### Lint e formatacao

```bash
# Verificar estilo de codigo
ruff check backend/ frontend/
ruff format --check backend/ frontend/

# Ou via Makefile:
make lint

# Corrigir automaticamente
ruff check --fix backend/ frontend/
ruff format backend/ frontend/

# Ou via Makefile:
make format
```

## Importacao de Dados

### Dados de demonstracao

O projeto inclui um gerador de dados sinteticos:

```bash
python scripts/generate_sample_data.py

# Ou via Makefile:
make seed
```

Isso gera tres arquivos em `sample_data/`:
- `vendas_sinteticas.csv` — ~2.000 registros de vendas (jan-jul/2025)
- `producao_sintetica.csv` — registros diarios de producao
- `vendas_com_erros.csv` — arquivo com erros para testar validacao

### Importacao via interface

1. Acesse a pagina **Importacao** no menu lateral do frontend.
2. Selecione o tipo de importacao (Vendas ou Producao).
3. Faca upload do arquivo CSV ou Excel.
4. Revise o preview com validos e invalidos.
5. Confirme a importacao.

### Formato dos arquivos

**Vendas** — colunas obrigatorias: `data_venda`, `id_pedido`, `produto`, `categoria`, `quantidade`, `valor_unitario`, `status`

**Producao** — colunas obrigatorias: `data`, `produto`, `categoria`, `quantidade_produzida`, `quantidade_vendida`, `quantidade_descartada`

Templates prontos podem ser baixados diretamente na interface de importacao ou via API:
- `GET /api/v1/imports/templates/sales`
- `GET /api/v1/imports/templates/production`

## Estrutura do Projeto

```
PI-DoceriaCatarina/
├── backend/
│   ├── alembic/                    # Migracoes do banco de dados
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── main.py                 # Ponto de entrada FastAPI
│   │   ├── config.py               # Configuracoes (pydantic-settings)
│   │   ├── domain/                 # Camada de dominio
│   │   │   ├── entities/           # Entidades (dataclasses puras)
│   │   │   ├── value_objects/      # Money, SaleStatus
│   │   │   ├── services/           # Logica de negocio pura
│   │   │   ├── repositories/       # Contratos de repositorio
│   │   │   └── exceptions/         # Excecoes de dominio
│   │   ├── application/            # Camada de aplicacao
│   │   │   ├── dto/                # Data Transfer Objects
│   │   │   ├── ports/              # Interfaces de servico
│   │   │   └── use_cases/          # Casos de uso (insights engine)
│   │   ├── infrastructure/         # Camada de infraestrutura
│   │   │   ├── database/           # Conexao e modelos ORM
│   │   │   ├── repositories/       # Implementacoes SQLAlchemy
│   │   │   ├── importers/          # Logica de importacao de arquivos
│   │   │   └── exporters/          # Logica de exportacao
│   │   └── presentation/           # Camada de apresentacao
│   │       └── api/
│   │           ├── routes/         # Endpoints FastAPI
│   │           ├── schemas/        # Schemas Pydantic
│   │           ├── dependencies.py # Injecao de dependencias
│   │           └── exception_handlers.py
│   ├── tests/
│   │   ├── unit/                   # Testes de dominio
│   │   ├── integration/            # Testes de repositorios
│   │   └── api/                    # Testes de endpoints
│   └── Dockerfile
├── frontend/
│   ├── app.py                      # Pagina inicial Streamlit
│   ├── pages/                      # Paginas do dashboard
│   │   ├── 1_Visao_Geral.py
│   │   ├── 2_Produtos.py
│   │   ├── 3_Canais_Periodos.py
│   │   ├── 4_Producao_DesPerdicio.py
│   │   ├── 5_Insights.py
│   │   ├── 6_Importacao.py
│   │   └── 7_Sobre_Indicadores.py
│   ├── services/
│   │   └── api_client.py           # Cliente HTTP da API
│   ├── components/                 # Componentes reutilizaveis
│   ├── utils/                      # Utilitarios
│   ├── assets/                     # Recursos estaticos
│   └── Dockerfile
├── scripts/
│   └── generate_sample_data.py     # Gerador de dados sinteticos
├── sample_data/                    # Dados gerados (gitignored)
├── docs/                           # Documentacao
│   ├── architecture.md
│   ├── requirements.md
│   ├── data_dictionary.md
│   ├── kpis.md
│   ├── api.md
│   ├── academic_report_template.md
│   └── extension_evidence_checklist.md
├── docker-compose.yml
├── pyproject.toml
├── alembic.ini
├── Makefile
├── .env.example
└── .gitignore
```

## Limitacoes Conhecidas

- **Sem autenticacao** — o sistema nao possui controle de acesso ou multi-usuario. Qualquer pessoa com acesso a URL pode usar o sistema e importar dados.
- **SQLite** — banco de dados embarcado, nao adequado para acesso concorrente de alta escala. Suficiente para o cenario de uma unica doceria.
- **Dados sinteticos** — os dados de demonstracao sao gerados aleatoriamente e nao representam vendas reais. O sistema esta pronto para receber dados reais via importacao.
- **Monetario em centavos** — todos os valores monetarios sao armazenados em centavos (inteiros) para evitar problemas de ponto flutuante. A conversao para reais e feita apenas na apresentacao.
- **Insights baseados em regras** — o motor de insights usa regras deterministicas pre-definidas, nao inteligencia artificial. Isso garante previsibilidade mas limita a profundidade das analises.
- **Sem agendamento** — a importacao de dados e manual. Nao ha integracao automatica com sistemas de PDV ou plataformas de delivery.
- **Sem persistencia de sessao** — filtros e selecoes do frontend nao sao persistidos entre recarregamentos da pagina.

## Roadmap

### Versao 1.1 — Curto prazo
- [ ] Autenticacao basica com login/senha para o proprietario
- [ ] Exportacao de relatorios em PDF
- [ ] Filtro por forma de pagamento
- [ ] Grafico de Pareto de produtos (curva ABC)

### Versao 1.2 — Medio prazo
- [ ] Migracao para PostgreSQL
- [ ] Integracao com API do iFood para importacao automatica
- [ ] Alertas automaticos por e-mail (desperdicio alto, queda de faturamento)
- [ ] Previsao de demanda baseada em media movel

### Versao 2.0 — Longo prazo
- [ ] Multi-tenancy (multiplos usuarios/docerias)
- [ ] Aplicativo mobile para registro rapido de vendas
- [ ] Integracao com leitor de codigo de barras
- [ ] Modulo de precificacao com sugestao baseada em margem target
- [ ] Dashboard compartilhavel com link publico (somente leitura)

## Licenca

Projeto academico desenvolvido para fins de extensao universitaria.

## Contato

Projeto Integrador — Universidade [inserir nome da instituicao]
