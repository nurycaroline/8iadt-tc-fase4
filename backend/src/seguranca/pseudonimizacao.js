// Pseudonimização (Fase 7 — F7-05 / docs/07 §1). Garante `case_id` opaco e minimiza a PII enviada
// ao serviço de IA (o nome não é necessário para a decisão de risco e fica só no backend).
import { randomUUID } from 'node:crypto';

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function ehUuid(valor) {
  return typeof valor === 'string' && UUID_RE.test(valor);
}

/**
 * Normaliza o `case_id` recebido no corpo da requisição.
 * - Ausente  → gera um UUID opaco.
 * - Presente + UUID → usa como está.
 * - Presente + não-UUID → erro em produção (rejeita identificador legível); aceita em dev/demo.
 */
export function normalizarCaseId(caseIdBody, { isProduction = false } = {}) {
  if (!caseIdBody) return randomUUID();
  if (ehUuid(caseIdBody)) return caseIdBody;
  if (isProduction) {
    const erro = new Error('case_id deve ser opaco (UUID) em produção');
    erro.statusCode = 400;
    throw erro;
  }
  return caseIdBody;
}

/**
 * Contexto mínimo da paciente para o serviço de IA — SEM PII direta (nome). Mantém apenas o que a
 * decisão de risco usa (id pseudonimizado, idade, gestação). O nome permanece só no backend.
 */
export function pacienteMinimo(paciente) {
  if (!paciente) return paciente;
  return {
    id: paciente.id,
    idade: paciente.idade ?? null,
    gestante: Boolean(paciente.gestante),
    idade_gestacional_semanas: paciente.idade_gestacional_semanas ?? null,
  };
}
