// Repositórios de Paciente e Caso (modelo de arquitetura §7). Devolve objetos no formato da API.
import { randomUUID } from 'node:crypto';

function paraPaciente(row) {
  if (!row) return null;
  return {
    id: row.id,
    primeiro_nome: row.primeiro_nome,
    idade: row.idade,
    gestante: Boolean(row.gestante),
    idade_gestacional_semanas: row.idade_gestacional_semanas,
    criado_em: row.criado_em,
  };
}

function paraCaso(row) {
  if (!row) return null;
  return {
    id: row.id,
    paciente_id: row.paciente_id,
    video_cicatriz_url: row.video_cicatriz_url,
    video_fisioterapia_url: row.video_fisioterapia_url,
    audio_url: row.audio_url,
    sinais_vitais_csv_url: row.sinais_vitais_csv_url,
    texto_clinico: row.texto_clinico,
    risco_detectado: row.risco_detectado,
    relatorio_url: row.relatorio_url,
    resultado_json: row.resultado_json ? JSON.parse(row.resultado_json) : null,
    timestamp: row.timestamp,
  };
}

// Caso + paciente embutido (consumido pelo dashboard: visão geral, histórico e detalhe).
function paraCasoComPaciente(row) {
  if (!row) return null;
  const caso = paraCaso(row);
  caso.paciente = {
    id: row.paciente_id,
    primeiro_nome: row.paciente_nome,
    idade: row.paciente_idade,
    gestante: Boolean(row.paciente_gestante),
    idade_gestacional_semanas: row.paciente_idade_gestacional,
  };
  return caso;
}

const SELECT_CASO_COM_PACIENTE = `
  SELECT c.*, p.primeiro_nome AS paciente_nome, p.idade AS paciente_idade,
         p.gestante AS paciente_gestante,
         p.idade_gestacional_semanas AS paciente_idade_gestacional
  FROM casos c
  JOIN pacientes p ON p.id = c.paciente_id`;

export function criarRepositorios(db) {
  const pacientes = {
    criar({ primeiro_nome, idade = null, gestante = false, idade_gestacional_semanas = null }) {
      const id = randomUUID();
      // gestante = false → idade gestacional não se aplica (arquitetura §7).
      const idadeGest = gestante ? idade_gestacional_semanas : null;
      db.prepare(
        `INSERT INTO pacientes
           (id, primeiro_nome, idade, gestante, idade_gestacional_semanas, criado_em)
         VALUES (?, ?, ?, ?, ?, ?)`,
      ).run(id, primeiro_nome, idade, gestante ? 1 : 0, idadeGest, new Date().toISOString());
      return pacientes.obter(id);
    },
    listar() {
      return db
        .prepare('SELECT * FROM pacientes ORDER BY criado_em DESC')
        .all()
        .map(paraPaciente);
    },
    obter(id) {
      return paraPaciente(db.prepare('SELECT * FROM pacientes WHERE id = ?').get(id));
    },
    remover(id) {
      return db.prepare('DELETE FROM pacientes WHERE id = ?').run(id).changes;
    },
  };

  const casos = {
    criar(caso) {
      const id = caso.id || randomUUID();
      db.prepare(
        `INSERT INTO casos
           (id, paciente_id, video_cicatriz_url, video_fisioterapia_url, audio_url,
            sinais_vitais_csv_url, texto_clinico, risco_detectado, relatorio_url,
            resultado_json, timestamp)
         VALUES (@id, @paciente_id, @video_cicatriz_url, @video_fisioterapia_url, @audio_url,
            @sinais_vitais_csv_url, @texto_clinico, @risco_detectado, @relatorio_url,
            @resultado_json, @timestamp)`,
      ).run({
        id,
        paciente_id: caso.paciente_id,
        video_cicatriz_url: caso.video_cicatriz_url ?? null,
        video_fisioterapia_url: caso.video_fisioterapia_url ?? null,
        audio_url: caso.audio_url ?? null,
        sinais_vitais_csv_url: caso.sinais_vitais_csv_url ?? null,
        texto_clinico: caso.texto_clinico ?? null,
        risco_detectado: caso.risco_detectado ?? null,
        relatorio_url: caso.relatorio_url ?? null,
        resultado_json: caso.resultado_json ? JSON.stringify(caso.resultado_json) : null,
        timestamp: caso.timestamp || new Date().toISOString(),
      });
      return casos.obter(id);
    },
    obter(id) {
      return paraCaso(db.prepare('SELECT * FROM casos WHERE id = ?').get(id));
    },
    obterComPaciente(id) {
      return paraCasoComPaciente(
        db.prepare(`${SELECT_CASO_COM_PACIENTE} WHERE c.id = ?`).get(id),
      );
    },
    listar() {
      return db
        .prepare(`${SELECT_CASO_COM_PACIENTE} ORDER BY c.timestamp DESC`)
        .all()
        .map(paraCasoComPaciente);
    },
    porPaciente(pacienteId) {
      return db
        .prepare('SELECT * FROM casos WHERE paciente_id = ? ORDER BY timestamp DESC')
        .all(pacienteId)
        .map(paraCaso);
    },
  };

  return { pacientes, casos };
}
