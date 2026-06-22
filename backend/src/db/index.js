// Persistência leve com better-sqlite3. Tabelas pacientes/casos (modelo de arquitetura §7).
import fs from 'node:fs';
import path from 'node:path';

import Database from 'better-sqlite3';

import { config } from '../config.js';

export function abrirBanco(dbPath = config.dbPath) {
  if (dbPath !== ':memory:') {
    fs.mkdirSync(path.dirname(dbPath), { recursive: true });
  }
  const db = new Database(dbPath);
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');
  migrar(db);
  return db;
}

function migrar(db) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS pacientes (
      id TEXT PRIMARY KEY,
      primeiro_nome TEXT NOT NULL,
      idade INTEGER,
      gestante INTEGER NOT NULL DEFAULT 0,
      idade_gestacional_semanas INTEGER,
      criado_em TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS casos (
      id TEXT PRIMARY KEY,
      paciente_id TEXT NOT NULL,
      video_cicatriz_url TEXT,
      video_fisioterapia_url TEXT,
      audio_url TEXT,
      sinais_vitais_csv_url TEXT,
      texto_clinico TEXT,
      risco_detectado TEXT,
      relatorio_url TEXT,
      resultado_json TEXT,
      timestamp TEXT NOT NULL,
      FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE
    );
  `);
}
