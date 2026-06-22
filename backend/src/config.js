// Configuração via variáveis de ambiente (dotenv). Segredos NUNCA vêm do Git — ver .env.example.
import 'dotenv/config';

const nodeEnv = process.env.NODE_ENV || 'development';
const isProduction = nodeEnv === 'production';

export const config = {
  port: Number(process.env.PORT || 3000),
  nodeEnv,
  isProduction,
  // URL do serviço de IA (FastAPI) chamado por axios em POST /analisar.
  aiServiceUrl: process.env.AI_SERVICE_URL || 'http://localhost:8000',
  aiTimeoutMs: Number(process.env.AI_TIMEOUT_MS || 120000),
  // Storage: 'local' (fallback em disco) ou 'azure' (Azure Blob Storage).
  storageBackend: process.env.STORAGE_BACKEND || 'local',
  storageDir: process.env.STORAGE_DIR || 'data/_storage',
  // Banco SQLite (better-sqlite3). Ignorado pelo Git.
  dbPath: process.env.DB_PATH || 'data/_storage/app.sqlite',
  azure: {
    connectionString: process.env.AZURE_STORAGE_CONNECTION_STRING || '',
    container: process.env.AZURE_STORAGE_CONTAINER || 'monitoramento',
    sasExpiryMinutes: Number(process.env.AZURE_SAS_EXPIRY_MINUTES || 60),
    // Fase 7 (F7-07): carrega segredos do Azure Key Vault quando definido; fallback p/ env/.env.
    keyVaultUrl: process.env.AZURE_KEY_VAULT_URL || '',
  },
  // ── Fase 7 — Privacidade e Segurança (LGPD) ──
  // F7-01: credencial de serviço. Vazio => auth desabilitada (preserva a demo/fallback — DD10).
  // AUTH_REQUIRED=true força negar quando a credencial não está configurada (fail-safe explícito).
  apiKey: process.env.API_KEY || '',
  aiServiceApiKey: process.env.AI_SERVICE_API_KEY || '',
  authRequired: process.env.AUTH_REQUIRED === 'true',
  // F7-06: allowlist de origens (CSV). Vazio => '*' em dev e same-origin em produção.
  corsOrigins: (process.env.CORS_ORIGINS || '')
    .split(',')
    .map((o) => o.trim())
    .filter(Boolean),
  // F7-04: retenção de dados (dias). 0 => sem expiração automática (comportamento atual).
  retentionDays: Number(process.env.RETENTION_DAYS || 0),
  logLevel: process.env.LOG_LEVEL || 'info',
};
