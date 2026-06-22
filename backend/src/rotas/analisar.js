// POST /analisar: upload → storage → serviço de IA (contrato §1) → persiste Caso → responde o risco.
import { randomUUID } from 'node:crypto';

import { Router } from 'express';
import multer from 'multer';

import { comCaso } from '../logger.js';

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 50 * 1024 * 1024 },
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

export function criarRotasAnalisar({ repos, storage, inferir, emitirAlerta = null }) {
  const router = Router();

  router.post('/analisar', upload.fields(CAMPOS_ARQUIVO), async (req, res) => {
    const caseId = req.body.case_id || randomUUID();
    const log = comCaso(caseId);

    const paciente = repos.pacientes.obter(req.body.paciente_id);
    if (!paciente) {
      return res.status(404).json({ erro: 'paciente não encontrado', case_id: caseId });
    }

    // 1) Sobe os arquivos ao storage e monta as URLs do contrato §1.
    const payload = { case_id: caseId, paciente };
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

    // 4) Alerta em tempo real (MEDIO/ALTO) — integrado na Tarefa 3.3b (T11).
    if (emitirAlerta) emitirAlerta({ ...resultado, paciente, case_id: caseId });

    return res.json({ ...resultado, caso_id: caso.id });
  });

  return router;
}
