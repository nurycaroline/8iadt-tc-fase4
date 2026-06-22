import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import request from 'supertest';

import { createApp } from '../src/app.js';
import { abrirBanco } from '../src/db/index.js';
import { criarRepositorios } from '../src/db/repositorios.js';

function appDeTeste() {
  const db = abrirBanco(':memory:');
  const repos = criarRepositorios(db);
  return { app: createApp({ db, repos }), repos };
}

function semearCaso(repos, { risco = 'ALTO', relatorioUrl = null } = {}) {
  const paciente = repos.pacientes.criar({
    primeiro_nome: 'Maria',
    idade: 31,
    gestante: true,
    idade_gestacional_semanas: 30,
  });
  const caso = repos.casos.criar({
    paciente_id: paciente.id,
    risco_detectado: risco,
    relatorio_url: relatorioUrl,
    resultado_json: {
      risco_detectado: risco,
      mensagem_alerta: 'Sinal de infecção com febre.',
      evidencias: { sinais_vitais: { tipo: 'hipertensao', valor: '150/95' } },
    },
    timestamp: new Date().toISOString(),
  });
  return { paciente, caso };
}

describe('Consulta de casos (dashboard)', () => {
  it('GET /casos lista casos com o paciente embutido', async () => {
    const { app, repos } = appDeTeste();
    semearCaso(repos, { risco: 'ALTO' });

    const resp = await request(app).get('/casos');
    expect(resp.status).toBe(200);
    expect(resp.body).toHaveLength(1);
    expect(resp.body[0].risco_detectado).toBe('ALTO');
    expect(resp.body[0].paciente.primeiro_nome).toBe('Maria');
    expect(resp.body[0].paciente.gestante).toBe(true);
  });

  it('GET /casos/:id devolve o detalhe com evidências da fusão', async () => {
    const { app, repos } = appDeTeste();
    const { caso } = semearCaso(repos, { risco: 'MEDIO' });

    const resp = await request(app).get(`/casos/${caso.id}`);
    expect(resp.status).toBe(200);
    expect(resp.body.id).toBe(caso.id);
    expect(resp.body.resultado_json.evidencias.sinais_vitais.tipo).toBe('hipertensao');
    expect(resp.body.paciente.primeiro_nome).toBe('Maria');
  });

  it('GET /casos/:id retorna 404 para caso inexistente', async () => {
    const { app } = appDeTeste();
    const resp = await request(app).get('/casos/nao-existe');
    expect(resp.status).toBe(404);
  });

  it('GET /casos/:id/relatorio streama o arquivo local quando existe', async () => {
    const { app, repos } = appDeTeste();
    const arquivo = path.join(os.tmpdir(), `relatorio-teste-${Date.now()}.html`);
    fs.writeFileSync(arquivo, '<h1>Relatório</h1>');
    const { caso } = semearCaso(repos, { relatorioUrl: arquivo });

    const resp = await request(app).get(`/casos/${caso.id}/relatorio`);
    expect(resp.status).toBe(200);
    expect(resp.text).toContain('Relatório');
    fs.rmSync(arquivo, { force: true });
  });

  it('GET /casos/:id/relatorio redireciona quando a URL é http (Azure SAS)', async () => {
    const { app, repos } = appDeTeste();
    const { caso } = semearCaso(repos, {
      relatorioUrl: 'https://conta.blob.core.windows.net/monitoramento/abc.pdf?sas',
    });

    const resp = await request(app).get(`/casos/${caso.id}/relatorio`);
    expect(resp.status).toBe(302);
    expect(resp.headers.location).toContain('blob.core.windows.net');
  });

  it('GET /casos/:id/relatorio retorna 404 quando não há relatório', async () => {
    const { app, repos } = appDeTeste();
    const { caso } = semearCaso(repos, { relatorioUrl: null });

    const resp = await request(app).get(`/casos/${caso.id}/relatorio`);
    expect(resp.status).toBe(404);
  });
});

describe('Readiness (F5-06)', () => {
  it('GET /ready responde ready com as dependências ok', async () => {
    const { app } = appDeTeste();
    const resp = await request(app).get('/ready');
    expect(resp.status).toBe(200);
    expect(resp.body.status).toBe('ready');
  });
});
