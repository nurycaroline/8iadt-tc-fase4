// Storage Azure Blob (modo nuvem) — espelha app/storage_azure.py. URLs de leitura recebem SAS.
import os from 'node:os';
import path from 'node:path';
import { URL } from 'node:url';

import {
  BlobSASPermissions,
  BlobServiceClient,
  generateBlobSASQueryParameters,
} from '@azure/storage-blob';

import { config } from '../config.js';
import { logger } from '../logger.js';

export class AzureBlobStorage {
  constructor({
    connectionString = config.azure.connectionString,
    container = config.azure.container,
    sasMinutes = config.azure.sasExpiryMinutes,
  } = {}) {
    if (!connectionString) throw new Error('AZURE_STORAGE_CONNECTION_STRING ausente');
    this.service = BlobServiceClient.fromConnectionString(connectionString);
    this.container = container;
    this.sasMinutes = sasMinutes;
    this.containerClient = this.service.getContainerClient(container);
  }

  async salvar(conteudo, nome) {
    await this.containerClient.createIfNotExists();
    const blob = this.containerClient.getBlockBlobClient(nome);
    const buffer = Buffer.isBuffer(conteudo) ? conteudo : Buffer.from(conteudo);
    await blob.uploadData(buffer);
    logger.info({ container: this.container, nome }, 'Artefato enviado ao Blob');
    return this.#urlComSas(nome, blob);
  }

  async abrir(url) {
    const nome = this.#blobName(url);
    const blob = this.containerClient.getBlockBlobClient(nome);
    const destino = path.join(os.tmpdir(), path.basename(nome));
    await blob.downloadToFile(destino);
    return destino;
  }

  async remover(url) {
    const nome = this.#blobName(url);
    await this.containerClient.getBlockBlobClient(nome).deleteIfExists();
  }

  #urlComSas(nome, blob) {
    const sas = generateBlobSASQueryParameters(
      {
        containerName: this.container,
        blobName: nome,
        permissions: BlobSASPermissions.parse('r'),
        expiresOn: new Date(Date.now() + this.sasMinutes * 60000),
      },
      this.service.credential,
    ).toString();
    return `${blob.url}?${sas}`;
  }

  #blobName(url) {
    if (!url.toLowerCase().startsWith('http')) return url;
    const caminho = new URL(url).pathname.replace(/^\/+/, '');
    const prefixo = `${this.container}/`;
    return caminho.startsWith(prefixo) ? caminho.slice(prefixo.length) : caminho;
  }
}
