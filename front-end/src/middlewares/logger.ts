import { type Request, type Response, type NextFunction } from 'express';
import fs from 'fs/promises';
import getEnv from '../utils/getEnv.js';

type LogType = 'simple' | 'complete';
const env = getEnv();

const pathLog = `${process.cwd()}/${env.LOGGER_PATH}`;
const fileLog = `${pathLog}/logs.log`;

async function creatLogPathLog() {
  try {
    await fs.access(pathLog);
  } catch (err) {
    await fs.mkdir(pathLog);
  }
}
function logger(type: LogType) {
  if (type === 'simple') {
    return async (req: Request, res: Response, next: NextFunction) => {
      await creatLogPathLog();
      const log = `${new Date().toISOString()} ${req.url} ${req.method} ${req.httpVersion}\n`;
      await fs.appendFile(fileLog, log);
      next();
    };
  } else {
    return async (req: Request, res: Response, next: NextFunction) => {
      await creatLogPathLog();
      const log = `${new Date().toISOString()} ${req.url} ${req.method} ${req.httpVersion} ${req.get('User-Agent')}\n`;
      await fs.appendFile(fileLog, log);
      next();
    };
  }
}

export default logger;
