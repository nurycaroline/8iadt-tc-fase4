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
    -- Trilha de auditoria de acesso (Fase 7 — F7-03): quem/quando/qual caso/ação. Registra apenas
    -- IDENTIFICADORES (usuário, case_id, ação, recurso) — nunca conteúdo clínico sensível.
    CREATE TABLE IF NOT EXISTS auditoria (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      usuario TEXT NOT NULL,
      acao TEXT NOT NULL,
      recurso TEXT,
      case_id TEXT,
      timestamp TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_auditoria_case ON auditoria(case_id);
  `);
}
