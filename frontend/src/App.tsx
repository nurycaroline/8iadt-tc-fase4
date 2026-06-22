import { useState } from 'react'
import { NavLink, Route, Routes } from 'react-router-dom'

import { AlertaBanner } from './components/AlertaBanner'
import { useAlertas } from './hooks/useAlertas'
import { Dashboard } from './pages/Dashboard'
import { DarEntrada } from './pages/DarEntrada'
import { DetalheCaso } from './pages/DetalheCaso'
import { EnviarCaso } from './pages/EnviarCaso'
import { Historico } from './pages/Historico'
import { Pacientes } from './pages/Pacientes'

export default function App() {
  const { conectado, ultimo } = useAlertas()
  // Visibilidade derivada: o banner some quando o caso atual é dispensado e reaparece
  // sozinho ao chegar um alerta de caso diferente (sem setState em efeito).
  const [dispensado, setDispensado] = useState<string | null>(null)
  const alertaVisivel = ultimo != null && ultimo.case_id !== dispensado

  return (
    <div className="app">
      <header className="topbar">
        <h1>Saúde da Mulher</h1>
        <nav>
          <NavLink to="/dashboard" className={({ isActive }) => (isActive ? 'ativo' : '')}>
            Dashboard
          </NavLink>
          <NavLink to="/pacientes" className={({ isActive }) => (isActive ? 'ativo' : '')}>
            Pacientes
          </NavLink>
          <NavLink to="/historico" className={({ isActive }) => (isActive ? 'ativo' : '')}>
            Histórico
          </NavLink>
        </nav>
        <span className={`conexao ${conectado ? 'online' : 'offline'}`}>
          {conectado ? 'tempo real conectado' : 'sem conexão em tempo real'}
        </span>
      </header>

      <main>
        {ultimo && alertaVisivel && (
          <AlertaBanner alerta={ultimo} onFechar={() => setDispensado(ultimo.case_id)} />
        )}

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/pacientes" element={<Pacientes />} />
          <Route path="/pacientes/nova" element={<DarEntrada />} />
          <Route path="/pacientes/:id/enviar" element={<EnviarCaso />} />
          <Route path="/casos/:id" element={<DetalheCaso />} />
          <Route path="/historico" element={<Historico />} />
        </Routes>
      </main>

      <footer className="disclaimer">
        Ferramenta de <strong>apoio à decisão clínica</strong> — não substitui avaliação profissional
        nem constitui diagnóstico. Dados sintéticos/pseudonimizados (LGPD).
      </footer>
    </div>
  )
}
