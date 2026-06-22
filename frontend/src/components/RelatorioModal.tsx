import { useEffect, useRef } from 'react'

// Pré-visualização do relatório clínico no dashboard (Fase 6 / F6-04, docs/06 §5).
// Modal acessível: role=dialog + aria-modal, foco inicial no botão Fechar e tecla Esc.
// O relatório é exibido num iframe (HTML ou PDF, conforme o que o serviço de IA gerou).
export function RelatorioModal({ url, onFechar }: { url: string; onFechar: () => void }) {
  const fecharRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    fecharRef.current?.focus()
    function aoTeclar(evento: KeyboardEvent) {
      if (evento.key === 'Escape') onFechar()
    }
    document.addEventListener('keydown', aoTeclar)
    return () => document.removeEventListener('keydown', aoTeclar)
  }, [onFechar])

  return (
    <div className="modal-overlay" role="presentation" onClick={onFechar}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label="Relatório clínico do caso"
        onClick={(evento) => evento.stopPropagation()}
      >
        <header className="modal-cabecalho">
          <h3>Relatório clínico do caso</h3>
          <div className="modal-acoes">
            <a href={url} target="_blank" rel="noreferrer">
              <button type="button">Abrir em nova aba</button>
            </a>
            <button type="button" ref={fecharRef} className="primario" onClick={onFechar}>
              Fechar
            </button>
          </div>
        </header>
        <iframe className="modal-corpo" src={url} title="Relatório clínico do caso" />
        <p className="card-sub modal-rodape">
          Documento de apoio à decisão clínica gerado automaticamente. Não substitui a avaliação de
          profissionais de saúde.
        </p>
      </div>
    </div>
  )
}
