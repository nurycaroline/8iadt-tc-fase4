// Fábrica do app Express (testável). server.js adiciona http + socket.io e sobe o listen.
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import express from 'express';
import pinoHttp from 'pino-http';

import { abrirBanco } from './db/index.js';
import { criarRepositorios } from './db/repositorios.js';
import { logger } from './logger.js';
import { criarRotasAnalisar } from './rotas/analisar.js';
import { criarRotasPacientes } from './rotas/pacientes.js';
import { criarClienteInferencia } from './servicos/inferencia.js';
import { criarStorage } from './storage/index.js';

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
  const db = deps.db || abrirBanco();
  const repos = deps.repos || criarRepositorios(db);
  const storage = deps.storage || criarStorage();
  const inferir = deps.inferir || criarClienteInferencia();
  const emitirAlerta = deps.emitirAlerta || null;

  const app = express();
  app.use(express.json({ limit: '2mb' }));
  app.use(logHttp());

  if (deps.io) app.set('io', deps.io);
  app.set('repos', repos);
  app.set('storage', storage);

  app.get('/health', (_req, res) => res.json({ status: 'ok' }));
  app.use('/', criarRotasPacientes(repos, storage));
  app.use('/', criarRotasAnalisar({ repos, storage, inferir, emitirAlerta }));

  // Cliente mínimo de demonstração do alerta (servido em /).
  const publicDir = path.resolve(fileURLToPath(new URL('../public', import.meta.url)));
  app.use(express.static(publicDir));

  return app;
}
