import { Router } from 'express';
import mainController from '../controllers/main.js';
const router = Router();

// Auth
router.get('/login', mainController.login);
router.get('/logout', mainController.logout);

// App Routes
router.get('/', (req, res) => res.redirect('/dashboard'));
router.get('/dashboard', mainController.dashboard);
router.get('/simulacao', mainController.simulacao);
router.get('/metrics', mainController.metrics);

export default router;
