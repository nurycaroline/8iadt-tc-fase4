# Deploy na Azure (Blob + serviço de IA) — Fase 3

> Como publicar a stack da Fase 3 na **Azure** (Blob Storage para artefatos + hospedagem do serviço
> Python) mantendo um **fallback local** funcional para a demonstração. Alinha-se a
> [docs/03 §3.4](03-fase3-fusao-e-nuvem.md), [arquitetura](arquitetura.md) e
> [privacidade/LGPD](07-privacidade-e-seguranca.md).

> ⚠️ **Fallback local sempre disponível:** se a conta Azure estiver indisponível ou com limite, rode a
> stack com `docker compose up` e `STORAGE_BACKEND=local` — o pipeline funciona ponta-a-ponta sem a
> nuvem (ver [README](../README.md)). O deploy real na Azure **não bloqueia** o gate da fase.

## 1. Pré-requisitos

- Conta Microsoft Azure (o tier gratuito atende à demo).
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) (`az`) autenticada: `az login`.
- Imagens da stack (`ai-service/Dockerfile`, `backend/Dockerfile`) — ver `docker-compose.yml`.

## 2. Variáveis de ambiente

Todas as variáveis estão em [`.env.example`](../.env.example). As sensíveis (connection string) vêm de
**Azure Key Vault** ou do `.env` — **nunca** do Git.

| Variável | Descrição |
| -------- | --------- |
| `STORAGE_BACKEND` | `azure` para usar o Blob; `local` para o fallback |
| `AZURE_STORAGE_CONNECTION_STRING` | connection string da Storage Account (segredo) |
| `AZURE_STORAGE_CONTAINER` | container dos artefatos (vídeos/áudios/relatórios) |
| `AZURE_SAS_EXPIRY_MINUTES` | expiração do SAS das URLs de leitura |
| `AI_SERVICE_URL` | URL pública/privada do serviço de IA usada pelo backend |

## 3. Criar Storage Account + container

```bash
az group create --name rg-saude-mulher --location brazilsouth

az storage account create \
  --name stsaudemulher \
  --resource-group rg-saude-mulher \
  --sku Standard_LRS \
  --kind StorageV2 \
  --min-tls-version TLS1_2

# Connection string (use como AZURE_STORAGE_CONNECTION_STRING — trate como segredo).
az storage account show-connection-string \
  --name stsaudemulher --resource-group rg-saude-mulher --query connectionString -o tsv

az storage container create --name monitoramento --account-name stsaudemulher
```

> O Blob já aplica **criptografia em repouso** (server-side). As URLs de leitura recebem **SAS com
> expiração** (gerado pelo adaptador de storage), atendendo aos controles de [docs/07](07-privacidade-e-seguranca.md).

## 4. Publicar o serviço de IA (Python/FastAPI)

Há três caminhos suportados pela arquitetura; escolha um.

### Opção A — Azure Container Instances (mais simples para a demo)

```bash
# 1) Container Registry e build da imagem do ai-service
az acr create --resource-group rg-saude-mulher --name acrsaudemulher --sku Basic
az acr login --name acrsaudemulher
az acr build --registry acrsaudemulher --image ai-service:latest ./ai-service

# 2) Container com as variáveis de ambiente
az container create \
  --resource-group rg-saude-mulher \
  --name ai-service \
  --image acrsaudemulher.azurecr.io/ai-service:latest \
  --ports 8000 \
  --environment-variables STORAGE_BACKEND=azure AZURE_STORAGE_CONTAINER=monitoramento \
  --secure-environment-variables AZURE_STORAGE_CONNECTION_STRING="<connection-string>" \
  --dns-name-label ai-service-saude
```

`AI_SERVICE_URL` do backend passa a ser `http://ai-service-saude.<regiao>.azurecontainer.io:8000`.

### Opção B — Azure App Service (Web App for Containers)

```bash
az appservice plan create --name plan-ai --resource-group rg-saude-mulher --is-linux --sku B1
az webapp create --resource-group rg-saude-mulher --plan plan-ai --name ai-service-saude \
  --deployment-container-image-name acrsaudemulher.azurecr.io/ai-service:latest
az webapp config appsettings set --resource-group rg-saude-mulher --name ai-service-saude \
  --settings STORAGE_BACKEND=azure AZURE_STORAGE_CONTAINER=monitoramento \
  AZURE_STORAGE_CONNECTION_STRING="<connection-string>" WEBSITES_PORT=8000
```

### Opção C — Azure Functions

Empacote `POST /inferencia` como uma function HTTP (custom handler/ASGI). Recomendado apenas se já houver
familiaridade com Functions; para a demo, A ou B são mais diretos.

## 5. Backend Node (orquestrador)

Pode rodar do mesmo modo (ACI/App Service) apontando `AI_SERVICE_URL` para o serviço de IA e
`STORAGE_BACKEND=azure`. Em demos locais, rode o backend com `docker compose` e aponte apenas o storage
para a Azure (híbrido), mantendo o WebSocket/alerta local.

## 6. Segurança (LGPD)

- Segredos via **Key Vault** ou `.env` (nunca no Git) — ver [docs/07](07-privacidade-e-seguranca.md).
- **TLS** em todas as chamadas (Node ↔ Python ↔ Azure).
- **SAS com expiração** nas URLs de leitura; **RBAC** na Storage Account.
- Apenas **dados sintéticos/abertos** — nenhum dado real de paciente.

## 7. Smoke pós-deploy

```bash
curl https://<host-ai-service>/health           # -> {"status":"ok"}
# Envie um caso pelo backend (POST /analisar) e confirme o alerta no cliente mínimo (/).
```

Se algo falhar na nuvem, volte ao **fallback local** (`STORAGE_BACKEND=local` + `docker compose up`)
para não travar a gravação da demonstração.
