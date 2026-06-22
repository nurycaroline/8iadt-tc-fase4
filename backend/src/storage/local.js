// Storage local (fallback da demo) — espelha a interface do app/storage.py (Python).
import fs from 'node:fs';
import path from 'node:path';

import { config } from '../config.js';

export class LocalStorage {
  constructor(baseDir = config.storageDir) {
    this.baseDir = baseDir;
  }

  // salvar(buffer|string, nome) -> caminho/URL local resolvível por abrir().
  async salvar(conteudo, nome) {
    const destino = path.join(this.baseDir, nome);
    await fs.promises.mkdir(path.dirname(destino), { recursive: true });
    await fs.promises.writeFile(destino, conteudo);
    return destino;
  }

  // No backend local a URL já é o caminho do arquivo.
  async abrir(url) {
    return url;
  }

  async remover(url) {
    await fs.promises.rm(url, { force: true });
  }
}
