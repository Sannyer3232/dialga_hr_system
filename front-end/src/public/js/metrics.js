let scatterChart;

async function atualizarMetricas() {
    const percentage = document.getElementById('percentageInput').value;
    const token = localStorage.getItem('dialga_token');

    try {
        const response = await fetch('http://localhost:8000/absenteeism/model-metrics/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ percentage: parseFloat(percentage) })
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('maeVal').innerText = `${data.metrics.mae.toFixed(2)} hrs`;
            document.getElementById('rmseVal').innerText = `${data.metrics.rmse.toFixed(2)} hrs`;
            document.getElementById('r2Val').innerText = data.metrics.r2_score.toFixed(4);

            renderScatterChart(data.scatter_plot_data);
        } else {
            alert('Erro ao buscar métricas: ' + (data.error || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro de conexão com a API.');
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
    atualizarMetricas();
});
