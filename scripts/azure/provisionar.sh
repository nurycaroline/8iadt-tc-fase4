#!/usr/bin/env bash
# Provisiona os recursos Azure da Fase 3 (Storage Account + container) via Azure CLI.
# Pré-requisito: `az login`. Idempotente o suficiente para a demo. Ver docs/deploy-azure.md.
#
# Uso:
#   RESOURCE_GROUP=rg-saude-mulher LOCATION=brazilsouth \
#   STORAGE_ACCOUNT=stsaudemulher CONTAINER=monitoramento \
#   bash scripts/azure/provisionar.sh
set -euo pipefail

RESOURCE_GROUP="${RESOURCE_GROUP:-rg-saude-mulher}"
LOCATION="${LOCATION:-brazilsouth}"
STORAGE_ACCOUNT="${STORAGE_ACCOUNT:-stsaudemulher}"
CONTAINER="${CONTAINER:-monitoramento}"

echo "==> Resource group: ${RESOURCE_GROUP} (${LOCATION})"
az group create --name "${RESOURCE_GROUP}" --location "${LOCATION}" --output none

echo "==> Storage account: ${STORAGE_ACCOUNT}"
az storage account create \
  --name "${STORAGE_ACCOUNT}" \
  --resource-group "${RESOURCE_GROUP}" \
  --sku Standard_LRS \
  --kind StorageV2 \
  --min-tls-version TLS1_2 \
  --output none

echo "==> Container: ${CONTAINER}"
az storage container create \
  --name "${CONTAINER}" \
  --account-name "${STORAGE_ACCOUNT}" \
  --output none

echo "==> Connection string (defina como AZURE_STORAGE_CONNECTION_STRING — trate como segredo):"
az storage account show-connection-string \
  --name "${STORAGE_ACCOUNT}" \
  --resource-group "${RESOURCE_GROUP}" \
  --query connectionString -o tsv

echo "==> Pronto. Configure STORAGE_BACKEND=azure e AZURE_STORAGE_CONTAINER=${CONTAINER} no .env."
