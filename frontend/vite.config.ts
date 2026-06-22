/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// O dashboard fala com o backend Node por REST + WebSocket. Em dev, o proxy do Vite
// encaminha as rotas da API e do socket.io para o backend (evita CORS).
const BACKEND = process.env.BACKEND_URL || 'http://localhost:3000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/pacientes': BACKEND,
      '/casos': BACKEND,
      '/analisar': BACKEND,
      '/health': BACKEND,
      '/ready': BACKEND,
      '/socket.io': { target: BACKEND, ws: true },
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
    css: true,
  },
})
