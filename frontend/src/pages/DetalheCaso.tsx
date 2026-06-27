import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { api } from '../api'
import { Carregando, Erro } from '../components/Estado'
import { RelatorioModal } from '../components/RelatorioModal'
import { RiscoBadge } from '../components/RiscoBadge'
import { mensagemErro } from '../erros'
import { infoRisco } from '../risco'
import type { SubEvidencia } from '../types'

function Linha({ rotulo, valor }: { rotulo: string; valor?: string | number | null }) {
  return (
    <div className="kv">
      <span>{rotulo}</span>
      <span>{valor != null && valor !== '' ? valor : '—'}</span>
    </div>
  )
}

// Formata uma subevidência ML da Fase 8 (depressão/violência) como "rótulo (confiança)".
function fmtSub(sub?: SubEvidencia | null): string | null {
  if (!sub?.rotulo) return null
  return sub.confianca != null ? `${sub.rotulo} (${sub.confianca})` : sub.rotulo
}

// Tela principal (docs/frontend.md §3.5): painéis por modalidade + painel de fusão.
export function DetalheCaso() {
  const { id } = useParams<{ id: string }>()
  const [previewAberto, setPreviewAberto] = useState(false)
  const {
    data: caso,
    isPending,
    error,
    refetch,
  } = useQuery({
    queryKey: ['caso', id],
    queryFn: () => api.obterCaso(id as string),
    enabled: Boolean(id),
  })

  if (isPending) return <Carregando texto="Carregando caso…" />
  if (error) return <Erro mensagem={mensagemErro(error)} onTentar={refetch} />
  if (!caso) return null

  const p = caso.paciente
  const ev = caso.resultado_json?.evidencias ?? {}
  const info = infoRisco(caso.risco_detectado)

  return (
    <section>
      <div className="cabecalho-pagina">
        <div>
          <h2 style={{ marginBottom: '0.25rem' }}>{p?.primeiro_nome ?? 'Paciente'}</h2>
          <span className="card-sub">
            {p?.idade != null ? `${p.idade} anos` : 'idade n/d'}
            {p?.gestante
              ? ` · gestante${p.idade_gestacional_semanas ? ` (${p.idade_gestacional_semanas} sem)` : ''}`
              : ' · não gestante'}{' '}
            · caso {caso.id.slice(0, 8)}
          </span>
        </div>
        <Link to="/dashboard">
          <button>← Voltar</button>
        </Link>
      </div>

      <div className="paineis">
        <div className="painel">
          <h3>Vídeo — cicatriz (YOLO)</h3>
          <Linha rotulo="Evento" valor={ev.video_cicatriz?.evento} />
          <Linha
            rotulo="Confiança"
            valor={ev.video_cicatriz?.confianca != null ? ev.video_cicatriz.confianca : null}
          />
        </div>

        <div className="painel">
          <h3>Vídeo — fisioterapia (pose)</h3>
          <Linha rotulo="Execução" valor={ev.video_fisioterapia?.execucao} />
          <Linha rotulo="Amplitude" valor={ev.video_fisioterapia?.amplitude} />
        </div>

        <div className="painel">
          <h3>Sinais vitais</h3>
          <Linha rotulo="Classe" valor={ev.sinais_vitais?.tipo} />
          <Linha rotulo="Valor" valor={ev.sinais_vitais?.valor} />
        </div>

        <div className="painel">
          <h3>Áudio</h3>
          <Linha rotulo="Violência (acústico)" valor={fmtSub(ev.audio?.acustico)} />
          <Linha rotulo="Depressão (fala)" valor={fmtSub(ev.audio?.texto?.depressao)} />
          <Linha rotulo="Violência (fala)" valor={fmtSub(ev.audio?.texto?.violencia)} />
          <Linha rotulo="Resumo" valor={ev.audio?.categoria} />
          {ev.audio?.transcricao && <p className="card-sub">“{ev.audio.transcricao}”</p>}
        </div>

        <div className="painel">
          <h3>Texto / NLP</h3>
          <Linha rotulo="Achado" valor={ev.texto?.achado} />
          <Linha rotulo="Trecho" valor={ev.texto?.trecho} />
          <Linha rotulo="Depressão" valor={fmtSub(ev.texto?.depressao)} />
          <Linha rotulo="Violência" valor={fmtSub(ev.texto?.violencia)} />
          {caso.texto_clinico && <p className="card-sub">“{caso.texto_clinico}”</p>}
        </div>

        <div className={`painel painel-fusao ${info.classe}`}>
          <h3>Fusão multimodal</h3>
          <div className="gauge">
            <RiscoBadge risco={caso.risco_detectado} />
          </div>
          <p>{caso.resultado_json?.mensagem_alerta ?? 'Sem mensagem de alerta.'}</p>
          {caso.relatorio_url ? (
            <div className="relatorio-acoes">
              <button
                type="button"
                className="primario"
                onClick={() => setPreviewAberto(true)}
              >
                Pré-visualizar relatório
              </button>
              <a href={api.relatorioUrl(caso.id)} target="_blank" rel="noreferrer">
                <button type="button">Baixar relatório</button>
              </a>
            </div>
          ) : (
            <p className="card-sub">Relatório indisponível para este caso.</p>
          )}
        </div>
      </div>

      {previewAberto && caso.relatorio_url && (
        <RelatorioModal url={api.relatorioUrl(caso.id)} onFechar={() => setPreviewAberto(false)} />
      )}
    </section>
  )
}
