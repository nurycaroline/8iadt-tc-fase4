import { useQuery } from '@tanstack/react-query'
import { useEffect } from 'react'
import { Link } from 'react-router-dom'

import { api } from '../api'
import { Carregando, Erro, Vazio } from '../components/Estado'
import { RiscoBadge } from '../components/RiscoBadge'
import { mensagemErro } from '../erros'
import { useAlertas } from '../hooks/useAlertas'
import type { Caso, Risco } from '../types'

function contar(casos: Caso[], risco: Risco): number {
  return casos.filter((c) => c.risco_detectado === risco).length
}

export function Dashboard() {
  const { data, isPending, error, refetch } = useQuery({
    queryKey: ['casos'],
    queryFn: api.listarCasos,
  })
  const { ultimo } = useAlertas()

  // Recarrega a visão geral quando chega um alerta novo em tempo real.
  useEffect(() => {
    if (ultimo) refetch()
  }, [ultimo, refetch])

  return (
    <section>
      <div className="cabecalho-pagina">
        <h2>Monitoramento</h2>
      </div>

      {isPending && <Carregando />}
      {error && <Erro mensagem={mensagemErro(error)} onTentar={refetch} />}

      {data && (
        <>
          <div className="contadores">
            <div className="contador">
              <div className="numero">{contar(data, 'BAIXO')}</div>
              <div className="rotulo">🟢 Baixo</div>
            </div>
            <div className="contador">
              <div className="numero">{contar(data, 'MEDIO')}</div>
              <div className="rotulo">🟡 Médio</div>
            </div>
            <div className="contador">
              <div className="numero">{contar(data, 'ALTO')}</div>
              <div className="rotulo">🔴 Alto</div>
            </div>
          </div>

          {data.length === 0 ? (
            <Vazio texto="Nenhum caso analisado ainda. Dê entrada de uma paciente e envie um caso." />
          ) : (
            <div className="cards">
              {data.map((caso) => (
                <Link className="card" key={caso.id} to={`/casos/${caso.id}`}>
                  <div className="card-titulo">
                    <strong>{caso.paciente?.primeiro_nome ?? 'Paciente'}</strong>
                    <RiscoBadge risco={caso.risco_detectado} />
                  </div>
                  <div className="card-sub">
                    {caso.resultado_json?.mensagem_alerta ?? 'Caso analisado'}
                  </div>
                  <div className="card-sub">{new Date(caso.timestamp).toLocaleString('pt-BR')}</div>
                </Link>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  )
}
