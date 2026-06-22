import { jest } from '@jest/globals';
import { io as Client } from 'socket.io-client';
import request from 'supertest';

import { abrirBanco } from '../src/db/index.js';
import { criarRepositorios } from '../src/db/repositorios.js';
import { criarServidor } from '../src/server.js';

const storageFake = {
  salvar: async (_b, nome) => `memory://${nome}`,
  abrir: async (u) => u,
  remover: async () => {},
};

function respostaIA(risco) {
  return {
    timestamp: '2026-06-10T21:15:00Z',
    case_id: 'c-1',
    risco_detectado: risco,
    evidencias: {},
    mensagem_alerta: `Risco ${risco}`,
    relatorio_url: null,
  };
}

describe('Alerta em tempo real (socket.io)', () => {
  let server;
  let porta;
  let cliente;

  function subir(inferir) {
    const db = abrirBanco(':memory:');
    const repos = criarRepositorios(db);
    const paciente = repos.pacientes.criar({ primeiro_nome: 'Maria', gestante: false });
    const r = criarServidor({ db, repos, storage: storageFake, inferir });
    server = r.server;
    return new Promise((resolve) => {
      server.listen(0, () => {
        porta = server.address().port;
        resolve({ paciente });
      });
    });
  }

  afterEach(async () => {
    if (cliente) cliente.close();
    if (server) await new Promise((res) => server.close(res));
  });

  it('empurra o evento alerta ao processar um caso ALTO', async () => {
    const inferir = jest.fn(async () => respostaIA('ALTO'));
    const { paciente } = await subir(inferir);

    const recebido = new Promise((resolve) => {
      cliente = Client(`http://127.0.0.1:${porta}`, { transports: ['websocket'] });
      cliente.on('alerta', resolve);
    });
    await new Promise((res) => cliente.on('connect', res));

    await request(`http://127.0.0.1:${porta}`)
      .post('/analisar')
      .field('paciente_id', paciente.id)
      .field('texto_clinico', 'caso');

    const alerta = await recebido;
    expect(alerta.risco_detectado).toBe('ALTO');
    expect(alerta.mensagem_alerta).toContain('ALTO');
    expect(alerta.paciente.primeiro_nome).toBe('Maria');
  });
});
