// Configuração via variáveis de ambiente (dotenv). Segredos NUNCA vêm do Git — ver .env.example.
import 'dotenv/config';

export const config = {
  port: Number(process.env.PORT || 3000),
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
  },
  logLevel: process.env.LOG_LEVEL || 'info',
};
