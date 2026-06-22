// Alerta em tempo real (Tarefa 3.3b): empurra o evento 'alerta' quando o risco é MEDIO/ALTO.
import { comCaso } from '../logger.js';

export const NIVEIS_ALERTA = new Set(['MEDIO', 'ALTO']);

export function criarEmissorAlerta(io) {
  return function emitir(resultado) {
    const risco = resultado?.risco_detectado;
    if (!NIVEIS_ALERTA.has(risco)) return false; // BAIXO não dispara alerta de risco.

    const paciente = resultado.paciente
      ? { id: resultado.paciente.id, primeiro_nome: resultado.paciente.primeiro_nome }
      : null;
    const alerta = {
      case_id: resultado.case_id,
      risco_detectado: risco,
      mensagem_alerta: resultado.mensagem_alerta,
      relatorio_url: resultado.relatorio_url ?? null,
      paciente,
      timestamp: resultado.timestamp,
    };
    io.emit('alerta', alerta);
    comCaso(resultado.case_id).info({ risco }, 'Alerta empurrado em tempo real');
    return true;
  };
}
