document.addEventListener('DOMContentLoaded', function () {
    // Inicialização do Chart.js
    const ctx = document.getElementById('gapChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            datasets: [
                {
                    label: 'Faltas Reais',
                    data: [120, 150, 110, 90, 130, 124],
                    borderColor: '#1B3A57',
                    tension: 0.4
                },
                {
                    label: 'Previsão (IA)',
                    data: [125, 145, 115, 95, 125, 130],
                    borderColor: '#00D4FF',
                    borderDash: [5, 5],
                    tension: 0.4
                }
            ]
        }
    });
});