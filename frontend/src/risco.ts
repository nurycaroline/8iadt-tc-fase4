// Mapeamento de risco → rótulo/ícone/cor. Acessibilidade: nunca depender só da cor
// (docs/frontend.md §7) — sempre acompanha ícone + texto.
import type { Risco } from './types'

export interface InfoRisco {
  rotulo: string
  icone: string
  classe: string
}

const MAPA: Record<Risco, InfoRisco> = {
  BAIXO: { rotulo: 'Baixo', icone: '🟢', classe: 'risco-baixo' },
  MEDIO: { rotulo: 'Médio', icone: '🟡', classe: 'risco-medio' },
  ALTO: { rotulo: 'Alto', icone: '🔴', classe: 'risco-alto' },
}

export function infoRisco(risco: Risco | null | undefined): InfoRisco {
  if (risco && risco in MAPA) return MAPA[risco]
  return { rotulo: 'Sem análise', icone: '⚪', classe: 'risco-indef' }
}
