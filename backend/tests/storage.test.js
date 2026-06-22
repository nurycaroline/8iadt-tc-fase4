import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { LocalStorage } from '../src/storage/index.js';

describe('LocalStorage', () => {
  it('salva e abre um artefato (round trip)', async () => {
    const base = fs.mkdtempSync(path.join(os.tmpdir(), 'storage-'));
    const storage = new LocalStorage(base);
    const url = await storage.salvar(Buffer.from('ola mundo'), 'sub/arquivo.txt');
    const caminho = await storage.abrir(url);
    expect(fs.readFileSync(caminho, 'utf-8')).toBe('ola mundo');
    await storage.remover(url);
    expect(fs.existsSync(caminho)).toBe(false);
  });
});
