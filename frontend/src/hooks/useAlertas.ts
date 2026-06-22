// Escuta o evento 'alerta' do backend e mantém o último alerta + status da conexão.
import { useEffect, useState } from 'react'

import { getSocket } from '../socket'
import type { Alerta } from '../types'

export interface EstadoAlertas {
  conectado: boolean
  ultimo: Alerta | null
  historico: Alerta[]
}

export function useAlertas(): EstadoAlertas {
  const [conectado, setConectado] = useState(() => getSocket().connected)
  const [ultimo, setUltimo] = useState<Alerta | null>(null)
  const [historico, setHistorico] = useState<Alerta[]>([])

  useEffect(() => {
    const socket = getSocket()
    const onConnect = () => setConectado(true)
    const onDisconnect = () => setConectado(false)
    const onAlerta = (a: Alerta) => {
      setUltimo(a)
      setHistorico((prev) => [a, ...prev].slice(0, 50))
    }

    socket.on('connect', onConnect)
    socket.on('disconnect', onDisconnect)
    socket.on('alerta', onAlerta)

    return () => {
      socket.off('connect', onConnect)
      socket.off('disconnect', onDisconnect)
      socket.off('alerta', onAlerta)
    }
  }, [])

  return { conectado, ultimo, historico }
}
