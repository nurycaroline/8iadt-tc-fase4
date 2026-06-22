// Logging estruturado (JSON) com pino, incluindo case_id para rastreabilidade ponta-a-ponta (DD13).
import pino from 'pino';

import { config } from './config.js';

export const logger = pino({ level: config.logLevel, base: { service: 'backend' } });

// Logger filho com o case_id fixado (mesma convenção do ai-service em Python).
export function comCaso(caseId) {
  return logger.child({ case_id: caseId || '-' });
}
