import axios from 'axios';

const API_BASE = 'http://localhost:8000/absenteeism';

const apiClient = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Interceptor para injetar o JWT token do Dialga HR System
apiClient.interceptors.request.use(config => {
    const token = localStorage.getItem('dialga_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const RelatoriosAPI = {
    getManagerDashboard: async () => {
        // GET /absenteeism/manager-dashboard/
        const response = await apiClient.get('/manager-dashboard/');
        return response.data;
    },
    
    postCollaboratorSimulation: async (payload: any) => {
        // POST /absenteeism/collaborator-simulation/
        const response = await apiClient.post('/collaborator-simulation/', payload);
        return response.data;
    },

    getModelMetrics: async () => {
        // GET /absenteeism/model-metrics/
        const response = await apiClient.get('/model-metrics/');
        return response.data; // Retorna { MAE: X, RMSE: Y, R2: Z, scatter_data: [] }
    }
};