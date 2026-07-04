// Rotas de gestão de pacientes (arquitetura §7): criar, listar, excluir (cascata no Caso + artefatos).
import { Router } from 'express';
import { z } from 'zod';

const PacienteInput = z.object({
  primeiro_nome: z.string().min(1, 'primeiro_nome é obrigatório'),
  idade: z.number().int().min(0).max(120).nullable().optional(),
  gestante: z.boolean().default(false),
  idade_gestacional_semanas: z.number().int().min(0).max(45).nullable().optional(),
});

export function criarRotasPacientes(repos, storage = null) {
  const router = Router();

  router.post('/pacientes', (req, res) => {
    const parse = PacienteInput.safeParse(req.body);
    if (!parse.success) {
      return res.status(400).json({ erro: 'validação', detalhes: parse.error.issues });
    }
    const paciente = repos.pacientes.criar(parse.data);
    return res.status(201).json(paciente);
  });

  router.get('/pacientes', (_req, res) => {
    return res.json(repos.pacientes.listar());
  });

  router.delete('/pacientes/:id', async (req, res) => {
    const { id } = req.params;
    if (!repos.pacientes.obter(id)) {
      return res.status(404).json({ erro: 'paciente não encontrado' });
    }
    // Remove artefatos dos casos no storage antes de apagar (cascata DB cuida das linhas).
    if (storage) {
      for (const caso of repos.casos.porPaciente(id)) {
        for (const url of [
          caso.video_cicatriz_url,
          caso.audio_url,
          caso.sinais_vitais_csv_url,
          caso.relatorio_url,
        ]) {
          if (url) await storage.remover(url).catch(() => {});
        }
      }
    }
    repos.pacientes.remover(id);
    return res.status(204).end();
  });

  return router;
}
