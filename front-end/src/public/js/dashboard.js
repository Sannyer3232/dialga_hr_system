let dashboardChart;

function renderChart(details) {
    const labels = [...new Set(details.map(d => d.date))];

    // Agrupa dados por data para o gráfico (média se houver múltiplos registros no mesmo mês para colaboradores diferentes)
    const groupedData = labels.map(label => {
        const matches = details.filter(d => d.date === label);
        const actualSum = matches.reduce((sum, m) => sum + m.actual, 0);
        const predictedSum = matches.reduce((sum, m) => sum + m.predicted, 0);
        return { label, actual: actualSum, predicted: predictedSum };
    });

    const ctx = document.getElementById('gapChart').getContext('2d');

    if (dashboardChart) {
        dashboardChart.destroy();
    }

    dashboardChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: groupedData.map(d => d.label),
            datasets: [
                {
                    label: 'Faltas Reais',
                    data: groupedData.map(d => d.actual),
                    borderColor: '#1B3A57',
                    backgroundColor: 'rgba(27, 58, 87, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Previsão Dialga (IA)',
                    data: groupedData.map(d => d.predicted),
                    borderColor: '#00D4FF',
                    borderDash: [5, 5],
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Horas' }
                }
            }
        }
    });
}

async function atualizarDashboardCustom() {
    const workload = document.getElementById('workloadSlider').value;
    const target = document.getElementById('targetSlider').value;
    const reason = document.getElementById('reasonSelect').value;
    const day = document.getElementById('daySelect').value;

    showLoader();

    try {
        const response = await fetch('/api/dashboard', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                work_load: parseFloat(workload),
                hit_target: parseInt(target),
                reason_code: parseInt(reason),
                day_of_week: parseInt(day)
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Atualiza Cards
            document.getElementById('actualCurrent').innerText = `${data.current_month.actual_total} hrs`;
            document.getElementById('predictedCurrent').innerText = `${data.current_month.predicted_total} hrs`;

            const gapEl = document.getElementById('gapCurrent');
            gapEl.innerText = `${data.current_month.gap} hrs`;
            gapEl.className = `fw-bold ${data.current_month.gap > 0 ? 'text-danger' : 'text-success'}`;

            document.getElementById('predictedNext').innerText = `${data.next_month.total_estimated_hour} hrs`;

            // Atualiza Lista da Equipe
            const teamList = document.getElementById('teamList');
            teamList.innerHTML = '';
            data.next_month.details.forEach(colab => {
                const li = document.createElement('li');
                li.className = 'list-group-item bg-transparent d-flex justify-content-between align-items-center border-secondary-subtle';
                li.innerHTML = `
                    <span class="text-dark">${colab.collaborator}</span>
                    <span class="badge bg-info rounded-pill">${colab.estimated_absence_hours}h</span>
                `;
                teamList.appendChild(li);
            });

            // Atualiza Gráfico
            renderChart(data.history.details);

            // Fecha o sidebar (opcional)
            const sidebar = bootstrap.Offcanvas.getInstance(document.getElementById('simulationSidebar'));
            sidebar.hide();
        } else {
            alert('Erro ao atualizar dashboard: ' + (data.error || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro de conexão com o servidor.');
    } finally {
        hideLoader();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (window.CHART_DATA) {
        renderChart(window.CHART_DATA);
    }
});