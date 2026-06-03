import type { Request, Response } from 'express';
import { RelatoriosAPI } from '../service/ApiService.js';
import { AuthService } from '../service/AuthService.js';

const getToken = (req: Request) => {
  const cookies = req.headers.cookie;
  if (!cookies) return null;
  const tokenCookie = cookies.split(';').find(c => c.trim().startsWith('dialga_token='));
  return tokenCookie ? tokenCookie.split('=')[1] : null;
};

const login = (req: Request, res: Response) => {
  res.render('login', { layout: false });
};

const postLogin = async (req: Request, res: Response) => {
  const { username, password } = req.body;
  try {
    const token = await AuthService.login(username, password);
    res.setHeader('Set-Cookie', `dialga_token=${token}; Path=/; HttpOnly`);
    res.redirect('/dashboard');
  } catch (error) {
    res.render('login', { error: 'Usuário ou senha inválidos', layout: false });
  }
};

const dashboard = async (req: Request, res: Response) => {
  const token = getToken(req);
  if (!token) return res.redirect('/login');

  try {
    const api = new RelatoriosAPI(token);
    const data = await api.getManagerDashboard();
    res.render('dashboard', {
      activeDashboard: true,
      data: data,
      // Stringify for the client-side chart logic
      chartData: JSON.stringify(data.history.details),
      teamData: data.next_month_projection.details
    });
  } catch (error) {
    console.error('Erro ao carregar dashboard:', error);
    res.redirect('/login');
  }
};

const simulacao = async (req: Request, res: Response) => {
  const token = getToken(req);
  if (!token) return res.redirect('/login');

  try {
    const api = new RelatoriosAPI(token);
    const collaborators = await api.getEmployees();
    const reasons = await api.getAbsenteeismReasons();

    res.render('simulacao', {
      activeSimulacao: true,
      collaborators,
      reasons
    });
  } catch (error) {
    res.redirect('/login');
  }
};

const metrics = async (req: Request, res: Response) => {
  const token = getToken(req);
  if (!token) return res.redirect('/login');

  try {
    const api = new RelatoriosAPI(token);
    // Initial metrics with 100%
    const data = await api.postModelMetrics(100);
    res.render('metrics', {
      activeMetrics: true,
      metrics: data.metrics,
      scatterData: JSON.stringify(data.scatter_plot_data)
    });
  } catch (error) {
    res.redirect('/login');
  }
};

const apiSimulate = async (req: Request, res: Response) => {
  const token = getToken(req);
  if (!token) return res.status(401).json({ error: 'Unauthorized' });

  try {
    const api = new RelatoriosAPI(token);
    const result = await api.postCollaboratorSimulation(req.body);
    res.json(result);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};

const apiMetrics = async (req: Request, res: Response) => {
  const token = getToken(req);
  if (!token) return res.status(401).json({ error: 'Unauthorized' });

  try {
    const api = new RelatoriosAPI(token);
    const result = await api.postModelMetrics(req.body.percentage);
    res.json(result);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};

const logout = (req: Request, res: Response) => {
  res.setHeader('Set-Cookie', 'dialga_token=; Path=/; HttpOnly; Max-Age=0');
  res.redirect('/login');
};

export default { login, postLogin, dashboard, simulacao, metrics, logout, apiSimulate, apiMetrics };
