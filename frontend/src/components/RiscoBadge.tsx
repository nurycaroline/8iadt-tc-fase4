import { infoRisco } from '../risco'
import type { Risco } from '../types'

// Selo de risco acessível: cor + ícone + texto.
export function RiscoBadge({ risco }: { risco: Risco | null | undefined }) {
  const info = infoRisco(risco)
  return (
    <span className={`badge ${info.classe}`}>
      <span aria-hidden="true">{info.icone}</span> {info.rotulo}
    </span>
  )
}
