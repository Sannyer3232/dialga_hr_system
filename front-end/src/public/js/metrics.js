document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('scatterChart').getContext('2d');
    
    // Simulação de dados para o gráfico de dispersão (Real vs Predito)
    const data = Array.from({ length: 50 }, () => ({
        x: Math.random() * 20, // Real
        y: 0
    })).map(p => ({
        x: p.x,
        y: p.x + (Math.random() - 0.5) * 2 // Predito com ruído
    }));

    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Distribuição de Predição',
                data: data,
                backgroundColor: '#00D4FF'
            }, {
                label: 'Ideal (x=y)',
                data: [{x: 0, y: 0}, {x: 20, y: 20}],
                type: 'line',
                borderColor: '#1B3A57',
                borderDash: [5, 5],
                fill: false
            }]
        },
        options: {
            scales: {
                x: { title: { display: true, text: 'Horas Reais' } },
                y: { title: { display: true, text: 'Horas Preditas' } }
            },
            plugins: {
                legend: { labels: { color: '#1B3A57' } }
            }
        }
    });
});
