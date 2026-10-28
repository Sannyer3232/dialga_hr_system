async function processarArquivo() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        alert('Por favor, selecione um arquivo.');
        return;
    }

    showLoader();

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/bulk', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            exibirResultados(data);
        } else {
            alert('Erro ao processar arquivo: ' + (data.error || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro de conexão com o servidor.');
    } finally {
        hideLoader();
    }
}

function exibirResultados(data) {
    // Mostrar container
    document.getElementById('resultsContainer').style.display = 'block';

    // Preencher Summary
    document.getElementById('resTotalRows').innerText = data.summary.total_rows;
    document.getElementById('resAvgHours').innerText = `${data.summary.average_predicted_hours} hrs`;
    document.getElementById('resProcTime').innerText = `${data.summary.processing_time_seconds}s`;

    // Preencher Ranking
    const tbody = document.getElementById('rankingBody');
    tbody.innerHTML = '';

    data.ranking.forEach((item, index) => {
        const tr = document.createElement('tr');
        
        let badgeClass = 'bg-success';
        let statusText = 'Excelente';
        
        if (item.predicted_hours > 4) {
            badgeClass = 'bg-warning';
            statusText = 'Atenção';
        }

        tr.innerHTML = `
            <td><span class="fw-bold text-info">#${index + 1}</span></td>
            <td>${item.collaborator}</td>
            <td>${item.predicted_hours} hrs</td>
            <td><span class="badge ${badgeClass}">${statusText}</span></td>
        `;
        tbody.appendChild(tr);
    });

    // Scroll suave para os resultados
    document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth' });
}
