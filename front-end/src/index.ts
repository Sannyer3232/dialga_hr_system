import express from 'express';
import { engine } from 'express-handlebars';
import getEnv from './utils/getEnv.js';
import helpers from './views/helpers/helper.js';
import router from './router/router.js';
import logger from './middlewares/logger.js';
const PORT = getEnv();

const app = express();

app.engine(
  'hbs',
  engine({
    extname: '.hbs',
    defaultLayout: 'main',
    helpers,
  }),
);

app.set('view engine', 'hbs');
app.set('views', `${process.cwd()}/src/views`);
app.use(logger('simple'));
app.use(router);
app.use('/css', [
  express.static(`${process.cwd()}/src/public/css`),
  express.static(`${process.cwd()}/node_modules/bootstrap/dist/css/`),
]);
app.use('/js', [
  express.static(`${process.cwd()}/src/public/js`),
  express.static(`${process.cwd()}/node_modules/bootstrap/dist/js/`),
]);
app.use(
  '/vendor/chartjs',
  express.static(`${process.cwd()}/node_modules/chart.js/dist/`),
);
app.use('/img', express.static(`${process.cwd()}/src/public/img`));

app.listen(PORT, () => {
  console.log(
    `[Dialga] Servidor rodando na porta ${PORT}. Domínio sobre o tempo iniciado.`,
  );
});
