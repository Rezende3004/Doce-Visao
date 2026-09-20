"""Deterministic insight generation based on rules, not LLM."""
from __future__ import annotations

from app.application.dto.analytics import SalesFilters
from app.application.dto.insights import Insight, InsightLevel
from app.infrastructure.repositories.implementations import (
    ProductionRepository,
    ProductRepository,
    SalesRepository,
)


def generate_insights(
    sales_repo: SalesRepository,
    product_repo: ProductRepository,
    production_repo: ProductionRepository,
    filters: SalesFilters | None = None,
) -> list[Insight]:
    insights: list[Insight] = []

    summary = sales_repo.get_summary(filters)
    if summary.num_pedidos == 0:
        insights.append(Insight(
            title="Sem dados de vendas",
            description="Não foram encontradas vendas concluídas no período selecionado.",
            evidence="0 pedidos no período.",
            recommendation="Verifique se os dados foram importados corretamente ou ajuste o filtro de período.",
            level=InsightLevel.ATENCAO,
        ))
        return insights

    weekdays = sales_repo.get_by_weekday(filters)
    if weekdays:
        best_day = max(weekdays, key=lambda w: w.faturamento_cents)
        insights.append(Insight(
            title=f"Dia de maior faturamento: {best_day.weekday}",
            description=f"As dados indicam que {best_day.weekday} concentra o maior faturamento.",
            evidence=f"Faturamento de R$ {best_day.faturamento_cents / 100:.2f}".replace(".", ",") + f" em {best_day.num_pedidos} pedidos.",
            recommendation="Vale investigar se há sazonalidade e planejar produção e equipe para este dia.",
            level=InsightLevel.INFORMATIVO,
            metric_value=best_day.faturamento_cents / 100,
        ))

    ranking_qty = product_repo.get_ranking_by_quantity(filters, limit=5)
    if ranking_qty:
        top = ranking_qty[0]
        insights.append(Insight(
            title=f"Produto mais vendido: {top.product_name}",
            description=f"Os dados indicam que '{top.product_name}' lidera em volume de vendas.",
            evidence=f"{top.quantity} unidades vendidas.",
            recommendation="Considere garantir estoque adequado e avaliar oportunidades de cross-sell.",
            level=InsightLevel.INFORMATIVO,
            metric_value=top.quantity,
        ))

    ranking_rev = product_repo.get_ranking_by_revenue(filters, limit=5)
    if ranking_rev:
        top = ranking_rev[0]
        insights.append(Insight(
            title=f"Maior faturamento: {top.product_name}",
            description=f"'{top.product_name}' gera o maior faturamento.",
            evidence=f"R$ {top.faturamento_cents / 100:.2f}".replace(".", ",") + " em vendas.",
            recommendation="Produto-chave para a doceria. Acompanhe margem e disponibilidade.",
            level=InsightLevel.INFORMATIVO,
            metric_value=top.faturamento_cents / 100,
        ))

    categories = product_repo.get_category_performance(filters)
    if categories:
        top_cat = categories[0]
        if top_cat.share_percentual > 50:
            insights.append(Insight(
                title=f"Concentração na categoria '{top_cat.category}'",
                description=f"A categoria '{top_cat.category}' representa {top_cat.share_percentual:.1f}% do faturamento.",
                evidence=f"R$ {top_cat.faturamento_cents / 100:.2f}".replace(".", ",") + f" de {top_cat.share_percentual:.1f}% do total.",
                recommendation="Alta concentração pode indicar risco. Vale diversificar o mix de produtos.",
                level=InsightLevel.ATENCAO,
                metric_value=top_cat.share_percentual,
            ))

    channels = sales_repo.get_by_channel(filters)
    if channels:
        top_ch = channels[0]
        insights.append(Insight(
            title=f"Canal principal: {top_ch.channel_name}",
            description=f"O canal '{top_ch.channel_name}' concentra o maior número de pedidos.",
            evidence=f"{top_ch.num_pedidos} pedidos, R$ {top_ch.faturamento_cents / 100:.2f}".replace(".", ",") + " em faturamento.",
            recommendation="Avalie se há oportunidades de crescimento em outros canais.",
            level=InsightLevel.INFORMATIVO,
        ))

    if summary.crescimento_percentual is not None:
        if summary.crescimento_percentual > 10:
            insights.append(Insight(
                title="Crescimento em relação ao período anterior",
                description=f"O faturamento cresceu {summary.crescimento_percentual:.1f}% em relação ao período anterior de mesma duração.",
                evidence=(
                    f"Período atual: R$ {summary.faturamento_cents / 100:.2f}".replace(".", ",")
                    + f" | Anterior: R$ {(summary.faturamento_anterior_cents or 0) / 100:.2f}".replace(".", ",")
                ),
                recommendation="Bom sinal. Investigue quais produtos/canais impulsionaram o crescimento.",
                level=InsightLevel.OPORTUNIDADE,
                metric_value=summary.crescimento_percentual,
            ))
        elif summary.crescimento_percentual < -10:
            insights.append(Insight(
                title="Queda em relação ao período anterior",
                description=f"O faturamento caiu {abs(summary.crescimento_percentual):.1f}% em relação ao período anterior.",
                evidence=(
                    f"Período atual: R$ {summary.faturamento_cents / 100:.2f}".replace(".", ",")
                    + f" | Anterior: R$ {(summary.faturamento_anterior_cents or 0) / 100:.2f}".replace(".", ",")
                ),
                recommendation="Vale investigar causas: sazonalidade, perda de clientes ou problemas operacionais.",
                level=InsightLevel.ATENCAO,
                metric_value=summary.crescimento_percentual,
            ))

    margin = product_repo.get_margin_info(filters)
    if margin.coverage_percentual < 50:
        insights.append(Insight(
            title="Cobertura de custos insuficiente",
            description=f"Apenas {margin.coverage_percentual:.0f}% das vendas possuem dados de custo.",
            evidence=f"Cobertura de {margin.coverage_percentual:.0f}% — margem calculada pode não ser representativa.",
            recommendation="Para análises de margem confiáveis, inclua o custo unitário nas importações.",
            level=InsightLevel.ATENCAO,
            metric_value=margin.coverage_percentual,
        ))

    waste = production_repo.get_waste_by_product(filters)
    if waste:
        total_discarded = sum(w.discarded for w in waste)
        total_produced = sum(w.produced for w in waste)
        if total_produced > 0:
            rate = total_discarded / total_produced * 100
            if rate > 10:
                insights.append(Insight(
                    title="Taxa de desperdício elevada",
                    description=f"A taxa de desperdício geral é de {rate:.1f}%.",
                    evidence=f"{total_discarded} unidades descartadas de {total_produced} produzidas.",
                    recommendation="Revise o planejamento de produção e as causas do desperdício.",
                    level=InsightLevel.ATENCAO,
                    metric_value=rate,
                ))
        worst = max(waste, key=lambda w: w.discarded)
        if worst.discarded > 0:
            insights.append(Insight(
                title=f"Maior desperdício: {worst.product_name}",
                description=f"'{worst.product_name}' apresenta o maior volume de desperdício.",
                evidence=f"{worst.discarded} unidades descartadas ({worst.waste_rate:.1f}% do produzido).",
                recommendation="Investigue causas e ajuste a produção deste produto.",
                level=InsightLevel.OPORTUNIDADE,
                metric_value=worst.waste_rate,
            ))
    else:
        insights.append(Insight(
            title="Sem dados de produção",
            description="Não há dados de produção importados. Análises de desperdício não estão disponíveis.",
            evidence="Nenhum registro de produção encontrado.",
            recommendation="Importe dados de produção para habilitar análises de desperdício e planejamento.",
            level=InsightLevel.INFORMATIVO,
        ))

    return insights
