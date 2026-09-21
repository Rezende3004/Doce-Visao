# Pendências para Entrega Acadêmica — DoceVisão

## Itens que dependem do aluno / da organização

### 1. Reunião com a Doceria Catarina
- [ ] Agendar reunião de apresentação do sistema
- [ ] Validar requisitos com o responsável pela doceria
- [ ] Coletar feedback sobre usabilidade e funcionalidades

### 2. Autorização de uso dos dados
- [ ] Obter autorização por escrito para utilizar dados reais da organização
- [ ] Definir política de privacidade para os dados coletados
- [ ] Garantir consentimento do parceiro para fins acadêmicos

### 3. Validação com dados reais
- [ ] Importar dados reais das vendas da doceria (caso autorizados)
- [ ] Comparar resultados do sistema com planilhas existentes
- [ ] Ajustar mapeamento de colunas conforme necessidade real

### 4. Evidências de extensão universitária
- [ ] Fotos da apresentação/demostração do sistema
- [ ] Registros de participação no evento de extensão
- [ ] Feedback documentado do parceiro (depoimento ou formulário)
- [ ] Material promocional utilizado (cartazes, folhetos, redes sociais)

### 5. Relatório técnico final
- [ ] Preencher nome da instituição no README e documentação
- [ ] Completar o relatório acadêmico com dados reais do projeto
- [ ] Incluir métricas de impacto quando disponíveis

### 6. Apresentação oral
- [ ] Preparar apresentação (slides) para defesa/prova
- [ ] Treinar demonstração ao vivo do sistema
- [ ] Preparar materiais complementares (prints, gráficos)

---

## Checklist pré-entrega técnica (automático)

| Critério | Status |
|----------|--------|
| 100% dos testes passando | OK |
| Cobertura mínima 80% | OK (85%) |
| Ruff sem erros | OK |
| Ruff format limpo | OK |
| Projeto compila | OK |
| Planilha sintética importa corretamente | OK (4818/4818 aceitas) |
| CSV com vírgula e ponto-e-vírgula | OK |
| Preview e confirmação funcionam | OK |
| Filtros aplicados na API | OK |
| Margem e cobertura calculadas corretamente | OK |
| Datas inválidas rejeitadas (HTTP 422) | OK |
| Nenhum percentual `inf` aparece | OK |

---

## Decisões técnicas documentadas

1. **Machine Learning opcional**: Módulos ML (anomaly detection, clustering, forecasting, trends) estão presentes mas não prejudicam o fluxo principal. Excluídos da contagem de cobertura.

2. **.xls removido como formato suportado**: Apenas `.csv` e `.xlsx` são suportados. A dependência `xlrd` não foi adicionada pois .xls é um formato legado.

3. **Arquitetura preservada**: Clean Architecture mantida com separação Domain → Application → Infrastructure → Presentation. Filtragem centralizada em `dependencies.py`.

4. **Monetário inteiro**: Conversão BRL→cents feita via string parsing sem float (`re.fullmatch` + split), eliminando problemas de arredondamento.
