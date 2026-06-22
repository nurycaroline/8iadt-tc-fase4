// Bootstrap do backend: Express + http + socket.io. Sobe o servidor na porta de config.
import http from 'node:http';

import { Server } from 'socket.io';

import { createApp } from './app.js';
import { config } from './config.js';
import { logger } from './logger.js';
import { criarEmissorAlerta } from './realtime/alertas.js';

export function criarServidor(deps = {}) {
  // Indireção do emissor quebra a dependência circular app↔io (o app é criado antes do io).
  let emissor = deps.emitirAlerta || (() => {});
  const app = createApp({ ...deps, emitirAlerta: (resultado) => emissor(resultado) });

  // http.createServer(app) registra o app como handler base; o socket.io é anexado depois e
  // delega ao app as requisições que não são do seu próprio caminho (/socket.io/...).
  const server = http.createServer(app);
  const io = new Server(server, { cors: { origin: '*' } });
  if (!deps.emitirAlerta) emissor = criarEmissorAlerta(io);
  app.set('io', io);

  return { server, io, app };
}

// Sobe o servidor apenas quando executado diretamente (não ao importar nos testes).
const executadoDireto = process.argv[1] && import.meta.url === `file://${process.argv[1]}`;
if (executadoDireto) {
  const { server } = criarServidor();
  server.listen(config.port, () => logger.info({ port: config.port }, 'backend ouvindo'));
}
