// Cliente do serviço de IA (FastAPI): POST {AI_SERVICE_URL}/inferencia com o payload do contrato §1.
import axios from 'axios';

import { config } from '../config.js';

export function criarClienteInferencia({
  baseUrl = config.aiServiceUrl,
  timeout = config.aiTimeoutMs,
  apiKey = config.aiServiceApiKey,
} = {}) {
  return async function inferir(payload) {
    const headers = { 'Content-Type': 'application/json' };
    // Credencial de serviço para o ai-service (Fase 7 — F7-01), quando configurada.
    if (apiKey) headers['x-api-key'] = apiKey;
    const { data } = await axios.post(`${baseUrl}/inferencia`, payload, { timeout, headers });
    return data;
  };
}
