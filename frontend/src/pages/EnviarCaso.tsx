import { useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { api } from '../api'

type Etapa = 'preenchendo' | 'enviando' | 'analisando' | 'erro'

const MODALIDADES: { campo: string; rotulo: string; accept: string }[] = [
  { campo: 'video_cicatriz', rotulo: 'Vídeo/foto da cicatriz', accept: 'image/*,video/*' },
  { campo: 'video_fisioterapia', rotulo: 'Vídeo da fisioterapia', accept: 'video/*' },
  { campo: 'audio', rotulo: 'Áudio do relato', accept: 'audio/*' },
  { campo: 'sinais_vitais', rotulo: 'Sinais vitais (CSV)', accept: '.csv,text/csv' },
]

// Envio dos dados do caso (docs/frontend.md §3.3): cada modalidade é opcional; o backend
// envia ao storage e chama a IA. Indicador de status enviando → analisando → concluído.
export function EnviarCaso() {
  const { id: pacienteId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const formRef = useRef<HTMLFormElement>(null)
  const [texto, setTexto] = useState('')
  const [etapa, setEtapa] = useState<Etapa>('preenchendo')
  const [erro, setErro] = useState<string | null>(null)

  async function enviar(e: React.FormEvent) {
    e.preventDefault()
    if (!pacienteId || !formRef.current) return
    setErro(null)

    const form = new FormData()
    form.append('paciente_id', pacienteId)
    if (texto.trim()) form.append('texto_clinico', texto.trim())

    let temArquivo = false
    for (const { campo } of MODALIDADES) {
      const input = formRef.current.elements.namedItem(campo) as HTMLInputElement | null
      const arquivo = input?.files?.[0]
      if (arquivo) {
        form.append(campo, arquivo)
        temArquivo = true
      }
    }

    if (!temArquivo && !texto.trim()) {
      setErro('Envie pelo menos uma modalidade (arquivo ou texto clínico).')
      return
    }

    setEtapa('enviando')
    try {
      setEtapa('analisando')
      const resultado = await api.analisar(form)
      navigate(`/casos/${resultado.caso_id}`)
    } catch {
      setErro('Falha ao analisar o caso. Verifique o serviço de IA e tente novamente.')
      setEtapa('erro')
    }
  }

  const processando = etapa === 'enviando' || etapa === 'analisando'

  return (
    <section>
      <h2>Enviar dados do caso</h2>
      <p className="dica">
        Envie as modalidades disponíveis desta paciente. O sistema cruza tudo (fusão multimodal) e
        classifica o risco, disparando alerta em tempo real quando necessário.
      </p>

      <form className="form" ref={formRef} onSubmit={enviar}>
        {MODALIDADES.map((m) => (
          <div className="campo" key={m.campo}>
            <label htmlFor={m.campo}>{m.rotulo}</label>
            <input id={m.campo} name={m.campo} type="file" accept={m.accept} />
          </div>
        ))}

        <div className="campo">
          <label htmlFor="texto">Texto clínico (laudo/evolução)</label>
          <textarea
            id="texto"
            rows={4}
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder="Ex.: relato de febre e dor na cicatriz…"
          />
        </div>

        {erro && <p className="aviso">{erro}</p>}
        {processando && (
          <p className="dica" role="status" aria-live="polite">
            <span className="spinner" aria-hidden="true" />{' '}
            {etapa === 'enviando' ? 'Enviando arquivos…' : 'Analisando (IA multimodal)…'}
          </p>
        )}

        <div className="acoes">
          <button className="primario" type="submit" disabled={processando}>
            Analisar caso
          </button>
          <button type="button" onClick={() => navigate('/pacientes')} disabled={processando}>
            Voltar
          </button>
        </div>
      </form>
    </section>
  )
}
