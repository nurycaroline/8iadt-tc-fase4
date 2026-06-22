// CLI da política de retenção (Fase 7 — F7-04). Uso: `npm run retencao` (ou via cron no deploy).
// Lê RETENTION_DAYS do ambiente; sem TTL configurado, não remove nada (no-op documentado).
import { abrirBanco } from '../db/index.js';
import { criarRepositorios } from '../db/repositorios.js';
import { logger } from '../logger.js';
import { limparExpirados } from '../servicos/retencao.js';
import { criarStorage } from '../storage/index.js';

async function main() {
  const db = abrirBanco();
  const repos = criarRepositorios(db);
  const storage = criarStorage();
  const resumo = await limparExpirados({ repos, storage });
  logger.info(resumo, 'Limpeza de retenção finalizada');
  db.close();
}

main().catch((err) => {
  logger.error({ err: String(err) }, 'Falha na rotina de retenção');
  process.exitCode = 1;
});
