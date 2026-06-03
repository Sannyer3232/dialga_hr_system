import { Router } from 'express';
import mainController from '../controllers/main.js';
const router = Router();

// Auth
router.get('/login', mainController.login);
router.post('/login', mainController.postLogin);
router.get('/logout', mainController.logout);

// App Routes
router.get('/', (req, res) => res.redirect('/dashboard'));
router.get('/dashboard', mainController.dashboard);
router.get('/simulacao', mainController.simulacao);
router.get('/metrics', mainController.metrics);

// Proxy API Routes
router.post('/api/simulate', mainController.apiSimulate);
router.post('/api/metrics', mainController.apiMetrics);

export default router;
