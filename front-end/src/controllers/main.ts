import type { Request, Response } from 'express';
import { RelatoriosAPI } from '../service/ApiService.js';
import { AuthService } from '../service/AuthService.js';
import FormData from 'form-data';

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
    // Persiste por 24 horas (86400 segundos)
    res.setHeader('Set-Cookie', `dialga_token=${token}; Path=/; HttpOnly; Max-Age=86400`);
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
    const user = await api.getUserInfo();
    const reasons = await api.getAbsenteeismReasons();

    res.render('dashboard', {
      activeDashboard: true,
      user,
      reasons,
      data: data,
      // Stringify for the client-side chart logic
      chartData: JSON.stringify(data.history.details),
      teamData: data.next_month.details
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
    const user = await api.getUserInfo();

    res.render('simulacao', {
      activeSimulacao: true,
      user,
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
    const user = await api.getUserInfo();

    res.render('metrics', {
      activeMetrics: true,
      user,
      metrics: data.metrics,
      scatterData: JSON.stringify(data.scatter_plot_data),
      scatterDataLength: data.scatter_plot_data.length
    });
  } catch (error) {
    res.redirect('/login');
  }
};

const bulk = async (req: Request, res: Response) => {
    const token = getToken(req);
    if (!token) return res.redirect('/login');
  
    try {
      const api = new RelatoriosAPI(token);
      const user = await api.getUserInfo();
  
      res.render('bulk', {
        activeBulk: true,
        user
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

const apiDashboard = async (req: Request, res: Response) => {
  const token = getToken(req);
  if (!token) return res.status(401).json({ error: 'Unauthorized' });

  try {
    const api = new RelatoriosAPI(token);
    const result = await api.postManagerDashboard(req.body);
    res.json(result);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};

const apiBulk = async (req: Request, res: Response) => {
    const token = getToken(req);
    if (!token) return res.status(401).json({ error: 'Unauthorized' });
    if (!req.file) return res.status(400).json({ error: 'No file uploaded' });
  
    try {
      const api = new RelatoriosAPI(token);
      
      const form = new FormData();
      form.append('file', req.file.buffer, {
          filename: req.file.originalname,
          contentType: req.file.mimetype,
      });

      const result = await api.postBulkPrediction(form as any);
      res.json(result);
    } catch (error: any) {
      console.error('Erro no processamento em lote:', error);
      res.status(500).json({ error: error.message });
    }
  };

const logout = (req: Request, res: Response) => {
  res.setHeader('Set-Cookie', 'dialga_token=; Path=/; HttpOnly; Max-Age=0');
  res.redirect('/login');
};

export default { login, postLogin, dashboard, simulacao, metrics, bulk, logout, apiSimulate, apiMetrics, apiDashboard, apiBulk };
