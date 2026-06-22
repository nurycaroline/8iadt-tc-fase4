import request from 'supertest';

import { createApp } from '../src/app.js';

describe('GET /health', () => {
  it('responde 200 com status ok', async () => {
    const app = createApp();
    const resp = await request(app).get('/health');
    expect(resp.status).toBe(200);
    expect(resp.body).toEqual({ status: 'ok' });
  });
});
