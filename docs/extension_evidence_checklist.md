# Checklist de Evidencias — Projeto de Extensao DoceVisao

Este checklist organiza as evidencias necessárias para atender aos requisitos de avaliacao de projetos de extensao universitaria. Cada item deve ser comprovado com documento, captura de tela ou registro apropriado.

---

## 1. Identificacao e Enquadramento

- [ ] **1.1.** Titulo do projeto definido e descritivo
- [ ] **1.2.** Area tematica de extensao identificada (ex: Tecnologia e Producao, Comunicacao, etc.)
- [ ] **1.3.** Linha de extensao da instituicao mapeada
- [ ] **1.4.** Objetivos de Desenvolvimento Sustentavel (ODS) relacionados identificados (ex: ODS 8 — Trabalho Decente e Crescimento Economico, ODS 9 — Industria, Inovacao e Infraestrutura)
- [ ] **1.5.** Publico-alvo definido (Doceria Catarina — pequeno negocio do segmento de confeitaria)
- [ ] **1.6.** Parceiro comunitario identificado e formalizado (nome, CNPJ se aplicavel, contato)

---

## 2. Diagnostico da Realidade

- [ ] **2.1.** Visita inicial a doceria registrada (data, participantes, fotos se autorizado)
- [ ] **2.2.** Diagnostico da situacao atual documentado (como a doceria controla vendas, producao, desperdicio)
- [ ] **2.3.** Problemas identificados junto ao proprietario listados e priorizados
- [ ] **2.4.** Necessidades reais do parceiro mapeadas (nao apenas o que a equipe imagina que ele precisa)
- [ ] **2.5.** Registro do diagnostico em formato escrito (ata de reuniao, relatorio de visita)

---

## 3. Planejamento

- [ ] **3.1.** Cronograma de atividades com datas de inicio e fim
- [ ] **3.2.** Divisao de tarefas entre os membros da equipe documentada
- [ ] **3.3.** Requisitos funcionais levantados e validados com o parceiro
- [ ] **3.4.** Requisitos nao funcionais definidos (performance, usabilidade, etc.)
- [ ] **3.5.** Termo de consentimento do parceiro para participacao no projeto
- [ ] **3.6.** Aprovacao do orientador para o plano de trabalho

---

## 4. Desenvolvimento Tecnico

### 4.1. Codigo-Fonte
- [ ] **4.1.1.** Repositorio de codigo criado e versionado (Git)
- [ ] **4.1.2.** Commits com mensagens descritivas e regulares
- [ ] **4.1.3.** Estrutura de diretorios documentada
- [ ] **4.1.4.** README do repositorio completo
- [ ] **4.1.5.** Codigo revisado pela equipe (code reviews se aplicavel)

### 4.2. Documentacao Tecnica
- [ ] **4.2.1.** Documento de arquitetura do sistema (`docs/architecture.md`)
- [ ] **4.2.2.** Dicionario de dados (`docs/data_dictionary.md`)
- [ ] **4.2.3.** Especificacao de requisitos (`docs/requirements.md`)
- [ ] **4.2.4.** Documentacao da API (`docs/api.md`)
- [ ] **4.2.5.** Documentacao dos KPIs (`docs/kpis.md`)

### 4.3. Testes e Qualidade
- [ ] **4.3.1.** Testes unitarios implementados
- [ ] **4.3.2.** Testes de integracao implementados
- [ ] **4.3.3.** Testes de API implementados
- [ ] **4.3.4.** Cobertura de testes mensurada (meta: >= 80%)
- [ ] **4.3.5.** Lint e formatacao de codigo automatizados (ruff)
- [ ] **4.3.6.** Relatorio de cobertura gerado e salvo

### 4.4. Infraestrutura
- [ ] **4.4.1.** Dockerfile do backend criado
- [ ] **4.4.2.** Dockerfile do frontend criado
- [ ] **4.4.3.** docker-compose.yml funcional
- [ ] **4.4.4.** Instrucoes de instalacao e execucao documentadas
- [ ] **4.4.5.** Variaveis de ambiente documentadas (.env.example)

---

## 5. Intercacao com a Comunidade

- [ ] **5.1.** Registro de reunioes com o parceiro (atas com data, participantes, pautas e decisoes)
- [ ] **5.2.** Apresentacoes intermediarias para o parceiro registradas (fotos, slides)
- [ ] **5.3.** Feedback do parceiro coletado e documentado em cada etapa
- [ ] **5.4.** Ajustes solicitados pelo parceiro realizados e registrados
- [ ] **5.5.** Evidencia de que o parceiro participou ativamente (nao apenas como observador)

---

## 6. Resultados e Entrega

### 6.1. Produto Funcional
- [ ] **6.1.1.** Sistema executando corretamente via Docker
- [ ] **6.1.2.** Sistema executando corretamente em instalacao local
- [ ] **6.1.3.** Importacao de dados de vendas funcionando
- [ ] **6.1.4.** Importacao de dados de producao funcionando
- [ ] **6.1.5.** Dashboard com todos os KPIs funcionando
- [ ] **6.1.6.** Insights automaticos gerando recomendacoes
- [ ] **6.1.7.** Exportacao de dados funcionando
- [ ] **6.1.8.** Dados sinteticos de demonstracao disponiveis

### 6.2. Capturas de Tela
- [ ] **6.2.1.** Tela inicial do dashboard
- [ ] **6.2.2.** KPIs principais (faturamento, pedidos, ticket medio, itens)
- [ ] **6.2.3.** Grafico de evolucao temporal
- [ ] **6.2.4.** Ranking de produtos
- [ ] **6.2.5.** Desempenho por categoria
- [ ] **6.2.6.** Analise de desperdicio
- [ ] **6.2.7.** Pagina de insights
- [ ] **6.2.8.** Tela de importacao (preview e confirmacao)
- [ ] **6.2.9.** Tratamento de erros na importacao

### 6.3. Entrega ao Parceiro
- [ ] **6.3.1.** Sistema entregue e funcionando no ambiente do parceiro (ou acessivel)
- [ ] **6.3.2.** Treinamento do proprietario realizado (registrar data, duracao, conteudo)
- [ ] **6.3.3.** Manual do usuario entregue (pode ser este README ou documento separado)
- [ ] **6.3.4.** Termo de entrega/aceite assinado pelo parceiro
- [ ] **6.3.5.** Canal de suporte pos-entrega definido (ex: e-mail, WhatsApp)

---

## 7. Avaliacao de Impacto

- [ ] **7.1.** Indicadores de impacto definidos antes da entrega
- [ ] **7.2.** Avaliacao do parceiro sobre a utilidade do sistema (depoimento escrito ou gravado)
- [ ] **7.3.** Mudancas observadas na gestao da doceria apos uso do sistema (se houver tempo de uso)
- [ ] **7.4.** Numero de importacoes realizadas pelo parceiro (metrica de uso)
- [ ] **7.5.** Decisoes de negocio tomadas com base nos dados do sistema (se houver registro)

---

## 8. Disseminacao e Sustentabilidade

- [ ] **8.1.** Repositorio publico no GitHub (ou equivalente) com licenca definida
- [ ] **8.2.** Documentacao completa permitindo que outra equipe de continuidade
- [ ] **8.3.** Plano de sustentabilidade definido (quem mantem o sistema apos o fim da disciplina)
- [ ] **8.4.** Possibilidade de reaplicacao em outras docerias ou pequenos negocios avaliada
- [ ] **8.5.** Artigo, poster ou apresentacao em evento academico produzido ou planejado

---

## 9. Aspectos Eticos e Legais

- [ ] **9.1.** Termo de consentimento do parceiro para uso da imagem (se houver fotos)
- [ ] **9.2.** Termo de consentimento para uso dos dados da doceria no projeto
- [ ] **9.3.** Declaracao de que os dados da doceria nao serao compartilhados com terceiros
- [ ] **9.4.** Confirmacao de que nenhum dado pessoal de clientes da doceria e armazenado
- [ ] **9.5.** Aprovacao do comite de etica da instituicao (se exigido)

---

## 10. Relatorio Final

- [ ] **10.1.** Relatorio de extensao escrito conforme modelo (`docs/academic_report_template.md`)
- [ ] **10.2.** Resumo entre 150-250 palavras
- [ ] **10.3.** Referencial teorico com citacoes e referencias ABNT
- [ ] **10.4.** Metodologia descrita com detalhes reprodutiveis
- [ ] **10.5.** Resultados apresentados com evidencias (telas, metricas, depoimentos)
- [ ] **10.6.** Conclusoes alinhadas aos objetivos iniciais
- [ ] **10.7.** Relatorio revisado pelo orientador antes da submissao

---

## Resumo de Evidencias por Categoria

| Categoria | Quantidade de Itens | Status |
|-----------|:-------------------:|--------|
| 1. Identificacao | 6 | [ ] |
| 2. Diagnostico | 5 | [ ] |
| 3. Planejamento | 6 | [ ] |
| 4. Desenvolvimento Tecnico | 17 | [ ] |
| 5. Interacao com a Comunidade | 5 | [ ] |
| 6. Resultados e Entrega | 18 | [ ] |
| 7. Avaliacao de Impacto | 5 | [ ] |
| 8. Disseminacao | 5 | [ ] |
| 9. Aspectos Eticos | 5 | [ ] |
| 10. Relatorio Final | 7 | [ ] |
| **Total** | **79** | [ ] |

---

## Observacoes

- Este checklist deve ser acompanhado ao longo de todo o semestre, nao apenas preenchido no final.
- Cada item marcado deve ter uma evidencia associada (documento, foto, captura de tela, ata).
- Itens nao aplicaveis devem ser justificados por escrito.
- O orientador deve validar periodicamente o progresso do checklist.
- Evidencias digitais devem ser organizadas em pasta especifica (ex: `evidencias/`) com nomenclatura clara.
