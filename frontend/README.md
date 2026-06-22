# Dashboard — Saúde da Mulher (Fase 5)

Painel de monitoramento clínico (React + Vite + TypeScript) que consome o backend Node por
**REST + WebSocket** e exibe a análise multimodal com **alerta em tempo real**. Substitui o
cliente mínimo da Fase 3. Especificação visual em [`docs/frontend.md`](../docs/frontend.md).

## Telas

- **Dashboard** (`/dashboard`) — visão geral: contadores por risco + cartões de casos + banner de alerta em tempo real.
- **Pacientes** (`/pacientes`) — lista, dar entrada e excluir.
- **Dar entrada** (`/pacientes/nova`) — cadastro curto da paciente.
- **Enviar caso** (`/pacientes/:id/enviar`) — upload das modalidades (vídeo, áudio, CSV, texto) → análise.
- **Detalhe do caso** (`/casos/:id`) — painéis por modalidade + painel de fusão + relatório.
- **Histórico** (`/historico`) — casos passados com filtro por risco.

## Stack

React 19, Vite, TypeScript, React Router, **@tanstack/react-query** (REST), **socket.io-client**
(tempo real). Testes com **Vitest + Testing Library**.

## Rodar em desenvolvimento

O backend precisa estar no ar (porta 3000). O Vite faz proxy de `/pacientes`, `/casos`,
`/analisar`, `/socket.io` etc. para o backend (sem CORS).

```bash
npm install
npm run dev        # http://localhost:5173 (proxy → http://localhost:3000)
```

Para apontar a outro backend: `BACKEND_URL=http://host:porta npm run dev`.

## Build de produção

```bash
npm run build      # gera frontend/dist
```

O backend serve `frontend/dist` automaticamente quando existe (SPA), então em produção o
dashboard fica disponível na mesma origem do backend.

## Qualidade

```bash
npm run lint       # eslint
npm test           # vitest (run)
```
