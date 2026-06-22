// Entrypoint de produção (Fase 7 — F7-07): carrega segredos do Key Vault (quando configurado)
// ANTES de avaliar a config/levantar o servidor, depois delega ao server.js.
import { carregarSegredos } from './seguranca/segredos.js';

await carregarSegredos();

// Import dinâmico após os segredos estarem em process.env (config lê env no import).
const { criarServidor } = await import('./server.js');
const { config } = await import('./config.js');
const { logger } = await import('./logger.js');

const { server } = criarServidor();
server.listen(config.port, () => logger.info({ port: config.port }, 'backend ouvindo'));
