# Fase 3 — Fusão Multimodal e Integração em Nuvem — Design

> Como vamos construir o que o [`spec.md`](spec.md) descreve. Alinha-se à
> [arquitetura](../../../docs/arquitetura.md) (Node orquestrador + Python/FastAPI + Azure), ao
> [contrato de API](../../../docs/contrato-api.md), ao template de
> [relatórios](../../../docs/06-relatorios-automaticos.md) e às práticas de
> [qualidade/CI](../../../docs/qualidade-testes-ci.md). **Reusa** o serviço de IA da
> [Fase 2](../fase2-modelos/) sem reescrever modelos.

## 1. Visão geral

A Fase 3 acrescenta **três camadas** sobre os modelos da Fase 2:

1. **Inteligência de fusão (Python, em `ai-service/app/`)** — funções puras que cruzam as evidências e
   produzem o JSON de risco + relatório, mais a métrica do ganho da fusão. **É o núcleo de valor.**
2. **Serviço de IA (FastAPI)** — expõe a fusão por HTTP (`POST /inferencia`).
3. **Orquestrador (Node.js/Express, em `backend/`)** — upload, armazenamento (Azure Blob/local),
   chamada ao Python, persistência e **alerta em tempo real**.

```
                       ┌──────────────────────── backend/ (Node + Express) ───────────────────────┐
  Front-end / cliente  │  POST /pacientes·GET·DELETE   POST /analisar   WebSocket (socket.io)      │
  (cliente mínimo)  ──►│        (CRUD pacientes)            │  ▲                 ▲ alerta MEDIO/ALTO │
                       │                                    │  │                 │                   │
                       │            ┌──── storage (Azure Blob | local) ────┐     │                   │
                       │            ▼                                       │     │                   │
                       │   sobe arquivos do caso          grava Caso (SQLite/repo)                   │
                       └────────────│───────────────────────────────────────────────────────────────┘
                                    │ axios  POST /inferencia  (contrato §1)
                                    ▼
        ┌──────────────────────── ai-service/ (Python + FastAPI) ───────────────────────┐
        │  app/api  ──►  app/pipeline  ──►  inferências da Fase 2 (cicatriz, vitais,     │
        │                     │             áudio, texto, fisioterapia)                  │
        │                     ▼                                                          │
        │              app/fusao.avaliar_fusao  ──►  app/relatorio.gerar_relatorio       │
        │                     │                              │                           │
        │                     ▼                              ▼                           │
        │          JSON de risco (contrato §2)      Markdown→HTML/PDF (storage)          │
        │  app/metricas_fusao  (offline: fusão × modalidade única → metricas_fusao.json) │
        └────────────────────────────────────────────────────────────────────────────────┘
```

**Princípio guia (do PDF e de [docs/00](../../../docs/00-visao-geral-e-escopo.md) D5):** a fusão é um
**motor de regras explícito** (não end-to-end). A IA das modalidades produz evidências; a **regra de
negócio** decide e explica o alerta. Tudo determinístico e testável.

## 2. Stack e dependências

Versões devem ser fixadas pela **última estável** no momento da implementação (princípio do `AGENTS.md`;
confirmar via `context7`/registries). Abaixo só o **conjunto de pacotes**, sem inventar números.

### 2.1 Python (acréscimos a `ai-service/requirements.txt`)

| Finalidade                         | Pacote/Ferramenta                 | Usado em                         |
| ---------------------------------- | --------------------------------- | -------------------------------- |
| API HTTP + ASGI                    | `fastapi`, `uvicorn[standard]`    | `app/api`                        |
| Validação de payload               | `pydantic` (v2, já vem com FastAPI) | schemas de request/response     |
| Cliente HTTP de teste              | `httpx` (TestClient)              | testes da API                    |
| Acesso ao Azure Blob               | `azure-storage-blob`              | `app/storage` (modo Azure)       |
| Markdown → HTML                    | `markdown`                        | `app/relatorio`                  |
| HTML → PDF (opcional, com fallback)| `weasyprint`                      | `app/relatorio` (degradável)     |

> `weasyprint` exige libs de sistema; o relatório **sempre** produz Markdown+HTML e só tenta PDF quando
> disponível (DD7). `azure-storage-blob` só é exigido no modo Azure; o **fallback local** não o importa.

### 2.2 Node.js (`backend/package.json`)

| Finalidade                | Pacote/Ferramenta              | Usado em                         |
| ------------------------- | ------------------------------ | -------------------------------- |
| Servidor HTTP             | `express`                      | rotas REST                       |
| Upload multipart          | `multer`                       | `POST /analisar`                 |
| Cliente HTTP p/ Python    | `axios`                        | chamada `POST /inferencia`       |
| Tempo real                | `socket.io`                    | alerta WebSocket (Tarefa 3.3b)   |
| Azure Blob                | `@azure/storage-blob`          | storage (modo Azure)             |
| Config/segredos           | `dotenv`                       | `.env` (sem segredos no Git)     |
| Persistência leve         | `better-sqlite3` (SQLite)      | repositório de Paciente/Caso     |
| Validação de entrada      | `zod`                          | validação dos corpos REST        |
| Logging estruturado       | `pino`                         | logs JSON com `case_id`          |
| Testes / Lint             | `jest` + `supertest` / `eslint`| rotas (Python mockado) / lint    |

> **Runtime Node:** versão **LTS ativa** (confirmar no momento da implementação). `package.json` com
> versões fixadas (Tarefa 4.1). TypeScript é opcional; o MVP pode ser JS moderno (ESM) para reduzir atrito.

## 3. Estrutura de pastas (a criar)

```
ai-service/
├── requirements.txt                 # + fastapi, uvicorn, httpx, azure-storage-blob, markdown, weasyprint
├── app/
│   ├── fusao.py                     # avaliar_fusao(evidencias) -> dict (F3F-01, F3F-02)
│   ├── pipeline.py                  # request(contrato §1) -> inferências -> fusão -> resposta §2 (F3F-03)
│   ├── relatorio.py                 # gerar_relatorio(json, paciente) -> md/html/pdf (F3F-09)
│   ├── storage.py                   # adaptador Blob | local (F3F-11)
│   ├── metricas_fusao.py            # fusão × modalidade única -> metricas_fusao.json (F3F-10)
│   └── api/
│       ├── __init__.py
│       ├── main.py                  # app FastAPI: POST /inferencia, GET /health (F3F-04)
│       └── modelos.py               # Pydantic: RequisicaoInferencia, RespostaRisco (contrato §1/§2)
├── models/
│   └── metricas_fusao.json          # artefato versionável (métricas da fusão)
└── tests/
    ├── test_fusao.py                # regras de fusão (núcleo — muitos casos)
    ├── test_pipeline.py             # montagem de evidências + degradação de modalidade
    ├── test_relatorio.py            # template do relatório (Markdown determinístico)
    ├── test_metricas_fusao.py       # comparação fusão × modalidade única
    └── test_api.py                  # TestClient: /inferencia (200/422) e /health

backend/                             # Node.js / Express (orquestrador)
├── package.json
├── .eslintrc.json
├── Dockerfile
├── src/
│   ├── server.js                    # bootstrap Express + socket.io + pino
│   ├── config.js                    # env (dotenv): PORTA, AI_SERVICE_URL, AZURE_*...
│   ├── storage/
│   │   ├── index.js                 # seletor: azure | local (mesma interface)
│   │   ├── azureBlob.js             # @azure/storage-blob
│   │   └── local.js                 # fallback em disco (uploads/)
│   ├── db/
│   │   ├── index.js                 # better-sqlite3 + migração simples
│   │   └── repositorios.js          # pacienteRepo, casoRepo (modelo de arquitetura §7)
│   ├── realtime/
│   │   └── alertas.js               # emitirAlerta(io, jsonRisco) p/ MEDIO/ALTO (F3F-08)
│   ├── rotas/
│   │   ├── pacientes.js             # POST /pacientes, GET /pacientes, DELETE /pacientes/:id (F3F-06)
│   │   └── analisar.js              # POST /analisar (upload→storage→python→db→alerta) (F3F-05)
│   └── servicos/
│       └── inferencia.js            # axios POST {AI_SERVICE_URL}/inferencia (contrato §1)
├── public/
│   └── index.html                   # cliente mínimo: conecta socket.io e mostra o alerta (F3F-16)
└── tests/
    ├── pacientes.test.js            # CRUD (supertest)
    └── analisar.test.js             # fluxo com axios/python mockado + evento de alerta

(raiz)
├── docker-compose.yml               # sobe ai-service + backend (F3F-12)
├── .env.example                     # variáveis (Azure, URLs, portas) — sem segredos (F3F-12)
├── .github/workflows/ci.yml         # ruff+pytest (Py) e eslint+jest (Node) (F3F-13)
└── scripts/
    └── e2e_demo.py (ou .sh)         # teste ponta-a-ponta com o caso de exemplo (F3F-14)
```

> Artefatos versionáveis: `metricas_fusao.json` (pequeno, vai para o relatório). Pesos, uploads, banco
> SQLite e `.env` **não** são versionados (ver `.gitignore`, DD9).

## 4. Componentes

### 4.1 `app/fusao.py` — motor de regras (F3F-01, F3F-02) ⭐

`avaliar_fusao(evidencias: dict) -> dict` recebe um dicionário com as evidências por modalidade (cada
uma no formato do contrato §3, montadas por `app/schemas.py` da Fase 2) e devolve:

```python
{
  "risco_detectado": "ALTO" | "MEDIO" | "BAIXO",
  "mensagem_alerta": "<texto explicável>",
  "gatilhos": ["infeccao_puerperal", "pre_eclampsia", ...],  # rastreabilidade p/ relatório
}
```

**Algoritmo (regras explícitas, ordem de prioridade):**

1. **Base (contrato §4)** — combina `cicatriz.evento` × `sinais_vitais.tipo`:
   - `sinal_infeccao` + (vitais de risco) → `ALTO`
   - `sinal_infeccao` + normal → `MEDIO`
   - ok/nenhum + (vitais de risco) → `MEDIO`
   - ok/nenhum + normal → `BAIXO`
   (vitais "de risco" = `tipo ∈ {risco_medio?, hipertensao, pre_eclampsia}` / `limiares.risco_alto_sinais_vitais`).
2. **Regras de elevação (contrato §4 + Tarefa 3.1)** — texto/áudio como **contexto**:
   - `cicatriz=sinal_infeccao` **E** (febre/dor em texto=`sinal_infeccao` **ou** áudio de fadiga/dor) →
     `ALTO` + gatilho `infeccao_puerperal`.
   - vitais de risco **E** texto=`complicacao` (cefaleia/proteinúria) → `ALTO` + gatilho `pre_eclampsia`.
   - `audio=violencia` (conf ≥ `CONFIANCA_MINIMA`) → `ALTO` + gatilho `violencia` (protocolo de proteção).
   - `audio ∈ {depressao_pos_parto, ansiedade}` (conf ≥ limiar) → ao menos `MEDIO` + gatilho
     `desconforto_psicologico`.
   - `fisioterapia.execucao=incorreta` + dor relatada → **contexto** adicional (não eleva sozinho).
3. **Contexto isolado** — se a **única** fonte de risco é texto/áudio fraco, o teto é `MEDIO`
   (contrato §4: texto/áudio são contexto adicional).
4. **Resolução** — o `risco_detectado` é o **maior** nível disparado; a `mensagem_alerta` concatena os
   gatilhos acionados (mensagens padronizadas por gatilho).

- Reusa `app/limiares.py` (`risco_alto_sinais_vitais`, `confianca_suficiente`, `CONFIANCA_MINIMA`).
- **Pura/determinística** → coberta por muitos testes unitários (prioridade de `qualidade-testes-ci`).

### 4.2 `app/pipeline.py` — orquestração da inferência (F3F-03)

`processar(requisicao: dict) -> dict`:
1. Para cada modalidade **presente** no payload (contrato §1), resolve a fonte via `app/storage.py`
   (URL Blob → arquivo local temporário ou caminho local direto) e chama a inferência da Fase 2:
   - `video_cicatriz_url` → `app.cicatriz.inferencia.detectar`
   - `video_fisioterapia_url` → `app.fisioterapia.inferencia.avaliar`
   - `dados_vitais.csv_url` → `app.sinais_vitais.inferencia.prever`
   - `audio_url` → `app.audio.classificacao.inferir`
   - `texto_clinico` → `app.texto.nlp.analisar`
2. Modalidade ausente/falha → **omite** a evidência (campo opcional, DD10) e loga (`case_id`).
3. Chama `fusao.avaliar_fusao(evidencias)`; gera o relatório (`relatorio.py`); monta a resposta do
   contrato §2 (`timestamp`, `case_id`, `evidencias`, `risco_detectado`, `mensagem_alerta`, `relatorio_url`).

### 4.3 `app/api/` — serviço FastAPI (F3F-04)

- `modelos.py`: `RequisicaoInferencia` e `RespostaRisco` (Pydantic v2) refletindo o contrato §1/§2
  (paciente, URLs, dados_vitais, texto_clinico → resposta com evidências e risco). Domínios validados.
- `main.py`: `app = FastAPI()`; `POST /inferencia` chama `pipeline.processar`; `GET /health` → `{status:"ok"}`.
  Erros de validação → `422` (automático do Pydantic); falha de modalidade é tratada no pipeline (não vira `500`).
- Servido por `uvicorn app.api.main:app`. Testado com `TestClient` (`httpx`).

### 4.4 `app/relatorio.py` — relatório automático (F3F-09)

- `gerar_markdown(json_fusao, paciente) -> str`: monta o **template** de
  [docs/06](../../../docs/06-relatorios-automaticos.md) §3 (resumo executivo, evidências por modalidade,
  gatilhos acionados, recomendação por nível de risco, anexos, disclaimer). **Pura/testável.**
- `salvar_relatorio(markdown, case_id, storage) -> url`: converte Markdown→HTML (`markdown`); tenta
  HTML→PDF (`weasyprint`) e, se indisponível, mantém HTML/Markdown (DD7); salva via `storage` e devolve a URL.

### 4.5 `app/storage.py` — armazenamento Azure/local (F3F-11)

Interface única (`salvar(bytes, nome) -> url`, `abrir(url) -> caminho_local`), selecionada por env:
- **Azure** (`STORAGE_BACKEND=azure` + `AZURE_STORAGE_CONNECTION_STRING`): `azure-storage-blob`,
  container configurável, SAS/expiração (ver [docs/07](../../../docs/07-privacidade-e-seguranca.md)).
- **Local** (padrão / sem credencial): grava sob `data/_storage/` (ignorado) e resolve caminhos locais.
- O **mesmo adaptador** é espelhado no Node (`backend/src/storage/`) para o upload; ambos compartilham as
  variáveis de ambiente do `.env`.

### 4.6 `app/metricas_fusao.py` — ganho da fusão (F3F-10)

- Sobre os casos de exemplo / mini-dataset, calcula a detecção de "caso crítico" em 4 cenários:
  **só-vídeo**, **só-vitais**, **só-áudio/texto** e **fusão** (via `pipeline`/`fusao`).
- Reusa `app.baseline.metricas_modalidade(y_true, y_pred)` para precisão/recall/**taxa de FP**.
- Salva `models/metricas_fusao.json` (tabela comparativa). **Conclusão esperada:** a fusão reduz FP
  e/ou aumenta recall — base da Tarefa 3.1b no relatório.

### 4.7 Backend Node (`backend/src/`) — F3F-05..F3F-08

- `rotas/pacientes.js`: CRUD enxuto (criar/listar/excluir) sobre `db/repositorios.js`; `DELETE` remove em
  cascata o `Caso` e os artefatos no storage (arquitetura §7).
- `rotas/analisar.js`: `multer` recebe os arquivos → `storage.salvar` (Blob/local) → monta payload do
  contrato §1 → `servicos/inferencia.js` (`axios`) → grava `Caso` (resultado + URLs) → `realtime/alertas.js`.
- `realtime/alertas.js`: se `risco_detectado ∈ {MEDIO, ALTO}` → `io.emit("alerta", {...})` com `case_id`,
  paciente, risco e `mensagem_alerta`.
- `config.js` (dotenv): `PORT`, `AI_SERVICE_URL`, `STORAGE_BACKEND`, `AZURE_*`, `DB_PATH`. `pino` loga JSON
  com `case_id` (mesma convenção do `ai-service`/Fase 1).
- `db/`: `better-sqlite3` com tabelas `pacientes` e `casos` (modelo de arquitetura §7). Migração simples no boot.

### 4.8 Cliente mínimo (`backend/public/index.html`) — F3F-16

Página estática servida pelo Express: conecta `socket.io-client`, escuta `alerta` e mostra um
**banner** (cor por nível de risco, conforme [docs/frontend](../../../docs/frontend.md) §4). Suficiente
para a cena de demonstração; o dashboard React completo é uma feature à parte.

### 4.9 Reprodutibilidade e E2E — F3F-12..F3F-15

- `ai-service/Dockerfile` (Python + uvicorn) e `backend/Dockerfile` (Node); `docker-compose.yml` orquestra
  os dois (`depends_on`, `env_file`), conforme [qualidade-testes-ci](../../../docs/qualidade-testes-ci.md) §1.
- `.github/workflows/ci.yml`: job Python (`ruff check scripts ai-service` + `pytest -q`) e job Node
  (`eslint` + `jest`).
- `scripts/e2e_demo`: processa um `data/casos/*.json` ponta-a-ponta (upload local → `/analisar` → alerta no
  log/cliente) e imprime/coleta evidências para o relatório/vídeo (Tarefa 3.5).
- Deploy Azure documentado (App Service / Container) + variáveis; **fallback local** sempre funcional.

## 5. Modelo de dados (arquitetura §7)

`better-sqlite3`, duas tabelas espelhando [arquitetura §7](../../../docs/arquitetura.md):

```
pacientes(id PK, primeiro_nome, idade, gestante, idade_gestacional_semanas, criado_em)
casos(id PK, paciente_id FK, video_cicatriz_url, video_fisioterapia_url, audio_url,
      sinais_vitais_csv_url, texto_clinico, risco_detectado, relatorio_url, resultado_json, timestamp)
```

- `gestante = false` → `idade_gestacional_semanas` nulo.
- Excluir paciente → cascata em `casos` + remoção dos artefatos no storage.

## 6. Decisões de design

| #    | Decisão                                                                       | Justificativa                                                                          |
| ---- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| DD1  | **Fusão como motor de regras puro** em `ai-service/app/fusao.py`              | [docs/00](../../../docs/00-visao-geral-e-escopo.md) D5: explicável, demonstrável, testável |
| DD2  | **Reusar as inferências da Fase 2** sem reescrever modelos                    | Fase 2 já entrega o dicionário do contrato §3; pipeline só orquestra                    |
| DD3  | **Pipeline único** consumido por FastAPI e pelos testes                       | Uma porta de entrada da IA; `POST /inferencia` é wrapper fino                           |
| DD4  | **FastAPI + Pydantic v2** para validar o contrato                             | Validação declarativa do payload; `422` automático; padrão atual                        |
| DD5  | **Node como orquestrador** (upload, storage, banco, alerta), Python só IA     | [arquitetura](../../../docs/arquitetura.md): isola responsabilidades                    |
| DD6  | **Tempo real via `socket.io` (WebSocket)**; SSE como alternativa              | [docs/frontend](../../../docs/frontend.md) sugere `socket.io-client`; doc 3.3b aceita ambos |
| DD7  | **Relatório sempre Markdown/HTML; PDF opcional (`weasyprint`) com fallback**  | `weasyprint` exige libs de sistema; garante saída mesmo sem PDF (edge case do spec)     |
| DD8  | **Storage com adaptador Azure | local** (mesma interface, escolha por env)    | [docs/03](../../../docs/03-fase3-fusao-e-nuvem.md) §3.4: ter fallback local p/ a demo   |
| DD9  | **SQLite (`better-sqlite3`) local** para Paciente/Caso; Postgres/Cosmos opcional | MVP demonstrável e reproduzível; banco gerenciado é deploy avançado (out of scope)   |
| DD10 | **Cliente mínimo** (HTML+socket.io) em vez do dashboard React completo        | Demonstra a Tarefa 3.3b; dashboard rico é feature de front-end separada                 |
| DD11 | **Testar funções puras** (fusão, relatório, métricas) + rotas com mocks       | Núcleo de valor é determinístico; rede/IO/Blob validados por E2E/smoke (segue Fase 2 DD5) |
| DD12 | **Versões: última estável, confirmar via `context7`/registries**             | Princípio do `AGENTS.md`; não inventar números (mantém convenção da Fase 2)             |
| DD13 | **`case_id` em todos os logs** (Python `get_logger` + Node `pino`)            | Observabilidade ponta-a-ponta ([qualidade-testes-ci](../../../docs/qualidade-testes-ci.md) §4) |
| DD14 | **Node em JS moderno (ESM)** no MVP; TypeScript opcional                      | Reduz atrito de build; foco no fluxo. `package.json` com versões fixadas (Fase 4)       |

## 7. Estratégia de testes (entra em cada tarefa)

Conforme [qualidade-testes-ci](../../../docs/qualidade-testes-ci.md): **prioridade no motor de fusão**.
O `pyproject.toml` da raiz já cobre `ai-service/tests`; o Node usa `jest` em `backend/tests`.

| Camada                                  | Tipo  | O que cobre                                                          |
| --------------------------------------- | ----- | ------------------------------------------------------------------- |
| `fusao.avaliar_fusao`                   | unit  | matriz base + regras (infecção, pré-eclâmpsia, violência, psico); contexto isolado teto `MEDIO`; "vermelhidão leve sem febre/PA" não é `ALTO` |
| `pipeline.processar`                    | unit  | montagem de evidências; modalidade ausente é omitida; resposta válida no contrato §2 |
| `relatorio.gerar_markdown`              | unit  | seções do template + gatilhos no texto (determinístico)             |
| `metricas_fusao`                        | unit  | comparação fusão × modalidade (reusa `baseline.metricas_modalidade`) |
| `api` (FastAPI `TestClient`)            | unit/integ | `/inferencia` 200 (payload válido) e 422 (inválido); `/health` 200 |
| `pacientes` (supertest)                 | unit  | CRUD; cascata no `DELETE`                                            |
| `analisar` (supertest + python mock)    | integ | upload → storage local → `/inferencia` mockado → `Caso` salvo → evento `alerta` emitido |
| storage Azure, deploy, conversão PDF    | none  | IO/rede/sistema — validados por E2E/smoke (DD11)                    |

- **Gate Python:** `ruff check scripts ai-service && pytest -q`.
- **Gate Node:** `npm run lint && npm test` (`eslint` + `jest`).
- **Gate E2E (manual/CI opcional):** `scripts/e2e_demo` processa um caso e mostra o alerta.

## 8. Riscos e mitigação

| Risco                                               | Mitigação na Fase 3                                                              |
| --------------------------------------------------- | -------------------------------------------------------------------------------- |
| Conta/limite da **Azure** trava a demo              | Adaptador de storage com **fallback local** (DD8); deploy documentado, não obrigatório para o gate |
| **Cicatriz** ainda em smoke (não detecta acima do limiar) | Pipeline degrada a evidência (DD10); a fusão usa as demais; documentar no relatório |
| Áudio/fisioterapia dependem de dados manuais        | Modalidade ausente é omitida; casos de exemplo usam as modalidades disponíveis    |
| `weasyprint`/libs de PDF ausentes no ambiente       | Relatório em Markdown/HTML garantido; PDF é melhor-esforço (DD7)                  |
| Acoplamento Node ↔ Python (rede)                    | `axios` com timeout/erro claro; `case_id` nos logs dos dois lados (DD13)          |
| Regras de fusão divergirem do contrato              | `app/schemas.py` valida domínios; `fusao` coberta por muitos testes (DD11)        |
| Segredos vazarem no Git                             | `.env` no `.gitignore`; `.env.example` sem valores; storage por env (docs/07)     |
| Banco SQLite não escalar                            | Suficiente para o MVP/demo; Postgres/Cosmos como evolução (DD9, out of scope)     |

## 9. Rastreabilidade design → requisito

| Componente                         | Requisito(s)        |
| ---------------------------------- | ------------------- |
| `app/fusao.py`                     | F3F-01, F3F-02      |
| `app/pipeline.py`                  | F3F-03              |
| `app/api/`                         | F3F-04              |
| `backend` `POST /analisar` + storage | F3F-05, F3F-11    |
| `backend` CRUD pacientes           | F3F-06              |
| `backend` persistência (SQLite)    | F3F-07              |
| `backend` tempo real (socket.io)   | F3F-08              |
| `app/relatorio.py`                 | F3F-09              |
| `app/metricas_fusao.py`            | F3F-10              |
| Docker + compose + `.env.example`  | F3F-12              |
| CI (GitHub Actions)                | F3F-13              |
| `scripts/e2e_demo` + logging       | F3F-14              |
| Deploy Azure (docs/scripts)        | F3F-15              |
| `backend/public/index.html`        | F3F-16              |
| READMEs + STATE + cross-refs       | F3F-17              |
