let scatterChart;

function syncInputs(source) {
    const slider = document.getElementById('percentageSlider');
    const input = document.getElementById('percentageInput');

    if (source === 'slider') {
        input.value = slider.value;
    } else {
        slider.value = input.value;
    }
}

async function atualizarMetricas() {
    const percentage = document.getElementById('percentageInput').value;
    showLoader();

    try {
        const response = await fetch('/api/metrics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ percentage: parseFloat(percentage) })
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('maeVal').innerText = `${data.metrics.mae.toFixed(2)} hrs`;
            document.getElementById('rmseVal').innerText = `${data.metrics.rmse.toFixed(2)} hrs`;
            
            // Sincronizado com o roundPercentageHelper (digits: 2)
            const r2Percent = (Number(data.metrics.r2_score.toFixed(2)) * 100);
            document.getElementById('r2Val').innerText = `${r2Percent}%`;

            document.getElementById('totalRecords').innerText = data.scatter_plot_data.length;

            renderScatterChart(data.scatter_plot_data);
        } else {
            alert('Erro ao buscar métricas: ' + (data.error || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro de conexão com o servidor.');
    } finally {
        hideLoader();
    }
}

function renderScatterChart(scatterData) {
    const ctx = document.getElementById('scatterChart').getContext('2d');
    
    const formattedData = scatterData.map(p => ({
        x: p.actual,
        y: p.predicted
    }));

    if (scatterChart) {
        scatterChart.destroy();
    }

    scatterChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Distribuição de Predição',
                data: formattedData,
                backgroundColor: 'rgba(0, 212, 255, 0.6)'
            }, {
                label: 'Ideal (x=y)',
                data: [{x: 0, y: 0}, {x: Math.max(...formattedData.map(d => d.x)), y: Math.max(...formattedData.map(d => d.x))}],
                type: 'line',
                borderColor: '#1B3A57',
                borderDash: [5, 5],
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: 'Horas Reais' } },
                y: { title: { display: true, text: 'Horas Preditas' } }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    if (window.SCATTER_DATA) {
        renderScatterChart(window.SCATTER_DATA);
    }
});

