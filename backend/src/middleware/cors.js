// CORS por allowlist (Fase 7 — F7-06). Em produção a API é servida same-origin (via nginx), então
// o default é NÃO habilitar CORS cross-origin; em dev, libera para facilitar o `npm run dev` do
// dashboard. Defina CORS_ORIGINS (CSV) para uma allowlist explícita.
import { config } from '../config.js';

export function criarCors(origins) {
  const allowlist = origins !== undefined ? origins : config.corsOrigins;
  const liberarTudo = allowlist.length === 0 && !config.isProduction;

  return function cors(req, res, next) {
    const origem = req.headers.origin;

    if (liberarTudo) {
      res.setHeader('Access-Control-Allow-Origin', origem || '*');
      res.setHeader('Vary', 'Origin');
    } else if (origem && allowlist.includes(origem)) {
      res.setHeader('Access-Control-Allow-Origin', origem);
      res.setHeader('Vary', 'Origin');
    }
    // Sem origem na allowlist (e não-dev): não emite cabeçalhos CORS → o navegador bloqueia
    // cross-origin; requisições same-origin (a SPA servida pelo backend/nginx) seguem normais.

    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-api-key, x-user-id, x-case-id');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');

    if (req.method === 'OPTIONS') return res.sendStatus(204);
    return next();
  };
}

// Origens permitidas para o socket.io (mesma allowlist). '*' só em dev sem allowlist explícita.
export function origensSocket() {
  if (config.corsOrigins.length > 0) return config.corsOrigins;
  return config.isProduction ? false : '*';
}
