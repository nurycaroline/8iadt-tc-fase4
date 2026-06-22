// POST /analisar: upload → storage → serviço de IA (contrato §1) → persiste Caso → responde o risco.
import { Router } from 'express';
import multer from 'multer';

import { config } from '../config.js';
import { comCaso } from '../logger.js';
import { normalizarCaseId, pacienteMinimo } from '../seguranca/pseudonimizacao.js';

// Validação de upload (Fase 7 — F7-06): só tipos esperados por campo. Prefixo "x/" casa por família.
const MIME_PERMITIDOS = {
  video_cicatriz: ['video/', 'image/'],
  video_fisioterapia: ['video/', 'image/'],
  audio: ['audio/', 'video/'],
  sinais_vitais: ['text/csv', 'text/plain', 'application/vnd.ms-excel', 'application/octet-stream'],
};

function tipoPermitido(fieldname, mimetype) {
  const permitidos = MIME_PERMITIDOS[fieldname];
  if (!permitidos) return false;
  return permitidos.some((p) => (p.endsWith('/') ? mimetype.startsWith(p) : mimetype === p));
}

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 50 * 1024 * 1024 },
  fileFilter(_req, file, cb) {
    if (tipoPermitido(file.fieldname, file.mimetype)) return cb(null, true);
    const erro = new Error(`tipo de arquivo não permitido em "${file.fieldname}": ${file.mimetype}`);
    erro.statusCode = 400;
    return cb(erro);
  },
});

const CAMPOS_ARQUIVO = [
  { name: 'video_cicatriz', maxCount: 1 },
  { name: 'video_fisioterapia', maxCount: 1 },
  { name: 'audio', maxCount: 1 },
  { name: 'sinais_vitais', maxCount: 1 },
];

// Mapeia o campo do upload → chave de URL no contrato §1.
const MAPA_URL = {
  video_cicatriz: 'video_cicatriz_url',
  video_fisioterapia: 'video_fisioterapia_url',
  audio: 'audio_url',
};

// Wrapper que converte erros do multer (tamanho/tipo) em 400 JSON em vez de 500.
function receberUploads(req, res, next) {
  upload.fields(CAMPOS_ARQUIVO)(req, res, (err) => {
    if (err) {
      const status = err.statusCode || (err.code === 'LIMIT_FILE_SIZE' ? 413 : 400);
      return res.status(status).json({ erro: err.message || 'upload inválido' });
    }
    return next();
  });
}

export function criarRotasAnalisar({ repos, storage, inferir, emitirAlerta = null }) {
  const router = Router();

  router.post('/analisar', receberUploads, async (req, res) => {
    let caseId;
    try {
      caseId = normalizarCaseId(req.body.case_id, { isProduction: config.isProduction });
    } catch (err) {
      return res.status(err.statusCode || 400).json({ erro: err.message });
    }
    const log = comCaso(caseId);

    const paciente = repos.pacientes.obter(req.body.paciente_id);
    if (!paciente) {
      return res.status(404).json({ erro: 'paciente não encontrado', case_id: caseId });
    }

    // 1) Sobe os arquivos ao storage e monta as URLs do contrato §1.
    // Pseudonimização (F7-05): envia o contexto MÍNIMO da paciente à IA (sem o nome).
    const payload = { case_id: caseId, paciente: pacienteMinimo(paciente) };
    const urlsCaso = {};
    const arquivos = req.files || {};
    try {
      for (const [campo, urlKey] of Object.entries(MAPA_URL)) {
        const arquivo = arquivos[campo]?.[0];
        if (arquivo) {
          const url = await storage.salvar(arquivo.buffer, `${caseId}/${campo}-${arquivo.originalname}`);
          payload[urlKey] = url;
          urlsCaso[urlKey] = url;
        }
      }
      const csv = arquivos.sinais_vitais?.[0];
      if (csv) {
        const url = await storage.salvar(csv.buffer, `${caseId}/sinais_vitais-${csv.originalname}`);
        payload.dados_vitais = { csv_url: url };
        urlsCaso.sinais_vitais_csv_url = url;
      }
      if (req.body.texto_clinico) {
        payload.texto_clinico = req.body.texto_clinico;
      }
    } catch (err) {
      log.error({ err: String(err) }, 'Falha ao salvar upload no storage');
      return res.status(500).json({ erro: 'falha no armazenamento', case_id: caseId });
    }

    // 2) Chama o serviço de IA (Python). Indisponibilidade → 502/504 (upload preservado).
    let resultado;
    try {
      resultado = await inferir(payload);
    } catch (err) {
      const status = err.response ? 502 : 504;
      log.error({ err: String(err), status }, 'Serviço de IA indisponível');
      return res.status(status).json({ erro: 'serviço de IA indisponível', case_id: caseId });
    }

    // 3) Persiste o Caso (resultado + URLs) e responde o JSON de risco.
    const caso = repos.casos.criar({
      id: caseId,
      paciente_id: paciente.id,
      ...urlsCaso,
      texto_clinico: payload.texto_clinico ?? null,
      risco_detectado: resultado.risco_detectado,
      relatorio_url: resultado.relatorio_url ?? null,
      resultado_json: resultado,
      timestamp: resultado.timestamp,
    });
    log.info({ risco: resultado.risco_detectado }, 'Caso analisado e persistido');

    // Auditoria de acesso (F7-03): registra a análise (quem/quando/qual caso), sem dado clínico.
    repos.auditoria?.registrar({
      usuario: req.usuario,
      acao: 'analisar',
      recurso: 'POST /analisar',
      case_id: caseId,
    });

    // 4) Alerta em tempo real (MEDIO/ALTO) — integrado na Tarefa 3.3b (T11).
    if (emitirAlerta) emitirAlerta({ ...resultado, paciente, case_id: caseId });

    return res.json({ ...resultado, caso_id: caso.id });
  });

  return router;
}
