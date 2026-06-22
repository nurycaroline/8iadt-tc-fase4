import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'

import { api } from '../api'
import { Carregando, Erro, Vazio } from '../components/Estado'
import { mensagemErro } from '../erros'
import type { Paciente } from '../types'

function descricao(p: Paciente): string {
  const partes: string[] = []
  if (p.idade != null) partes.push(`${p.idade} anos`)
  if (p.gestante) {
    partes.push(
      p.idade_gestacional_semanas != null
        ? `gestante · ${p.idade_gestacional_semanas} sem`
        : 'gestante',
    )
  } else {
    partes.push('não gestante')
  }
  return partes.join(' · ')
}

export function Pacientes() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { data, isPending, error, refetch } = useQuery({
    queryKey: ['pacientes'],
    queryFn: api.listarPacientes,
  })

  const excluir = useMutation({
    mutationFn: (id: string) => api.excluirPaciente(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['pacientes'] }),
  })

  function confirmarExclusao(p: Paciente) {
    if (confirm(`Excluir a paciente ${p.primeiro_nome} e seus casos?`)) excluir.mutate(p.id)
  }

  return (
    <section>
      <div className="cabecalho-pagina">
        <h2>Pacientes</h2>
        <button className="primario" onClick={() => navigate('/pacientes/nova')}>
          + Dar entrada
        </button>
      </div>

      {isPending && <Carregando />}
      {error && <Erro mensagem={mensagemErro(error)} onTentar={refetch} />}
      {data?.length === 0 && (
        <Vazio texto="Nenhuma paciente cadastrada. Use “Dar entrada” para começar o monitoramento." />
      )}

      {data && data.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Paciente</th>
              <th>Perfil</th>
              <th aria-label="Ações" />
            </tr>
          </thead>
          <tbody>
            {data.map((p) => (
              <tr key={p.id}>
                <td>{p.primeiro_nome}</td>
                <td className="card-sub">{descricao(p)}</td>
                <td>
                  <div className="acoes">
                    <Link to={`/pacientes/${p.id}/enviar`}>
                      <button>Enviar caso</button>
                    </Link>
                    <button className="perigo" onClick={() => confirmarExclusao(p)}>
                      Excluir
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}
