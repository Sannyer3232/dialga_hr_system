import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

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
        const response = await this.apiClient.get('/absenteeism/dashboard/');
        return response.data;
    }

    async postManagerDashboard(payload: any) {
        const response = await this.apiClient.post('/absenteeism/dashboard/', payload);
        return response.data;
    }

    async postCollaboratorSimulation(payload: any) {
        const response = await this.apiClient.post('/absenteeism/simulate/', payload);
        return response.data;
    }

    async postModelMetrics(percentage: number) {
        const response = await this.apiClient.post('/absenteeism/model-metrics/', { percentage });
        return response.data;
    }

    async getEmployees() {
        const response = await this.apiClient.get('/absenteeism/collaborators/');
        return response.data;
    }

    async getAbsenteeismReasons() {
        const response = await this.apiClient.get('/absenteeism/reasons/');
        return response.data;
    }

    async getUserInfo() {
        const response = await this.apiClient.get('/me/');
        return response.data;
    }

    async postBulkPrediction(formData: FormData) {
        const response = await this.apiClient.post('/absenteeism/bulk-prediction/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    }
    }