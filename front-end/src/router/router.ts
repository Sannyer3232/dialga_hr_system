import { Router } from 'express';
import mainController from '../controllers/main.js';
import multer from 'multer';

const router = Router();
const upload = multer({ storage: multer.memoryStorage() });

// Auth
router.get('/login', mainController.login);
router.post('/login', mainController.postLogin);
router.get('/logout', mainController.logout);

// App Routes
router.get('/', (req, res) => res.redirect('/dashboard'));
router.get('/dashboard', mainController.dashboard);
router.get('/simulacao', mainController.simulacao);
router.get('/metrics', mainController.metrics);
router.get('/bulk', mainController.bulk);

// Proxy API Routes
router.post('/api/simulate', mainController.apiSimulate);
router.post('/api/metrics', mainController.apiMetrics);
router.post('/api/dashboard', mainController.apiDashboard);
router.post('/api/bulk', upload.single('file'), mainController.apiBulk);

export default router;
