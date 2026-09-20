function createLineChart(elementId, dates, values, title = '') {
    const data = [{
        x: dates,
        y: values,
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy',
        line: { color: '#D4577B' },
    }];
    const layout = {
        title: title,
        xaxis: { title: 'Data' },
        yaxis: { title: 'Faturamento (R$)' },
        height: 350,
        margin: { t: 40, b: 40, l: 60, r: 20 },
    };
    Plotly.newPlot(elementId, data, layout, { responsive: true });
}

function createBarChart(elementId, labels, values, title = '', color = '#D4577B') {
    const data = [{
        x: labels,
        y: values,
        type: 'bar',
        marker: { color: color },
    }];
    const layout = {
        title: title,
        xaxis: { tickangle: -45 },
        yaxis: { title: 'Faturamento (R$)' },
        height: 350,
        margin: { t: 40, b: 80, l: 60, r: 20 },
    };
    Plotly.newPlot(elementId, data, layout, { responsive: true });
}

function createGroupedBarChart(elementId, labels, values1, values2, name1, name2) {
    const data = [
        {
            x: labels,
            y: values1,
            type: 'bar',
            name: name1,
            marker: { color: '#22C55E' },
        },
        {
            x: labels,
            y: values2,
            type: 'bar',
            name: name2,
            marker: { color: '#EF4444' },
        },
    ];
    const layout = {
        barmode: 'group',
        xaxis: { tickangle: -45 },
        yaxis: { title: 'Quantidade' },
        height: 400,
        margin: { t: 40, b: 80, l: 60, r: 20 },
    };
    Plotly.newPlot(elementId, data, layout, { responsive: true });
}

function createDualAxisChart(elementId, dates, values1, values2, name1, name2) {
    const data = [
        {
            x: dates,
            y: values1,
            type: 'scatter',
            mode: 'lines',
            name: name1,
            line: { color: '#D4577B' },
        },
        {
            x: dates,
            y: values2,
            type: 'scatter',
            mode: 'lines',
            name: name2,
            yaxis: 'y2',
            line: { color: '#F59E0B' },
        },
    ];
    const layout = {
        xaxis: { title: 'Data' },
        yaxis: { title: 'Faturamento (R$)', side: 'left' },
        yaxis2: { title: 'Pedidos', side: 'right', overlaying: 'y' },
        height: 400,
        margin: { t: 40, b: 40, l: 60, r: 60 },
    };
    Plotly.newPlot(elementId, data, layout, { responsive: true });
}
