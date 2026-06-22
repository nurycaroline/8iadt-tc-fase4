import { infoRisco } from '../risco'
import type { Alerta } from '../types'

// Banner fixo de alerta para risco MÉDIO/ALTO chegando em tempo real (docs/frontend.md §3.4/§4).
export function AlertaBanner({ alerta, onFechar }: { alerta: Alerta; onFechar?: () => void }) {
  const info = infoRisco(alerta.risco_detectado)
  const nome = alerta.paciente?.primeiro_nome ?? 'Paciente'
  return (
    <div className={`alerta-banner ${info.classe}`} role="alert" aria-live="assertive">
      <span className="alerta-banner-texto">
        <span aria-hidden="true">{info.icone}</span> <strong>Alerta {info.rotulo.toLowerCase()}:</strong>{' '}
        {nome} — {alerta.mensagem_alerta}
      </span>
      {onFechar && (
        <button type="button" className="alerta-banner-fechar" onClick={onFechar} aria-label="Fechar alerta">
          ×
        </button>
      )}
    </div>
  )
}
