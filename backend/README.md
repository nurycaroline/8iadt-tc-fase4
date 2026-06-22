# backend — Orquestrador (Node.js + Express) — Fase 3

Backend que **orquestra o fluxo** do monitoramento: recebe o upload de um caso, sobe os arquivos ao
**storage** (Azure Blob ou local), chama o **serviço de IA** (FastAPI) pelo
[contrato de API §1](../docs/contrato-api.md), **persiste o Caso** (SQLite) e **empurra o alerta em
tempo real** (socket.io) quando o risco é `MEDIO`/`ALTO`. Também gerencia pacientes (CRUD).

> Planejamento: [`.specs/features/fase3-fusao-e-nuvem/`](../.specs/features/fase3-fusao-e-nuvem/).
> Motor de IA (Python/FastAPI): [`../ai-service`](../ai-service). Contrato:
> [`../docs/contrato-api.md`](../docs/contrato-api.md).

## Requisitos

- Node.js **20+** (LTS; testado em 22).
- O serviço de IA rodando (local em `http://localhost:8000` ou via `docker compose`).

## Instalação e execução

```bash
cd backend
npm install
cp ../.env.example ../.env   # ajuste as variáveis (ver abaixo)
npm start                    # sobe o Express + socket.io na porta de PORT (3000)
```

Abra `http://localhost:3000/` para o **cliente mínimo de demonstração** do alerta em tempo real.

### Variáveis de ambiente (ver [`.env.example`](../.env.example))

`PORT`, `AI_SERVICE_URL`, `AI_TIMEOUT_MS`, `DB_PATH`, `STORAGE_BACKEND` (`local`|`azure`),
`STORAGE_DIR`, `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_STORAGE_CONTAINER`, `AZURE_SAS_EXPIRY_MINUTES`,
`LOG_LEVEL`. Segredos **nunca** vão para o Git (ver [docs/07](../docs/07-privacidade-e-seguranca.md)).

## Endpoints

| Método | Rota | Descrição |
| ------ | ---- | --------- |
| `GET`  | `/health` | readiness (`{status:"ok"}`) |
| `POST` | `/pacientes` | cria paciente (validação `zod`) |
| `GET`  | `/pacientes` | lista pacientes |
| `DELETE` | `/pacientes/:id` | exclui paciente (cascata no Caso + artefatos) |
| `POST` | `/analisar` | upload → storage → IA → banco → alerta; devolve o JSON de risco |
| WebSocket | evento `alerta` | empurrado quando o risco é `MEDIO`/`ALTO` |

### `POST /analisar` (multipart)

Campos: `paciente_id` (obrigatório), `case_id` (opcional), `texto_clinico` (texto) e arquivos
`video_cicatriz`, `video_fisioterapia`, `audio`, `sinais_vitais` (CSV). O backend monta o payload do
contrato §1, chama `POST {AI_SERVICE_URL}/inferencia` (`axios`) e persiste o resultado. Se o serviço de
IA estiver indisponível, responde `502/504` (com `case_id` logado) sem perder o upload já armazenado.

## Estrutura

```
backend/
├── src/
│   ├── server.js          # http + socket.io + bootstrap
│   ├── app.js             # fábrica do Express (injeção de deps p/ testes)
│   ├── config.js          # variáveis de ambiente (dotenv)
│   ├── logger.js          # pino (JSON) com case_id (observabilidade)
│   ├── db/                # better-sqlite3 + repositórios (pacientes/casos)
│   ├── rotas/             # pacientes.js, analisar.js
│   ├── servicos/          # inferencia.js (axios → FastAPI)
│   ├── storage/           # index.js (seletor), local.js, azureBlob.js
│   └── realtime/          # alertas.js (emite o evento 'alerta')
├── public/index.html      # cliente mínimo (socket.io-client + banner de risco)
└── tests/                 # jest + supertest (Python mockado)
```

## Testes e lint (gate)

```bash
npm run lint   # eslint
npm test       # jest + supertest (rotas com o serviço de IA mockado)
```

Os testes cobrem o CRUD de pacientes, o fluxo do `POST /analisar` (sucesso, IA indisponível, paciente
inexistente) e a emissão do alerta em tempo real (socket.io). IO de rede/Blob é validado por E2E/smoke.

## Observabilidade

Logs estruturados (JSON) via `pino`, com `case_id` para rastrear um caso ponta-a-ponta — a mesma
convenção do `ai-service` (Python), atendendo [docs/qualidade-testes-ci §4](../docs/qualidade-testes-ci.md).
