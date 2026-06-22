import { abrirBanco } from '../src/db/index.js';
import { criarRepositorios } from '../src/db/repositorios.js';
import { limparExpirados } from '../src/servicos/retencao.js';

function isoDiasAtras(dias) {
  return new Date(Date.now() - dias * 24 * 60 * 60 * 1000).toISOString();
}

function semear(repos) {
  const paciente = repos.pacientes.criar({ primeiro_nome: 'Maria', idade: 31 });
  repos.casos.criar({
    id: 'antigo',
    paciente_id: paciente.id,
    relatorio_url: 'memory://relatorios/antigo.html',
    risco_detectado: 'ALTO',
    timestamp: isoDiasAtras(120),
  });
  repos.casos.criar({
    id: 'recente',
    paciente_id: paciente.id,
    risco_detectado: 'BAIXO',
    timestamp: isoDiasAtras(5),
  });
}

describe('Política de retenção (F7-04)', () => {
  it('não remove nada quando o TTL está desabilitado (0)', async () => {
    const repos = criarRepositorios(abrirBanco(':memory:'));
    semear(repos);
    const resumo = await limparExpirados({ repos, ttlDias: 0 });
    expect(resumo.habilitado).toBe(false);
    expect(repos.casos.listar()).toHaveLength(2);
  });

  it('remove apenas os casos além do TTL, apaga artefatos e audita', async () => {
    const repos = criarRepositorios(abrirBanco(':memory:'));
    semear(repos);
    const removidosStorage = [];
    const storage = { remover: async (url) => removidosStorage.push(url) };

    const resumo = await limparExpirados({ repos, storage, ttlDias: 90 });

    expect(resumo.removidos).toBe(1);
    expect(resumo.casos).toEqual(['antigo']);
    expect(repos.casos.obter('antigo')).toBeNull();
    expect(repos.casos.obter('recente')).toBeTruthy();
    expect(removidosStorage).toContain('memory://relatorios/antigo.html');

    const trilha = repos.auditoria.listar();
    expect(trilha.some((e) => e.acao === 'retencao_remover' && e.case_id === 'antigo')).toBe(true);
  });
});
