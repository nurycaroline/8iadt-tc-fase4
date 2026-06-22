import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from '../api'

// Formulário curto de entrada da paciente (docs/frontend.md §3.2). Idade gestacional só
// aparece quando gestante = sim. Ao salvar, segue direto para o envio do caso.
export function DarEntrada() {
  const navigate = useNavigate()
  const [primeiroNome, setPrimeiroNome] = useState('')
  const [idade, setIdade] = useState('')
  const [gestante, setGestante] = useState(false)
  const [semanas, setSemanas] = useState('')
  const [erro, setErro] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  async function salvar(e: React.FormEvent) {
    e.preventDefault()
    setErro(null)
    if (!primeiroNome.trim()) {
      setErro('Informe o primeiro nome.')
      return
    }
    setEnviando(true)
    try {
      const paciente = await api.criarPaciente({
        primeiro_nome: primeiroNome.trim(),
        idade: idade ? Number(idade) : null,
        gestante,
        idade_gestacional_semanas: gestante && semanas ? Number(semanas) : null,
      })
      navigate(`/pacientes/${paciente.id}/enviar`)
    } catch {
      setErro('Não foi possível cadastrar a paciente.')
      setEnviando(false)
    }
  }

  return (
    <section>
      <h2>Dar entrada de paciente</h2>
      <form className="form" onSubmit={salvar}>
        <div className="campo">
          <label htmlFor="nome">Primeiro nome</label>
          <input
            id="nome"
            value={primeiroNome}
            onChange={(e) => setPrimeiroNome(e.target.value)}
            autoFocus
          />
        </div>

        <div className="campo">
          <label htmlFor="idade">Idade</label>
          <input
            id="idade"
            type="number"
            min={0}
            max={120}
            value={idade}
            onChange={(e) => setIdade(e.target.value)}
          />
        </div>

        <div className="campo checkbox">
          <input
            id="gestante"
            type="checkbox"
            checked={gestante}
            onChange={(e) => setGestante(e.target.checked)}
          />
          <label htmlFor="gestante">Gestante</label>
        </div>

        {gestante && (
          <div className="campo">
            <label htmlFor="semanas">Idade gestacional (semanas)</label>
            <input
              id="semanas"
              type="number"
              min={0}
              max={45}
              value={semanas}
              onChange={(e) => setSemanas(e.target.value)}
            />
          </div>
        )}

        {erro && <p className="aviso">{erro}</p>}

        <div className="acoes">
          <button className="primario" type="submit" disabled={enviando}>
            {enviando ? 'Salvando…' : 'Salvar e enviar dados'}
          </button>
          <button type="button" onClick={() => navigate('/pacientes')}>
            Cancelar
          </button>
        </div>
      </form>
    </section>
  )
}
