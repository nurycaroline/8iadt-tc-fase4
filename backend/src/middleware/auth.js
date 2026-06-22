// Autenticação por credencial de serviço (Fase 7 — F7-01). Protege as rotas que expõem dados
// sensíveis; /health, /ready e os estáticos da SPA permanecem públicos (montados antes deste
// middleware). A credencial vem por variável de ambiente (segredo fora do Git — docs/07 §2).
//
// Regras:
// - API_KEY configurada      → exige o header `x-api-key` correto (401 caso contrário).
// - sem API_KEY + AUTH_REQUIRED=true → nega todas as chamadas (503): fail-safe explícito.
// - sem API_KEY (default)    → libera, preservando a demo/fallback local (DD10) e os testes,
//   marcando o chamador como `anonimo`. Em produção sem credencial, um aviso é emitido no startup
//   (ver app.js) recomendando configurar API_KEY.
//
// A identidade do chamador (`x-user-id`) é anexada em `req.usuario` para a trilha de auditoria
// (F7-03), sem exigir cadastro de usuários (fora de escopo).
import { config } from '../config.js';

export const USUARIO_ANONIMO = 'anonimo';

function identidade(req) {
  const id = req.headers['x-user-id'];
  if (typeof id === 'string' && id.trim()) return id.trim().slice(0, 120);
  return USUARIO_ANONIMO;
}

export function criarAutenticacao({
  apiKey = config.apiKey,
  authRequired = config.authRequired,
} = {}) {
  return function autenticar(req, res, next) {
    req.usuario = identidade(req);

    if (!apiKey) {
      if (authRequired) {
        // AUTH_REQUIRED sem credencial: não abrir o serviço silenciosamente.
        return res.status(503).json({ erro: 'serviço sem credencial configurada (API_KEY)' });
      }
      return next(); // Demo/dev: auth desabilitada (comportamento atual preservado).
    }

    const recebida = req.headers['x-api-key'];
    if (typeof recebida !== 'string' || recebida !== apiKey) {
      return res.status(401).json({ erro: 'credencial de serviço ausente ou inválida' });
    }
    return next();
  };
}
