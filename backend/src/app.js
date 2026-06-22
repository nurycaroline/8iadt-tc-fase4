// Fábrica do app Express (testável). server.js adiciona http + socket.io e sobe o listen.
import express from 'express';
import pinoHttp from 'pino-http';

import { logger } from './logger.js';

// Middleware de log estruturado por requisição, anexando o case_id quando presente.
function logHttp() {
  return pinoHttp({
    logger,
    customProps: (req) => ({
      case_id: req.body?.case_id || req.headers['x-case-id'] || '-',
    }),
  });
}

/**
 * Cria o app Express. As dependências (db, storage, io, inferir) são injetáveis para os testes.
 * Rotas adicionais (pacientes, analisar) são montadas conforme as deps disponíveis.
 */
export function createApp(deps = {}) {
  const app = express();
  app.use(express.json({ limit: '2mb' }));
  app.use(logHttp());

  if (deps.io) app.set('io', deps.io);

  app.get('/health', (_req, res) => res.json({ status: 'ok' }));

  return app;
}
