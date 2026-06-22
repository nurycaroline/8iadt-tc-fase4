// Conexão única de socket.io com o backend (alerta em tempo real — docs/frontend.md §5).
import { io, type Socket } from 'socket.io-client'

let socket: Socket | null = null

export function getSocket(): Socket {
  if (!socket) {
    // Caminho relativo: o proxy do Vite (dev) ou o próprio backend (prod) resolve o host.
    socket = io({ autoConnect: true, transports: ['websocket', 'polling'] })
  }
  return socket
}
