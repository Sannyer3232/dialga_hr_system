async function executarPrevisao() {
    const colabId = document.getElementById('colabSelect').value;
    const workload = document.getElementById('workload').value;
    const hitTarget = document.getElementById('hitTarget').value;
    const month = document.getElementById('monthInput').value;
    const dayOfWeek = document.getElementById('dayOfWeekInput').value;
    const reasonCode = document.getElementById('reasonSelect').value;

    if (!colabId) {
        alert('Selecione um colaborador.');
        return;
    }

    const badge = document.getElementById('resultadoPrevisao');
    badge.innerHTML = '<span class="spinner-border text-info" role="status"></span>';

    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                collaborator_id: parseInt(colabId),
                work_load: parseFloat(workload),
                hit_target: parseInt(hitTarget),
                month: parseInt(month),
                day_of_week: parseInt(dayOfWeek),
                reason_code: parseInt(reasonCode)
            })
        });

        const data = await response.json();

        if (response.ok) {
            badge.innerText = `${data.predicted_absence_hours.toFixed(2)} hrs`;
        } else {
            badge.innerText = '-- hrs';
            alert('Erro na simulação: ' + (data.error || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro:', error);
        badge.innerText = '-- hrs';
        alert('Erro de conexão com o servidor.');
    }
}

