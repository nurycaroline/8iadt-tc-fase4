# Backend orquestrador (Node.js + Express) — Fase 3.
FROM node:22-bookworm-slim

ENV NODE_ENV=production

# Ferramentas para compilar better-sqlite3 quando não houver binário pré-compilado.
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 make g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

COPY package*.json ./
RUN npm ci --omit=dev

COPY . .

EXPOSE 3000
# Entrypoint que pré-carrega segredos do Key Vault (Fase 7 — F7-07) e sobe o servidor.
CMD ["node", "src/bootstrap.js"]
