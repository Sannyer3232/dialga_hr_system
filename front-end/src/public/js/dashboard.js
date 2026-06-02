async function carregarDashboard() {
    const token = localStorage.getItem('dialga_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    try {
        const response = await fetch('http://localhost:8000/absenteeism/dashboard/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) window.location.href = '/login';
            throw new Error('Erro ao carregar dados');
        }

        const data = await response.json();

        // Atualizar Cards
        document.getElementById('actualTotal').innerText = `${data.history.actual_total} hrs`;
        document.getElementById('predictedNext').innerText = `${data.next_month_projection.total_estimated_hour} hrs`;
        document.getElementById('gapVal').innerText = `${data.history.gap} hrs`;

        // Atualizar Gráfico
        renderChart(data.history.details);

        // Atualizar Lista da Equipe
        renderTeamList(data.next_month_projection.details);

    } catch (error) {
        console.error('Erro:', error);
        document.getElementById('teamList').innerHTML = '<li class="list-group-item bg-transparent text-danger">Falha ao carregar dados.</li>';
    }
}

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

function renderTeamList(details) {
    const list = document.getElementById('teamList');
    list.innerHTML = details.map(colab => `
        <li class="list-group-item bg-transparent d-flex justify-content-between align-items-center">
            ${colab.collaborator}
            <span class="badge bg-info rounded-pill">${colab.estimated_absence_hours}h</span>
        </li>
    `).join('');
}

document.addEventListener('DOMContentLoaded', carregarDashboard);