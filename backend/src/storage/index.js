// Seletor de storage por env (STORAGE_BACKEND): 'local' (padrão) ou 'azure'.
import { config } from '../config.js';
import { logger } from '../logger.js';
import { AzureBlobStorage } from './azureBlob.js';
import { LocalStorage } from './local.js';

export function criarStorage(backend = config.storageBackend) {
  if ((backend || 'local').toLowerCase() === 'azure') {
    try {
      return new AzureBlobStorage();
    } catch (err) {
      logger.warn({ err: String(err) }, 'Storage Azure indisponível; usando fallback local.');
      return new LocalStorage();
    }
  }
  return new LocalStorage();
}

export { AzureBlobStorage, LocalStorage };
