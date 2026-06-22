import request from 'supertest';

import { abrirBanco } from '../src/db/index.js';
import { createApp } from '../src/app.js';

describe('GET /health', () => {
  it('responde 200 com status ok', async () => {
    const app = createApp({ db: abrirBanco(':memory:') });
    const resp = await request(app).get('/health');
    expect(resp.status).toBe(200);
    expect(resp.body).toEqual({ status: 'ok' });
  });
});
