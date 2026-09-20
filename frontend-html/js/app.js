async function loadDashboard() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const params = { start_date: startDate, end_date: endDate };

    try {
        const summary = await API.getSummary(params);
        document.getElementById('faturamento').textContent = summary.faturamento;
        document.getElementById('pedidos').textContent = summary.num_pedidos;
        document.getElementById('ticketMedio').textContent = summary.ticket_medio;
        document.getElementById('itensVendidos').textContent = summary.itens_vendidos;

        if (summary.crescimento_percentual !== null) {
            const delta = document.getElementById('faturamentoDelta');
            const value = summary.crescimento_percentual.toFixed(1);
            delta.textContent = `${value}% vs período anterior`;
            delta.className = summary.crescimento_percentual >= 0 ? 'delta' : 'delta negative';
        }

        const timeline = await API.getTimeline(params);
        if (timeline.length > 0) {
            createLineChart(
                'timelineChart',
                timeline.map(p => p.date),
                timeline.map(p => p.faturamento_cents / 100),
                ''
            );
        }

        const weekdays = await API.getByWeekday(params);
        if (weekdays.length > 0) {
            createBarChart(
                'weekdayChart',
                weekdays.map(w => w.weekday),
                weekdays.map(w => w.faturamento_cents / 100),
                ''
            );
        }

        const insights = await API.getInsights(params);
        const insightsList = document.getElementById('insightsList');
        insightsList.innerHTML = insights.slice(0, 5).map(ins => `
            <div class="insight-card ${ins.level}">
                <h4>${ins.title}</h4>
                <p>${ins.description}</p>
                <p><strong>Evidência:</strong> ${ins.evidence}</p>
                <div class="recommendation">💡 ${ins.recommendation}</div>
            </div>
        `).join('');

    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        document.querySelector('.content').innerHTML += `
            <div class="alert alert-danger">
                Erro ao carregar dados. Verifique se o backend está rodando.
            </div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('applyFilters')) {
        document.getElementById('applyFilters').addEventListener('click', loadDashboard);
        loadDashboard();
    }
});
