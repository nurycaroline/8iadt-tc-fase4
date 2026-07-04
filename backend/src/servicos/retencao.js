// Política de retenção/expiração de dados (Fase 7 — F7-04 / docs/07 §2). Remove casos cujo
// `timestamp` excede o TTL configurado (RETENTION_DAYS), apagando os artefatos no storage
// (blob no modo Azure; arquivo no modo local) e registrando a limpeza na trilha de auditoria.
//
// TTL ausente/0 → no-op (preserva o comportamento atual): a expiração automática é opt-in.
import { config } from '../config.js';
import { comCaso, logger } from '../logger.js';

const URLS_DE = (caso) => [
  caso.video_cicatriz_url,
  caso.audio_url,
  caso.sinais_vitais_csv_url,
  caso.relatorio_url,
];

/**
 * Remove os casos mais antigos que o TTL. Retorna o resumo da limpeza.
 * @param {object} opts
 * @param {object} opts.repos     repositórios (casos + auditoria)
 * @param {object} [opts.storage] adaptador de storage (remove artefatos)
 * @param {number} [opts.ttlDias] dias de retenção (default: config.retentionDays)
 * @param {Date}   [opts.agora]   instante de referência (injetável p/ testes)
 * @param {string} [opts.usuario] identidade registrada na auditoria
 */
export async function limparExpirados({
  repos,
  storage = null,
  ttlDias = config.retentionDays,
  agora = new Date(),
  usuario = 'sistema:retencao',
} = {}) {
  if (!ttlDias || ttlDias <= 0) {
    logger.info('Retenção desabilitada (RETENTION_DAYS=0); nenhuma limpeza executada.');
    return { habilitado: false, removidos: 0, casos: [] };
  }

  const limite = new Date(agora.getTime() - ttlDias * 24 * 60 * 60 * 1000).toISOString();
  const expirados = repos.casos.anterioresA(limite);
  const removidos = [];

  for (const caso of expirados) {
    if (storage) {
      for (const url of URLS_DE(caso)) {
        if (url) await storage.remover(url).catch(() => {});
      }
    }
    repos.casos.remover(caso.id);
    repos.auditoria?.registrar({
      usuario,
      acao: 'retencao_remover',
      recurso: `retencao ttl=${ttlDias}d`,
      case_id: caso.id,
    });
    comCaso(caso.id).info({ timestamp: caso.timestamp }, 'Caso removido por política de retenção');
    removidos.push(caso.id);
  }

  logger.info({ ttlDias, limite, total: removidos.length }, 'Retenção concluída');
  return { habilitado: true, removidos: removidos.length, casos: removidos };
}
