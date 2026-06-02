import type { Request, Response } from 'express';

const login = (req: Request, res: Response) => {
  res.render('login', { layout: false }); // Render login without the main layout
};

const dashboard = async (req: Request, res: Response) => {
  res.render('dashboard', {
    activeDashboard: true,
  });
};

const simulacao = async (req: Request, res: Response) => {
  res.render('simulacao', {
    activeSimulacao: true,
  });
};

const metrics = async (req: Request, res: Response) => {
  res.render('metrics', {
    activeMetrics: true,
  });
};

const logout = (req: Request, res: Response) => {
  res.redirect('/login');
};



export default { login, dashboard, simulacao, metrics, logout };
