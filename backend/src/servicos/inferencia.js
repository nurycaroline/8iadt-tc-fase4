// Cliente do serviço de IA (FastAPI): POST {AI_SERVICE_URL}/inferencia com o payload do contrato §1.
import axios from 'axios';

import { config } from '../config.js';

export function criarClienteInferencia({
  baseUrl = config.aiServiceUrl,
  timeout = config.aiTimeoutMs,
} = {}) {
  return async function inferir(payload) {
    const { data } = await axios.post(`${baseUrl}/inferencia`, payload, {
      timeout,
      headers: { 'Content-Type': 'application/json' },
    });
    return data;
  };
}
