# Dashboard (React + Vite) — build estático servido por nginx, com proxy para o backend (Fase 5).
FROM node:22-bookworm-slim AS build
WORKDIR /app/frontend
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/frontend/dist /usr/share/nginx/html
EXPOSE 80
