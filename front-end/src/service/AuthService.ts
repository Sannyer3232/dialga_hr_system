import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export class AuthService {
  static async login(username: string, password: string) {
    try {
      const response = await axios.post(`${API_BASE}/token/`, { username, password });
      return response.data.access;
    } catch (error) {
      console.error('Falha na autenticação', error);
      return null;
    }
  }

  static setToken(token: string) {
    localStorage.setItem('dialga_token', token);
  }
}
