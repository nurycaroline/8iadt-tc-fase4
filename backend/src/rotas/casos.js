// Rotas de consulta de casos (Fase 5 — dashboard): visão geral, histórico, detalhe e relatório.
import fs from 'node:fs';
import path from 'node:path';

import { Router } from 'express';

const CONTENT_TYPE_POR_EXT = {
  '.html': 'text/html; charset=utf-8',
  '.htm': 'text/html; charset=utf-8',
  '.md': 'text/markdown; charset=utf-8',
  '.pdf': 'application/pdf',
  '.json': 'application/json; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
};

export function criarRotasCasos(repos) {
  const router = Router();

  // Registra acesso na trilha de auditoria (Fase 7 — F7-03): quem/quando/qual caso/ação.
  function auditar(req, acao, caseId = null) {
    repos.auditoria?.registrar({
      usuario: req.usuario,
      acao,
      recurso: req.originalUrl,
      case_id: caseId,
    });
  }

  // Lista de casos com o paciente embutido — alimenta a visão geral e o histórico do dashboard.
  router.get('/casos', (req, res) => {
    auditar(req, 'listar_casos');
    return res.json(repos.casos.listar());
  });

  // Detalhe de um caso (evidências por modalidade + fusão) — a tela principal do dashboard.
  router.get('/casos/:id', (req, res) => {
    const caso = repos.casos.obterComPaciente(req.params.id);
    if (!caso) return res.status(404).json({ erro: 'caso não encontrado' });
    auditar(req, 'ler_caso', req.params.id);
    return res.json(caso);
  });

  // Relatório automático do caso. Local: streama o arquivo; nuvem (SAS http): redireciona.
  router.get('/casos/:id/relatorio', (req, res) => {
    const caso = repos.casos.obter(req.params.id);
    if (!caso) return res.status(404).json({ erro: 'caso não encontrado' });
    auditar(req, 'ler_relatorio', req.params.id);

    const url = caso.relatorio_url;
    if (!url) return res.status(404).json({ erro: 'relatório indisponível para este caso' });

    if (/^https?:\/\//i.test(url)) return res.redirect(url); // Azure Blob (SAS com expiração).

    const arquivo = path.resolve(url);
    if (!fs.existsSync(arquivo) || !fs.statSync(arquivo).isFile()) {
      return res.status(404).json({ erro: 'arquivo do relatório não encontrado' });
    }
    const tipo = CONTENT_TYPE_POR_EXT[path.extname(arquivo).toLowerCase()] || 'application/octet-stream';
    res.type(tipo);
    return res.sendFile(arquivo);
  });

  return router;
}
