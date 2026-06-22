import request from 'supertest';

import { createApp } from '../src/app.js';
import { abrirBanco } from '../src/db/index.js';
import { criarRepositorios } from '../src/db/repositorios.js';

function appComChave(apiKey) {
  const db = abrirBanco(':memory:');
  const repos = criarRepositorios(db);
  return { app: createApp({ db, repos, apiKey }), repos };
}

describe('Autenticação por credencial de serviço (F7-01)', () => {
  it('libera as rotas quando API_KEY não está configurada (demo/dev)', async () => {
    const { app } = appComChave('');
    const resp = await request(app).get('/casos');
    expect(resp.status).toBe(200);
  });

  it('exige x-api-key nas rotas de dados quando a credencial está configurada', async () => {
    const { app } = appComChave('segredo-123');

    const semChave = await request(app).get('/casos');
    expect(semChave.status).toBe(401);

    const chaveErrada = await request(app).get('/casos').set('x-api-key', 'errada');
    expect(chaveErrada.status).toBe(401);

    const comChave = await request(app).get('/casos').set('x-api-key', 'segredo-123');
    expect(comChave.status).toBe(200);
  });

  it('mantém /health e /ready públicos mesmo com credencial configurada', async () => {
    const { app } = appComChave('segredo-123');
    expect((await request(app).get('/health')).status).toBe(200);
    expect((await request(app).get('/ready')).status).toBe(200);
  });
});
