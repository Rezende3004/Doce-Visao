# Modelo de Relatorio de Extensao Universitaria — DoceVisao

> **Nota:** Este e um modelo estruturado para o relatorio academico de extensao. Os campos entre colchetes `[...]` devem ser preenchidos com os dados reais do projeto. Nao preencher com dados ficticios.

---

## Pagina de Identificacao

**Instituicao:** [Nome da instituicao de ensino]
**Curso:** [Nome do curso]
**Disciplina:** [Nome da disciplina de projeto integrador / extensao]
**Semestre:** [Semestre/Ano]

**Titulo do Projeto:** DoceVisao — Sistema de Business Intelligence para Doceria Catarina
**Equipe:**
- [Nome completo do aluno 1] — [RA/matricula]
- [Nome completo do aluno 2] — [RA/matricula]
- [Nome completo do aluno 3] — [RA/matricula]

**Orientador(a):** [Nome do orientador]
**Empresa/Entidade parceira:** Doceria Catarina — [Cidade/UF]
**Periodo de desenvolvimento:** [Data inicio] a [Data fim]

---

## 1. Resumo

[Escrever um paragrafo de 150-250 palavras resumindo: o problema identificado, a solucao desenvolvida, as tecnologias utilizadas, os resultados alcancados e o impacto para a comunidade atendida.]

**Palavras-chave:** [3-5 palavras-chave, ex: Business Intelligence, Extensao Universitaria, Pequenos Negocios, Dashboard, Ciencia de Dados]

---

## 2. Introducao

### 2.1. Contextualizacao

[Descrever o cenario da doceria parceira: porte, segmento, forma de operacao, principais desafios de gestao. Contextualizar a realidade de pequenos negocios no Brasil e a dificuldade de acesso a ferramentas de analise de dados.]

### 2.2. Problema Identificado

[Descrever o problema concreto que motivou o projeto. Exemplos: falta de controle de faturamento, desperdicio nao mensurado, decisoes baseadas em intuicao, ausencia de historico de vendas estruturado.]

### 2.3. Objetivos

**Objetivo geral:**
[Descrever o objetivo principal do projeto.]

**Objetivos especificos:**
- [Objetivo especifico 1 — ex: Desenvolver um sistema de importacao de dados de vendas]
- [Objetivo especifico 2 — ex: Implementar dashboard com KPIs de faturamento e desperdicio]
- [Objetivo especifico 3 — ex: Capacitar o proprietario na leitura e uso dos indicadores]
- [Objetivo especifico 4 — ex: ...]

### 2.4. Justificativa

[Explicar por que este projeto e relevante: impacto social para o pequeno negocio, aplicacao pratica dos conceitos academicos, contribuicao para a formacao dos alunos, atendimento aos requisitos de extensao universitaria.]

---

## 3. Referencial Teorico

### 3.1. Business Intelligence para Pequenos Negocios

[Discutir conceitos de BI aplicados a pequenos negocios. Citar autores e referencias sobre: tomada de decisao baseada em dados, KPIs, dashboards, indicadores de desempenho.]

### 3.2. Engenharia de Software e Boas Praticas

[Discutir as praticas de engenharia de software aplicadas: Clean Architecture, separacao em camadas, testes automatizados, CI/CD, containerizacao. Citar referencias.]

### 3.3. Modelo Star Schema e Modelagem Dimensional

[Discutir o padrao de modelagem dimensional utilizado no banco de dados. Citar Kimball ou referencias equivalentes.]

### 3.4. Extensao Universitaria

[Discutir o papel da extensao universitaria na formacao do estudante e no impacto social. Citar diretrizes da instituicao e normas de extensao.]

---

## 4. Metodologia

### 4.1. Tipo de Projeto

[Classificar o projeto: aplicado, desenvolvimento experimental, estudo de caso, etc.]

### 4.2. Processo de Desenvolvimento

[Descrever as etapas do desenvolvimento:]

1. **Levantamento de requisitos** — [Como os requisitos foram levantados: visitas a doceria, entrevistas com o proprietario, observacao do processo operacional.]
2. **Modelagem de dados** — [Como o modelo de dados foi definido: star schema, tabelas de dimensao e fato.]
3. **Desenvolvimento do backend** — [Tecnologias, arquitetura em camadas, endpoints.]
4. **Desenvolvimento do frontend** — [Streamlit, paginas, visualizacoes.]
5. **Testes e validacao** — [Estrategia de testes, cobertura, validacao com o usuario.]
6. **Implantacao e treinamento** — [Como o sistema foi entregue e o proprietario capacitado.]

### 4.3. Tecnologias Utilizadas

[Listar e justificar as tecnologias escolhidas:]

| Tecnologia | Versao | Justificativa |
|-----------|--------|---------------|
| Python | 3.11+ | [Justificativa] |
| FastAPI | >=0.115 | [Justificativa] |
| Streamlit | >=1.38 | [Justificativa] |
| SQLAlchemy | >=2.0 | [Justificativa] |
| SQLite | — | [Justificativa] |
| Docker | — | [Justificativa] |
| [Outras] | — | [Justificativa] |

### 4.4. Cronograma

[Preencher o cronograma real de desenvolvimento:]

| Etapa | Inicio | Fim | Responsavel | Status |
|-------|--------|-----|-------------|--------|
| Levantamento de requisitos | [data] | [data] | [nome] | [concluido/em andamento] |
| Modelagem de dados | [data] | [data] | [nome] | [concluido/em andamento] |
| Desenvolvimento backend | [data] | [data] | [nome] | [concluido/em andamento] |
| Desenvolvimento frontend | [data] | [data] | [nome] | [concluido/em andamento] |
| Testes | [data] | [data] | [nome] | [concluido/em andamento] |
| Documentacao | [data] | [data] | [nome] | [concluido/em andamento] |
| Implantacao | [data] | [data] | [nome] | [concluido/em andamento] |

---

## 5. Resultados e Discussao

### 5.1. Produto Desenvolvido

[Descrever o sistema entregue: funcionalidades implementadas, telas principais, fluxos de uso. Incluir capturas de tela do dashboard.]

**Figura 1:** [Legenda — Tela principal do dashboard DoceVisao]
![Screenshot](caminho/para/imagem.png)

### 5.2. Indicadores Implementados

[Listar os KPIs implementados e sua relevancia para o negocio:]

| KPI | Formula | Relevancia para a Doceria |
|-----|---------|--------------------------|
| Faturamento | SUM(total) | [Descrever] |
| Ticket Medio | Faturamento / Pedidos | [Descrever] |
| Desperdicio | Descartado / Produzido | [Descrever] |
| [Outros] | [Formula] | [Descrever] |

### 5.3. Impacto para a Comunidade

[Descrever o impacto real ou esperado para a doceria parceira: melhoria na tomada de decisao, reducao de desperdicio, identificacao de produtos mais rentaveis, etc. Se houver dados reais de uso, incluir.]

### 5.4. Resultados Tecnicos

[Apresentar metricas tecnicas do projeto:]

| Metrica | Valor |
|---------|-------|
| Linhas de codigo (backend) | [valor] |
| Linhas de codigo (frontend) | [valor] |
| Cobertura de testes | [valor]% |
| Endpoints implementados | [valor] |
| Paginas do dashboard | [valor] |
| KPIs calculados | [valor] |

### 5.5. Dificuldades Encontradas

[Descrever as principais dificuldades tecnicas e de gestao encontradas durante o projeto e como foram superadas.]

---

## 6. Conclusoes

### 6.1. Objetivos Alcancados

[Avaliar cada objetivo especifico definido na secao 2.3 e indicar se foi alcancado, parcialmente alcancado ou nao alcancado.]

| Objetivo | Status | Observacoes |
|----------|--------|-------------|
| [Objetivo 1] | [Alcancado/Parcial/Nao] | [Observacao] |
| [Objetivo 2] | [Alcancado/Parcial/Nao] | [Observacao] |
| [Objetivo 3] | [Alcancado/Parcial/Nao] | [Observacao] |

### 6.2. Aprendizados

[Descrever os principais aprendizados da equipe: tecnicos, de gestao de projeto, de relacao com a comunidade.]

### 6.3. Trabalhos Futuros

[Listar possibilidades de evolucao do projeto:]
- [Trabalho futuro 1]
- [Trabalho futuro 2]
- [Trabalho futuro 3]

---

## 7. Referencias Bibliograficas

[Listar todas as referencias citadas no relatorio, formatadas conforme ABNT:]

- [SOBRENOME, Nome. Titulo. Editora, Ano.]
- [SOBRENOME, Nome. Titulo. Editora, Ano.]
- [SOBRENOME, Nome. Titulo. Editora, Ano.]

---

## Apendices

### Apendice A — Codigo-Fonte

O codigo-fonte completo do projeto esta disponivel no repositorio:
[URL do repositorio]

### Apendice B — Manual do Usuario

[Incluir ou referenciar o manual de uso do sistema para o proprietario da doceria.]

### Apendice C — Termos de Consentimento

[Incluir termos de consentimento da empresa parceira para uso da imagem e dos dados no projeto academico.]

---

## Checklist de Preenchimento

Antes de submeter o relatorio, verifique:

- [ ] Todos os campos entre colchetes foram preenchidos
- [ ] Nao ha dados ficticios — apenas informacoes reais do projeto
- [ ] As capturas de tela foram incluidas e legendadas
- [ ] As referencias bibliograficas estao formatadas conforme ABNT
- [ ] O cronograma reflete as datas reais de desenvolvimento
- [ ] Os objetivos foram avaliados individualmente
- [ ] O resumo esta entre 150-250 palavras
- [ ] O relatorio foi revisado pelo orientador
