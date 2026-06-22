// Seletor de storage por env (STORAGE_BACKEND): 'local' (padrão) ou 'azure'.
import { config } from '../config.js';
import { logger } from '../logger.js';
import { LocalStorage } from './local.js';

export function criarStorage(backend = config.storageBackend) {
  if ((backend || 'local').toLowerCase() === 'azure') {
    try {
      // O SDK Azure só é exigido no modo nuvem (configurado na Tarefa 3.4 / T13).
      return criarAzure();
    } catch (err) {
      logger.warn({ err: String(err) }, 'Storage Azure indisponível; usando fallback local.');
      return new LocalStorage();
    }
  }
  return new LocalStorage();
}

// Placeholder substituído pela implementação Azure na Tarefa 3.4 (T13).
function criarAzure() {
  throw new Error('Backend azure ainda não configurado');
}

export { LocalStorage };
