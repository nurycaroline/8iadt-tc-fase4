import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { api } from '../api'
import { Carregando, Erro } from '../components/Estado'
import { RiscoBadge } from '../components/RiscoBadge'
import { mensagemErro } from '../erros'
import { infoRisco } from '../risco'

function Linha({ rotulo, valor }: { rotulo: string; valor?: string | number | null }) {
  return (
    <div className="kv">
      <span>{rotulo}</span>
      <span>{valor != null && valor !== '' ? valor : '—'}</span>
    </div>
  )
}

// Tela principal (docs/frontend.md §3.5): painéis por modalidade + painel de fusão.
export function DetalheCaso() {
  const { id } = useParams<{ id: string }>()
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
          <Linha rotulo="Categoria" valor={ev.audio?.categoria} />
          <Linha rotulo="Confiança" valor={ev.audio?.confianca != null ? ev.audio.confianca : null} />
        </div>

        <div className="painel">
          <h3>Texto / NLP</h3>
          <Linha rotulo="Achado" valor={ev.texto?.achado} />
          <Linha rotulo="Trecho" valor={ev.texto?.trecho} />
          {caso.texto_clinico && <p className="card-sub">“{caso.texto_clinico}”</p>}
        </div>

        <div className={`painel painel-fusao ${info.classe}`}>
          <h3>Fusão multimodal</h3>
          <div className="gauge">
            <RiscoBadge risco={caso.risco_detectado} />
          </div>
          <p>{caso.resultado_json?.mensagem_alerta ?? 'Sem mensagem de alerta.'}</p>
          {caso.relatorio_url && (
            <a href={api.relatorioUrl(caso.id)} target="_blank" rel="noreferrer">
              <button className="primario">Ver/baixar relatório</button>
            </a>
          )}
        </div>
      </div>
    </section>
  )
}
