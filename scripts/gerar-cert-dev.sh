#!/usr/bin/env bash
# Gera um certificado TLS autoassinado para desenvolvimento (Fase 7 — F7-02).
# Os certificados ficam em ./certs (ignorado pelo Git) e são montados pelo docker-compose.tls.yml.
# NÃO use certificado autoassinado em produção — use o certificado gerenciado da nuvem/ingress.
set -euo pipefail

DEST="${1:-certs}"
mkdir -p "$DEST"

if [[ -f "$DEST/server.crt" && -f "$DEST/server.key" ]]; then
  echo "Certificado já existe em $DEST/ (server.crt/server.key). Nada a fazer."
  exit 0
fi

openssl req -x509 -nodes -newkey rsa:2048 \
  -keyout "$DEST/server.key" \
  -out "$DEST/server.crt" \
  -days 365 \
  -subj "/C=BR/ST=Dev/L=Dev/O=SaudeMulher/CN=localhost"

echo "Certificado autoassinado gerado em $DEST/ (válido por 365 dias)."
echo "Suba a stack com TLS: docker compose -f docker-compose.yml -f docker-compose.tls.yml up"
