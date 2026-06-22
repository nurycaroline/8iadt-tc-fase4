import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import { api } from '../api'
import { Carregando, Erro, Vazio } from '../components/Estado'
import { RiscoBadge } from '../components/RiscoBadge'
import { mensagemErro } from '../erros'
import type { Risco } from '../types'

const FILTROS: (Risco | 'TODOS')[] = ['TODOS', 'ALTO', 'MEDIO', 'BAIXO']

// Histórico de casos com filtro por risco (docs/frontend.md §3.6).
export function Historico() {
  const { data, isPending, error, refetch } = useQuery({
    queryKey: ['casos'],
    queryFn: api.listarCasos,
  })
  const [filtro, setFiltro] = useState<Risco | 'TODOS'>('TODOS')

  const filtrados = (data ?? []).filter((c) => filtro === 'TODOS' || c.risco_detectado === filtro)

  return (
    <section>
      <div className="cabecalho-pagina">
        <h2>Histórico de casos</h2>
        <div className="acoes">
          {FILTROS.map((f) => (
            <button key={f} className={f === filtro ? 'primario' : ''} onClick={() => setFiltro(f)}>
              {f === 'TODOS' ? 'Todos' : f}
            </button>
          ))}
        </div>
      </div>

      {isPending && <Carregando />}
      {error && <Erro mensagem={mensagemErro(error)} onTentar={refetch} />}
      {!isPending && !error && filtrados.length === 0 && <Vazio texto="Nenhum caso para este filtro." />}

      {!isPending && !error && filtrados.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Paciente</th>
              <th>Risco</th>
              <th>Data</th>
              <th aria-label="Ações" />
            </tr>
          </thead>
          <tbody>
            {filtrados.map((c) => (
              <tr key={c.id}>
                <td>{c.paciente?.primeiro_nome ?? 'Paciente'}</td>
                <td>
                  <RiscoBadge risco={c.risco_detectado} />
                </td>
                <td className="card-sub">{new Date(c.timestamp).toLocaleString('pt-BR')}</td>
                <td>
                  <Link to={`/casos/${c.id}`}>
                    <button>Abrir</button>
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}
