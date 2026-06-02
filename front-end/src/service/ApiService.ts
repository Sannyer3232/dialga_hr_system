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
        // GET /absenteeism/dashboard/
        const response = await apiClient.get('/dashboard/');
        return response.data;
    },

    
    postCollaboratorSimulation: async (payload: any) => {
        // POST /absenteeism/simulate/
        const response = await apiClient.post('/simulate/', payload);
        return response.data;
    },

    postModelMetrics: async (percentage: number) => {
        // POST /absenteeism/model-metrics/
        const response = await apiClient.post('/model-metrics/', { percentage });
        return response.data;
    },

    getEmployees: async () => {
        // GET /absenteeism/collaborators/
        const response = await apiClient.get('/collaborators/');
        return response.data;
    },
    getAbsenteeismReasons: async () => {
        // GET /absenteeism/reasons/
        const response = await apiClient.get('/reasons/');
        return response.data;
    },
};