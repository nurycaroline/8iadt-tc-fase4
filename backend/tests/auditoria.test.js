import { jest } from '@jest/globals';
import request from 'supertest';

import { createApp } from '../src/app.js';
import { abrirBanco } from '../src/db/index.js';
import { criarRepositorios } from '../src/db/repositorios.js';

const storageFake = {
  salvar: async (_buffer, nome) => `memory://${nome}`,
  abrir: async (url) => url,
  remover: async () => {},
};

const RESPOSTA_IA = {
  timestamp: '2026-06-10T21:15:00Z',
  case_id: 'gerado',
  risco_detectado: 'BAIXO',
  evidencias: {},
  mensagem_alerta: 'Sem sinais de risco.',
  relatorio_url: null,
};

function appDeTeste() {
  const db = abrirBanco(':memory:');
  const repos = criarRepositorios(db);
  const inferir = jest.fn(async () => RESPOSTA_IA);
  const app = createApp({ db, repos, storage: storageFake, inferir });
  return { app, repos, inferir };
}

describe('Auditoria de acesso (F7-03)', () => {
  it('registra a leitura de casos com usuário, ação e timestamp', async () => {
    const { app, repos } = appDeTeste();
    const paciente = repos.pacientes.criar({ primeiro_nome: 'Maria', idade: 31 });
    const caso = repos.casos.criar({ paciente_id: paciente.id, risco_detectado: 'BAIXO' });

    await request(app).get('/casos').set('x-user-id', 'enfermeira.ana');
    await request(app).get(`/casos/${caso.id}`).set('x-user-id', 'enfermeira.ana');

    const trilha = repos.auditoria.listar();
    const listar = trilha.find((e) => e.acao === 'listar_casos');
    const ler = trilha.find((e) => e.acao === 'ler_caso');
    expect(listar.usuario).toBe('enfermeira.ana');
    expect(listar.timestamp).toBeTruthy();
    expect(ler.case_id).toBe(caso.id);
  });

  it('marca o chamador como anonimo quando não há identidade', async () => {
    const { app, repos } = appDeTeste();
    await request(app).get('/casos');
    const trilha = repos.auditoria.listar();
    expect(trilha[0].usuario).toBe('anonimo');
  });

  it('não vaza conteúdo clínico na trilha (só identificadores)', async () => {
    const { app, repos } = appDeTeste();
    const paciente = repos.pacientes.criar({ primeiro_nome: 'Maria', idade: 31 });
    await request(app)
      .post('/analisar')
      .field('paciente_id', paciente.id)
      .field('texto_clinico', 'Puérpera com febre e dor na cicatriz');

    const evento = repos.auditoria.listar().find((e) => e.acao === 'analisar');
    expect(evento).toBeTruthy();
    const serializado = JSON.stringify(evento);
    expect(serializado).not.toContain('febre');
    expect(serializado).not.toContain('Maria');
  });
});
