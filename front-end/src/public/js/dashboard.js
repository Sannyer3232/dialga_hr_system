function renderChart(details) {
    const labels = details.map(d => d.date);
    const actualData = details.map(d => d.actual);
    const predictedData = details.map(d => d.predicted);

    const ctx = document.getElementById('gapChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Faltas Reais',
                    data: actualData,
                    borderColor: '#1B3A57',
                    tension: 0.4
                },
                {
                    label: 'Previsão (IA)',
                    data: predictedData,
                    borderColor: '#00D4FF',
                    borderDash: [5, 5],
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    if (window.CHART_DATA) {
        renderChart(window.CHART_DATA);
    }
});