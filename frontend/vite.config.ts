/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// O dashboard fala com o backend Node por REST + WebSocket. Em dev, o proxy do Vite
// encaminha as rotas da API e do socket.io para o backend (evita CORS).
const BACKEND = process.env.BACKEND_URL || 'http://localhost:3000'

// Porta do dev server do frontend. Fixa em 5173 (convenção do projeto) para nunca
// colidir com o backend (:3000). `strictPort` faz o Vite falhar de forma explícita
// se a porta estiver ocupada, em vez de migrar silenciosamente para outra.
const FRONTEND_PORT = Number(process.env.FRONTEND_PORT || 5173)

export default defineConfig({
  plugins: [react()],
  server: {
    port: FRONTEND_PORT,
    strictPort: true,
    proxy: {
      '/pacientes': BACKEND,
      '/casos': BACKEND,
      '/analisar': BACKEND,
      '/health': BACKEND,
      '/ready': BACKEND,
      '/socket.io': { target: BACKEND, ws: true },
    },
  },
  preview: {
    port: FRONTEND_PORT,
    strictPort: true,
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
    css: true,
  },
})
