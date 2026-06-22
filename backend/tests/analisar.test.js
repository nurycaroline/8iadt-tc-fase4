import { jest } from '@jest/globals';
import request from 'supertest';

import { createApp } from '../src/app.js';
import { abrirBanco } from '../src/db/index.js';
import { criarRepositorios } from '../src/db/repositorios.js';

// Storage falso (sem disco): devolve uma URL determinística por nome.
const storageFake = {
  salvar: async (_buffer, nome) => `memory://${nome}`,
  abrir: async (url) => url,
  remover: async () => {},
};

function appComMock(inferir) {
  const db = abrirBanco(':memory:');
  const repos = criarRepositorios(db);
  const paciente = repos.pacientes.criar({ primeiro_nome: 'Maria', idade: 31, gestante: false });
  const app = createApp({ db, repos, storage: storageFake, inferir });
  return { app, repos, paciente };
}

const RESPOSTA_IA = {
  timestamp: '2026-06-10T21:15:00Z',
  case_id: 'gerado',
  risco_detectado: 'ALTO',
  evidencias: { texto: { achado: 'sinal_infeccao', trecho: 'febre' } },
  mensagem_alerta: 'Suspeita de infecção puerperal.',
  relatorio_url: 'memory://relatorios/x.html',
};

describe('POST /analisar', () => {
  it('sobe upload, chama a IA, persiste o Caso e responde o risco', async () => {
    const inferir = jest.fn(async () => RESPOSTA_IA);
    const { app, repos, paciente } = appComMock(inferir);

    const resp = await request(app)
      .post('/analisar')
      .field('paciente_id', paciente.id)
      .field('texto_clinico', 'Puérpera com febre e dor na cicatriz')
      .attach('sinais_vitais', Buffer.from('SystolicBP\n150\n'), 'vitais.csv');

    expect(resp.status).toBe(200);
    expect(resp.body.risco_detectado).toBe('ALTO');
    expect(resp.body.caso_id).toBeTruthy();
    expect(inferir).toHaveBeenCalledTimes(1);
    // O payload enviado à IA segue o contrato §1.
    const payload = inferir.mock.calls[0][0];
    expect(payload.dados_vitais.csv_url).toContain('sinais_vitais');
    expect(payload.texto_clinico).toContain('febre');

    const casos = repos.casos.porPaciente(paciente.id);
    expect(casos).toHaveLength(1);
    expect(casos[0].risco_detectado).toBe('ALTO');
  });

  it('responde 502 quando o serviço de IA está indisponível', async () => {
    const inferir = jest.fn(async () => {
      const err = new Error('falhou');
      err.response = { status: 500 };
      throw err;
    });
    const { app, paciente } = appComMock(inferir);

    const resp = await request(app)
      .post('/analisar')
      .field('paciente_id', paciente.id)
      .field('texto_clinico', 'texto');

    expect(resp.status).toBe(502);
    expect(resp.body.case_id).toBeTruthy();
  });

  it('responde 404 quando o paciente não existe', async () => {
    const inferir = jest.fn();
    const { app } = appComMock(inferir);
    const resp = await request(app).post('/analisar').field('paciente_id', 'inexistente');
    expect(resp.status).toBe(404);
    expect(inferir).not.toHaveBeenCalled();
  });
});
