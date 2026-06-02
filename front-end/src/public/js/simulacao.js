async function carregarDadosIniciais() {
    const token = localStorage.getItem('dialga_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    try {
        // Carregar Colaboradores
        const resColabs = await fetch('http://localhost:8000/absenteeism/collaborators/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const colabs = await resColabs.json();
        const selectColab = document.getElementById('colabSelect');
        if (colabs.length > 0) {
            selectColab.innerHTML = colabs.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        } else {
            selectColab.innerHTML = '<option value="">Nenhum colaborador encontrado</option>';
        }

        // Carregar Motivos
        const resReasons = await fetch('http://localhost:8000/absenteeism/reasons/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const reasons = await resReasons.json();
        const selectReason = document.getElementById('reasonSelect');
        if (reasons.length > 0) {
            selectReason.innerHTML = reasons.map(r => `<option value="${r.code}">${r.description}</option>`).join('');
        } else {
            selectReason.innerHTML = '<option value="">Nenhum motivo encontrado</option>';
        }

    } catch (error) {
        console.error('Erro ao carregar dados iniciais:', error);
    }
}

async function executarPrevisao() {
    const colabId = document.getElementById('colabSelect').value;
    const workload = document.getElementById('workload').value;
    const hitTarget = document.getElementById('hitTarget').value;
    const month = document.getElementById('monthInput').value;
    const dayOfWeek = document.getElementById('dayOfWeekInput').value;
    const reasonCode = document.getElementById('reasonSelect').value;
    const token = localStorage.getItem('dialga_token');

    if (!colabId) {
        alert('Selecione um colaborador.');
        return;
    }

    const badge = document.getElementById('resultadoPrevisao');
    badge.innerHTML = '<span class="spinner-border text-info" role="status"></span>';

    try {
        const response = await fetch('http://localhost:8000/absenteeism/simulate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
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
        alert('Erro de conexão com a API.');
    }
}

document.addEventListener('DOMContentLoaded', carregarDadosIniciais);
