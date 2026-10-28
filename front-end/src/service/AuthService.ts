import axios from 'axios';
import getEnv from '../utils/getEnv.js';

const API_BASE = getEnv().API_BASE_URL;

export class AuthService {
  static async login(username: string, password: string) {
    try {
      const response = await axios.post(`${API_BASE}/token/`, {
        username,
        password,
      });
      return response.data.access;
    } catch (error) {
      console.error('Falha na autenticação', error);
      throw error;
    }
  }
}
