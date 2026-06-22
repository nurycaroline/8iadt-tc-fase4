import request from 'supertest';

import { createApp } from '../src/app.js';
import { abrirBanco } from '../src/db/index.js';
import { criarRepositorios } from '../src/db/repositorios.js';

function appDeTeste() {
  const db = abrirBanco(':memory:');
  const repos = criarRepositorios(db);
  return { app: createApp({ db, repos }), repos };
}

describe('CRUD de pacientes', () => {
  it('cria, lista e exclui um paciente', async () => {
    const { app } = appDeTeste();

    const criado = await request(app)
      .post('/pacientes')
      .send({ primeiro_nome: 'Maria', idade: 31, gestante: true, idade_gestacional_semanas: 28 });
    expect(criado.status).toBe(201);
    expect(criado.body.id).toBeTruthy();
    expect(criado.body.gestante).toBe(true);
    expect(criado.body.idade_gestacional_semanas).toBe(28);

    const lista = await request(app).get('/pacientes');
    expect(lista.status).toBe(200);
    expect(lista.body).toHaveLength(1);

    const del = await request(app).delete(`/pacientes/${criado.body.id}`);
    expect(del.status).toBe(204);

    const listaVazia = await request(app).get('/pacientes');
    expect(listaVazia.body).toHaveLength(0);
  });

  it('zera idade gestacional quando gestante = false', async () => {
    const { app } = appDeTeste();
    const criado = await request(app)
      .post('/pacientes')
      .send({ primeiro_nome: 'Ana', idade: 27, gestante: false, idade_gestacional_semanas: 20 });
    expect(criado.status).toBe(201);
    expect(criado.body.idade_gestacional_semanas).toBeNull();
  });

  it('rejeita payload inválido com 400', async () => {
    const { app } = appDeTeste();
    const resp = await request(app).post('/pacientes').send({ idade: 30 });
    expect(resp.status).toBe(400);
  });

  it('exclui caso em cascata e remove artefatos do storage', async () => {
    const { app, repos } = appDeTeste();
    const criado = await request(app)
      .post('/pacientes')
      .send({ primeiro_nome: 'Júlia', idade: 35, gestante: false });
    const pacienteId = criado.body.id;
    repos.casos.criar({
      paciente_id: pacienteId,
      relatorio_url: '/tmp/relatorio-inexistente.html',
      risco_detectado: 'ALTO',
    });
    expect(repos.casos.porPaciente(pacienteId)).toHaveLength(1);

    const del = await request(app).delete(`/pacientes/${pacienteId}`);
    expect(del.status).toBe(204);
    expect(repos.casos.porPaciente(pacienteId)).toHaveLength(0);
  });

  it('404 ao excluir paciente inexistente', async () => {
    const { app } = appDeTeste();
    const resp = await request(app).delete('/pacientes/nao-existe');
    expect(resp.status).toBe(404);
  });
});
