// Estados de UI reaproveitáveis: carregando, erro e vazio (docs/frontend.md §7).
export function Carregando({ texto = 'Carregando…' }: { texto?: string }) {
  return (
    <div className="estado" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" /> {texto}
    </div>
  )
}

export function Erro({ mensagem, onTentar }: { mensagem: string; onTentar?: () => void }) {
  return (
    <div className="estado estado-erro" role="alert">
      <p>⚠️ {mensagem}</p>
      {onTentar && (
        <button type="button" onClick={onTentar}>
          Tentar novamente
        </button>
      )}
    </div>
  )
}

export function Vazio({ texto }: { texto: string }) {
  return <p className="vazio">{texto}</p>
}
