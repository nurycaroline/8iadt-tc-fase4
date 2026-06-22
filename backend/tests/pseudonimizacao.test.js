import { ehUuid, normalizarCaseId, pacienteMinimo } from '../src/seguranca/pseudonimizacao.js';

describe('Pseudonimização (F7-05)', () => {
  it('gera um case_id opaco (UUID) quando ausente', () => {
    const id = normalizarCaseId(undefined);
    expect(ehUuid(id)).toBe(true);
  });

  it('aceita um case_id que já é UUID', () => {
    const uuid = '123e4567-e89b-42d3-a456-426614174000';
    expect(normalizarCaseId(uuid)).toBe(uuid);
  });

  it('rejeita case_id legível em produção', () => {
    expect(() => normalizarCaseId('caso-alto', { isProduction: true })).toThrow(/opaco/);
  });

  it('aceita case_id legível fora de produção (demo)', () => {
    expect(normalizarCaseId('caso-alto', { isProduction: false })).toBe('caso-alto');
  });

  it('pacienteMinimo remove a PII (primeiro_nome) e mantém o contexto clínico', () => {
    const minimo = pacienteMinimo({
      id: 'p1',
      primeiro_nome: 'Maria',
      idade: 31,
      gestante: true,
      idade_gestacional_semanas: 30,
    });
    expect(minimo.primeiro_nome).toBeUndefined();
    expect(minimo).toEqual({
      id: 'p1',
      idade: 31,
      gestante: true,
      idade_gestacional_semanas: 30,
    });
  });
});
