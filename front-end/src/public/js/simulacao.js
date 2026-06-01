 function executarPrevisao() {
        // Simulação visual da chamada Axios
        const badge = document.getElementById('resultadoPrevisao');
        badge.innerHTML = '<span class="spinner-border text-info" role="status"></span>';
        
        setTimeout(() => {
            badge.innerHTML = '32.5 hrs';
        }, 1500);
    }