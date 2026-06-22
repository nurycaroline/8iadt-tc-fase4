// Bootstrap do backend: Express + http + socket.io. Sobe o servidor na porta de config.
import http from 'node:http';

import { Server } from 'socket.io';

import { createApp } from './app.js';
import { config } from './config.js';
import { logger } from './logger.js';

export function criarServidor() {
  const server = http.createServer();
  const io = new Server(server, { cors: { origin: '*' } });
  const app = createApp({ io });
  server.on('request', app);
  return { server, io, app };
}

// Sobe o servidor apenas quando executado diretamente (não ao importar nos testes).
const executadoDireto = process.argv[1] && import.meta.url === `file://${process.argv[1]}`;
if (executadoDireto) {
  const { server } = criarServidor();
  server.listen(config.port, () => logger.info({ port: config.port }, 'backend ouvindo'));
}
