# Como Executar o Projeto

> Guia prático para subir a solução **IA Multimodal para Saúde da Mulher** (Fases 1–7): serviço de IA
> (Python/FastAPI), orquestrador (Node/Express) e dashboard (React/Vite). Cobre execução com Docker, em
> modo local, geração de dados, testes e os controles de privacidade/segurança (LGPD) da Fase 7.

> ⚠️ **Solução acadêmica** de apoio à decisão clínica, com **dados sintéticos**. Não use dados reais de
> pacientes — ver [privacidade e segurança](07-privacidade-e-seguranca.md).

## Sumário

- [1. Pré-requisitos](#1-pré-requisitos)
- [2. Arquitetura e portas](#2-arquitetura-e-portas)
- [3. Configuração (`.env`)](#3-configuração-env)
- [4. Opção A — Docker (recomendado)](#4-opção-a--docker-recomendado)
- [5. Opção B — Execução local (sem Docker)](#5-opção-b--execução-local-sem-docker)
- [6. Dados de teste (mini-dataset e casos sintéticos)](#6-dados-de-teste-mini-dataset-e-casos-sintéticos)
- [7. Primeiro fluxo ponta-a-ponta](#7-primeiro-fluxo-ponta-a-ponta)
- [8. Demo em processo (sem subir a stack)](#8-demo-em-processo-sem-subir-a-stack)
- [9. Testes e qualidade](#9-testes-e-qualidade)
- [10. Privacidade e segurança (Fase 7 — LGPD)](#10-privacidade-e-segurança-fase-7--lgpd)
- [11. Nuvem (Azure) e fallback local](#11-nuvem-azure-e-fallback-local)
- [12. Solução de problemas](#12-solução-de-problemas)

---

## 1. Pré-requisitos

| Ferramenta | Versão | Para quê |
|------------|--------|----------|
| **Docker + Docker Compose** | atual | subir toda a stack com um comando (Opção A) |
| **Python** | 3.12+ | serviço de IA, scripts de dados e demo (Opção B) |
| **Node.js** | 20+ | backend e frontend (Opção B) |
| **Git** | atual | clonar o repositório |

> A **Opção A (Docker)** dispensa instalar Python/Node localmente. A **Opção B** é útil para desenvolvimento
> com hot-reload.

## 2. Arquitetura e portas

```
┌──────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Dashboard   │ ───► │  Backend (Node)  │ ───► │ ai-service (Py) │
│ React/Vite   │ HTTP │  Express + WS    │ HTTP │ FastAPI         │
└──────────────┘ ◄─── └──────────────────┘      └─────────────────┘
   alerta WS            SQLite + storage           fusão + relatório
```

| Serviço | Porta (Docker) | Porta (local) | URL |
|---------|----------------|---------------|-----|
| Dashboard (nginx) | `8080` | `5173` (Vite) | http://localhost:8080 / http://localhost:5173 |
| Backend (Express) | `3000` | `3000` | http://localhost:3000 |
| ai-service (FastAPI) | `8000` | `8000` | http://localhost:8000 |
| Dashboard via TLS (Fase 7) | `8443` | — | https://localhost:8443 |

O backend também serve um **cliente mínimo** de tempo real em `http://localhost:3000/` (fallback) e, em
produção, serve o build do dashboard (`frontend/dist`) quando presente.

## 3. Configuração (`.env`)

Na raiz do repositório:

```bash
cp .env.example .env
```

O padrão usa **storage local** e **auth desabilitada**, garantindo a demo sem credenciais. As variáveis
estão documentadas em [`.env.example`](../.env.example). Resumo das principais:

| Variável | Padrão | Função |
|----------|--------|--------|
| `PORT` | `3000` | porta do backend |
| `AI_SERVICE_URL` | `http://localhost:8000` | URL do serviço de IA (no Docker: `http://ai-service:8000`) |
| `STORAGE_BACKEND` | `local` | `local` (disco) ou `azure` (Blob) |
| `STORAGE_DIR` | `data/_storage` | raiz do storage local |
| `DB_PATH` | `data/_storage/app.sqlite` | banco SQLite |
| `API_KEY` | _(vazio)_ | exige `x-api-key` nas rotas de dados quando definido (F7-01) |
| `AI_SERVICE_API_KEY` | _(vazio)_ | credencial backend→ai-service (F7-01) |
| `RETENTION_DAYS` | `0` | TTL de retenção; `0` desabilita (F7-04) |
| `AZURE_*` | _(vazio)_ | nuvem Azure (opcional) |

## 4. Opção A — Docker (recomendado)

Sobe **ai-service (8000)**, **backend (3000)** e **dashboard (8080)** de uma vez:

```bash
cp .env.example .env          # ajuste se for usar Azure; o padrão é storage local
docker compose up --build
```

- Dashboard: **http://localhost:8080/**
- Cliente mínimo de tempo real (fallback): http://localhost:3000/
- O backend só inicia após o `ai-service` passar no healthcheck; ambos compartilham `./data` por volume.

Para parar: `Ctrl+C` e, se quiser remover os contêineres, `docker compose down`.

### Com TLS (Fase 7)

```bash
./scripts/gerar-cert-dev.sh                                   # gera certs autoassinados em ./certs
docker compose -f docker-compose.yml -f docker-compose.tls.yml up --build
```

- Dashboard por HTTPS: **https://localhost:8443/** (aceite o certificado autoassinado de dev).

## 5. Opção B — Execução local (sem Docker)

Use **três terminais**. Em produção, troque `npm run dev` do frontend pelo build servido pelo backend.

> ⚠️ **Execute todos os comandos a partir da raiz do repositório** (a pasta que contém
> `ai-service/`, `backend/` e `frontend/`). Os caminhos abaixo são relativos a ela. Se o `pip install`
> falhar com `Could not open requirements file: ... 'ai-service/requirements.txt'`, você não está na
> raiz — rode `cd /caminho/para/o/repositorio` antes de continuar.

### Terminal 1 — serviço de IA (Python 3.12+)

> ⚠️ **Use Python 3.12+.** Em muitos sistemas (especialmente macOS) `python`/`python3` apontam para uma
> versão antiga (3.9, p. ex.), e o `pip install` falha com mensagens como
> `Could not find a version that satisfies the requirement onnxruntime>=1.20` /
> `Ignored the following versions that require a different python version`. Crie o venv com o interpretador
> 3.12 explícito e confirme a versão antes de instalar.

```bash
# a partir da raiz do repositório
python3.12 -m venv .venv && source .venv/bin/activate
python --version                              # confirme: Python 3.12.x
pip install -r ai-service/requirements.txt
cd ai-service && uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

> Sem o Python 3.12? Instale-o (macOS: `brew install python@3.12`; Ubuntu/Debian:
> `sudo apt install python3.12 python3.12-venv`) ou use a **Opção A (Docker)**, que não exige Python local.

### Terminal 2 — backend (Node 20+)

```bash
cd backend && npm install && npm start     # http://localhost:3000
```

### Terminal 3 — dashboard (React)

```bash
cd frontend && npm install && npm run dev   # http://localhost:5173 (proxy automático p/ o backend)
```

> Se o backend não estiver na porta padrão, aponte o proxy do Vite com
> `BACKEND_URL=http://host:porta npm run dev`.

## 6. Dados de teste (mini-dataset e casos sintéticos)

Os três casos de demonstração já estão versionados em `data/casos/` (`caso_baixo.json`,
`caso_medio.json`, `caso_alto.json`). Artefatos pesados (imagens/áudio/vídeo) **não** ficam no Git — gere
o mini-dataset localmente:

```bash
pip install -r scripts/requirements-data.txt
python -m scripts.data_prep        # baixa/gera vitais, cicatriz (YOLO) e texto
```

> Áudio e fisioterapia exigem amostras manuais em `data/audio/` e `data/video_fisioterapia/`. Sem elas, a
> modalidade **degrada graciosamente** (é omitida), o que é esperado.

## 7. Primeiro fluxo ponta-a-ponta

Com a stack no ar (Opção A ou B):

1. Abra o dashboard (`:8080` no Docker ou `:5173` em dev).
2. **Pacientes → Dar entrada:** cadastre uma paciente.
3. **Enviar caso:** anexe ao menos um texto clínico (ex.: "febre e dor na cicatriz") e, opcionalmente,
   arquivos de mídia/CSV.
4. Veja o **detalhe do caso** com os painéis por modalidade + o painel de **fusão** (risco e mensagem).
5. Deixe o dashboard aberto e envie um caso de risco `MÉDIO`/`ALTO`: um **banner de alerta em tempo real**
   aparece.
6. Abra o **relatório automático** pelo botão no detalhe do caso.

Equivalente por API (sem UI):

```bash
# health
curl http://localhost:3000/health
curl http://localhost:8000/health

# inferência direta no ai-service (contrato §1 → §2)
curl -X POST http://localhost:8000/inferencia \
  -H 'content-type: application/json' \
  -d '{"case_id":"demo-1","paciente":{"id":"p1"},"texto_clinico":"febre e dor na cicatriz"}'
```

## 8. Demo em processo (sem subir a stack)

Valida upload local → inferência → JSON de risco → alerta (log), sem HTTP:

```bash
python -m scripts.e2e_demo                  # caso_alto (padrão)
python -m scripts.e2e_demo --caso caso_medio
python -m scripts.e2e_demo --caso caso_baixo
```

## 9. Testes e qualidade

| Camada | Comando | Onde |
|--------|---------|------|
| Lint Python | `ruff check scripts ai-service` | raiz |
| Testes Python | `pytest -q` | raiz |
| Lint + testes backend | `npm run lint && npm test` | `backend/` |
| Lint + testes + build frontend | `npm run lint && npm test && npm run build` | `frontend/` |
| Conformidade LGPD (CI) | `python -m scripts.check_conformidade` | raiz |

Para a validação manual completa de todas as fases, siga o
[plano de teste manual](plano-de-teste-manual.md).

## 10. Privacidade e segurança (Fase 7 — LGPD)

Os controles são **opt-in por variável de ambiente**, preservando a demo local. Detalhes em
[`07-privacidade-e-seguranca.md`](07-privacidade-e-seguranca.md) e na traçabilidade da
[Fase 7](10-fase7-privacidade-e-seguranca.md).

- **Autenticação (F7-01):** defina `API_KEY` (header `x-api-key` nas rotas de dados) e
  `AI_SERVICE_API_KEY` (backend→ai-service). `/health` e `/ready` seguem públicos.
- **TLS (F7-02):** `./scripts/gerar-cert-dev.sh` + `docker compose -f docker-compose.yml -f docker-compose.tls.yml up`.
- **Auditoria (F7-03):** acessos ficam na tabela `auditoria`; informe a identidade via header `x-user-id`.
- **Retenção (F7-04):** defina `RETENTION_DAYS` e rode `npm run retencao` em `backend/`.
- **Segredos (F7-07):** defina `AZURE_KEY_VAULT_URL` para carregar do Key Vault (fallback `.env`).

## 11. Nuvem (Azure) e fallback local

Por padrão (`STORAGE_BACKEND=local`), tudo roda sem nuvem. Para usar o Azure Blob Storage:

1. Provisione os recursos (opcional): `bash scripts/azure/provisionar.sh`.
2. No `.env`, defina `STORAGE_BACKEND=azure` e `AZURE_STORAGE_CONNECTION_STRING` (+ container).
3. As URLs de leitura usam **SAS token** com expiração (`AZURE_SAS_EXPIRY_MINUTES`).

Passo a passo completo em [`deploy-azure.md`](deploy-azure.md).

## 12. Solução de problemas

| Sintoma | Causa provável | Ação |
|---------|----------------|------|
| Backend responde `502`/`504` em `/analisar` | `ai-service` indisponível/lento | confirme o `ai-service` (`curl :8000/health`); ajuste `AI_TIMEOUT_MS` |
| `401` nas rotas de dados | `API_KEY` definido | envie o header `x-api-key`; ou remova `API_KEY` para a demo |
| `503` em `/ready` ou nas rotas | dependência indisponível ou `AUTH_REQUIRED=true` sem `API_KEY` | verifique storage/DB; configure `API_KEY` |
| Áudio/fisioterapia `nao_avaliado` | sem amostras manuais | esperado (degradação graciosa) — adicione amostras em `data/` |
| Dashboard sem "tempo real conectado" | backend fora do ar ou proxy errado | confirme o backend `:3000` e o proxy do Vite |
| `relatorio_url` nulo | libs de PDF ausentes | esperado em ambiente sem PDF — cai em HTML; no Docker o PDF é garantido |
| Portas ocupadas (`8080`/`3000`/`8000`) | outro processo usando a porta | libere a porta ou ajuste o mapeamento no `docker-compose.yml`/`PORT` |
| `pip install` falha com `Could not open requirements file: ... 'ai-service/requirements.txt'` | comando rodado fora da raiz do repositório | `cd` para a raiz (pasta com `ai-service/`, `backend/`, `frontend/`) e rode novamente |
| `pip install` falha com `Could not find a version that satisfies onnxruntime>=1.20` / `Ignored the following versions that require a different python version` | venv criado com Python < 3.12 (ex.: 3.9 no macOS) | recrie o venv com 3.12: `rm -rf .venv && python3.12 -m venv .venv && source .venv/bin/activate` e confira com `python --version` |

---

> Dúvidas de arquitetura e contrato: [`arquitetura.md`](arquitetura.md) e [`contrato-api.md`](contrato-api.md).
> Para validar a entrega de ponta a ponta, use o [plano de teste manual](plano-de-teste-manual.md).
