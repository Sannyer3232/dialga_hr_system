import axios from 'axios';

const API_BASE = 'http://localhost:8000/absenteeism';

export class RelatoriosAPI {
    private apiClient;

    constructor(token?: string) {
        this.apiClient = axios.create({
            baseURL: API_BASE,
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (token) {
            this.apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        }
    }

    async getManagerDashboard() {
        const response = await this.apiClient.get('/dashboard/');
        return response.data;
    }

    async postCollaboratorSimulation(payload: any) {
        const response = await this.apiClient.post('/simulate/', payload);
        return response.data;
    }

    async postModelMetrics(percentage: number) {
        const response = await this.apiClient.post('/model-metrics/', { percentage });
        return response.data;
    }

    async getEmployees() {
        const response = await this.apiClient.get('/collaborators/');
        return response.data;
    }

    async getAbsenteeismReasons() {
        const response = await this.apiClient.get('/reasons/');
        return response.data;
    }
}