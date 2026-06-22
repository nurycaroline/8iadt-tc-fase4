// Bootstrap do backend: Express + http + socket.io. Sobe o servidor na porta de config.
import http from 'node:http';

import { Server } from 'socket.io';

import { createApp } from './app.js';
import { config } from './config.js';
import { logger } from './logger.js';
import { criarEmissorAlerta } from './realtime/alertas.js';

export function criarServidor(deps = {}) {
  const server = http.createServer();
  const io = new Server(server, { cors: { origin: '*' } });
  const emitirAlerta = deps.emitirAlerta || criarEmissorAlerta(io);
  const app = createApp({ ...deps, io, emitirAlerta });
  server.on('request', app);
  return { server, io, app };
}

// Sobe o servidor apenas quando executado diretamente (não ao importar nos testes).
const executadoDireto = process.argv[1] && import.meta.url === `file://${process.argv[1]}`;
if (executadoDireto) {
  const { server } = criarServidor();
  server.listen(config.port, () => logger.info({ port: config.port }, 'backend ouvindo'));
}
