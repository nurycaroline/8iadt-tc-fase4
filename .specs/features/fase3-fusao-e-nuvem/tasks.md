# Fase 3 — Fusão Multimodal e Integração em Nuvem — Tasks

**Spec**: [`spec.md`](spec.md)
**Design**: [`design.md`](design.md)
**Status**: Planejado (a implementar). Insumos prontos: serviço de IA da [Fase 2](../fase2-modelos/)
(inferências com saída do contrato §3) + casos de exemplo em `data/casos/*.json` (Fase 1).

> Cada tarefa = 1 entregável atômico (um arquivo/uma função/uma capacidade), com `Done when` testável e
> um commit. Funções puras carregam testes na própria tarefa (co-located), conforme `design.md` §7.
> Não re-treinar modelos (Fase 2) nem re-baixar dados (Fase 1) — esta fase **consome** as saídas.

---

## Execution Plan

### Fase A — Inteligência de fusão (Python, núcleo de valor) — Sequencial→Paralela

A fusão e o pipeline vêm primeiro: são o coração do projeto e não dependem de nuvem.

```
T1 (deps) → T2 (fusão) → T3 (pipeline) → ┌→ T4 (relatório)        [P]
                                          ├→ T5 (métricas fusão)  [P]
                                          └→ T6 (FastAPI)         [P]
```

### Fase B — Orquestrador Node + tempo real — Paralela à Fase A (usa mock do Python)

Pode começar cedo com **mock** da resposta de IA (contrato já definido).

```
T7 (scaffold) → T8 (storage) → T9 (db/CRUD) → T10 (/analisar) → T11 (tempo real) → T12 (cliente mínimo)
```

### Fase C — Integração, nuvem e reprodutibilidade — Sequencial (após A e B)

```
(T6 + T10) → T13 (storage Azure) → T14 (Docker+compose) → T15 (CI) → T16 (E2E) → T17 (Azure deploy) → T18 (docs)
```

---

## Task Breakdown

### T1: Dependências da Fase 3 (Python + Node)

**What**: Acrescentar a `ai-service/requirements.txt` os pacotes da API/relatório/storage e criar o
`backend/package.json` com as deps do orquestrador (versões: última estável — `context7`/registries).
**Where**: `ai-service/requirements.txt`, `backend/package.json`
**Depends on**: None
**Reuses**: `design.md` §2
**Requirement**: F3F-04, F3F-05, F3F-12

**Tools**: MCP: `context7` (confirmar versões/APIs atuais de fastapi, uvicorn, azure-storage-blob, weasyprint, express, socket.io, better-sqlite3) · Skill: NONE

**Done when**:

- [ ] `requirements.txt` inclui `fastapi`, `uvicorn[standard]`, `httpx`, `azure-storage-blob`, `markdown`, `weasyprint`.
- [ ] `backend/package.json` inclui `express`, `multer`, `axios`, `socket.io`, `@azure/storage-blob`, `dotenv`, `better-sqlite3`, `zod`, `pino` (+ `jest`, `supertest`, `eslint` em devDeps) com versões fixadas.
- [ ] `pip install -r ai-service/requirements.txt` e `npm install` (em `backend/`) resolvem sem conflito.

**Tests**: none · **Gate**: build
**Commit**: `chore(fase3): dependências do serviço de IA e do backend Node`

---

### T2: `app/fusao.py` — motor de regras clínicas (Tarefa 3.1) ⭐

**What**: Implementar `avaliar_fusao(evidencias) -> {risco_detectado, mensagem_alerta, gatilhos}` com a
matriz base (contrato §4) + regras de elevação (infecção puerperal, pré-eclâmpsia, violência, psico) e
contexto isolado com teto `MEDIO`.
**Where**: `ai-service/app/fusao.py`, `ai-service/tests/test_fusao.py`
**Depends on**: T1
**Reuses**: `app/limiares.py` (`risco_alto_sinais_vitais`, `confianca_suficiente`, `CONFIANCA_MINIMA`); `app/schemas.py` (domínios); `design.md` §4.1
**Requirement**: F3F-01, F3F-02

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Matriz base: infecção+risco → `ALTO`; infecção+normal → `MEDIO`; ok+risco → `MEDIO`; ok+normal → `BAIXO`.
- [ ] Regras: cicatriz infecção + febre/dor (texto/áudio) → `ALTO`+`infeccao_puerperal`; vitais risco + texto `complicacao` → `ALTO`+`pre_eclampsia`; áudio `violencia` → `ALTO`+`violencia`; áudio `depressao_pos_parto/ansiedade` → ≥`MEDIO`+`desconforto_psicologico`.
- [ ] Contexto isolado (só texto/áudio fraco) tem teto `MEDIO`; "vermelhidão leve sem febre/PA" não vira `ALTO`.
- [ ] `mensagem_alerta` concatena os gatilhos; `gatilhos` lista os acionados; modalidade ausente não quebra.
- [ ] Gate: `ruff check ai-service && pytest ai-service/tests/test_fusao.py -q`.
- [ ] Test count: ≥8 testes (matriz base + cada regra + contexto isolado + caso "vermelhidão leve").

**Tests**: unit · **Gate**: quick
**Commit**: `feat(ai): motor de fusão clínica (regras explícitas)`

---

### T3: `app/pipeline.py` — orquestração da inferência (contrato §1 → §2)

**What**: `processar(requisicao) -> resposta` que roda as inferências das modalidades presentes, monta
evidências (via `schemas`), chama `avaliar_fusao`, gera relatório e devolve o JSON do contrato §2.
**Where**: `ai-service/app/pipeline.py`, `ai-service/tests/test_pipeline.py`
**Depends on**: T2
**Reuses**: Fase 2 — `cicatriz.inferencia.detectar`, `fisioterapia.inferencia.avaliar`, `sinais_vitais.inferencia.prever`, `audio.classificacao.inferir`, `texto.nlp.analisar`; `app/schemas.py`; `design.md` §4.2
**Requirement**: F3F-03

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Invoca a inferência de cada modalidade **presente** no payload (contrato §1) e monta as evidências.
- [ ] Modalidade ausente/falha → evidência omitida + log com `case_id` (sem derrubar o caso, DD10).
- [ ] Monta a resposta do contrato §2 (`timestamp`, `case_id`, `evidencias`, `risco_detectado`, `mensagem_alerta`, `relatorio_url`).
- [ ] Roda sobre `data/casos/caso_alto.json` → `risco_detectado = ALTO` coerente; `caso_baixo` → `BAIXO`.
- [ ] Gate: `ruff check ai-service && pytest ai-service/tests/test_pipeline.py -q`.
- [ ] Test count: ≥3 testes (caso completo; modalidade ausente omitida; resposta válida no contrato).

**Tests**: unit · **Gate**: quick
**Commit**: `feat(ai): pipeline de inferência multimodal (contrato §1→§2)`

---

### T4: `app/relatorio.py` — relatório automático (Tarefa 3.3c / docs/06) [P]

**What**: `gerar_markdown(json_fusao, paciente)` (template de docs/06 §3) + `salvar_relatorio(...)`
(Markdown→HTML via `markdown`; HTML→PDF via `weasyprint` com fallback) salvando no storage.
**Where**: `ai-service/app/relatorio.py`, `ai-service/tests/test_relatorio.py`
**Depends on**: T3
**Reuses**: `docs/06-relatorios-automaticos.md` §3/§4; `app/storage.py` (T8/T13); `design.md` §4.4
**Requirement**: F3F-09

**Tools**: MCP: `context7` (API atual de `markdown`/`weasyprint`) · Skill: NONE

**Done when**:

- [ ] `gerar_markdown` (pura) produz as seções do template (resumo, evidências por modalidade, gatilhos, recomendação, anexos, disclaimer).
- [ ] Conteúdo-chave reflete o gatilho (infecção puerperal / pré-eclâmpsia / psico / violência).
- [ ] `salvar_relatorio` converte e salva; sem `weasyprint`/libs → mantém HTML/Markdown (fallback) sem quebrar.
- [ ] Gate: `ruff check ai-service && pytest ai-service/tests/test_relatorio.py -q`.
- [ ] Test count: ≥3 testes (seções presentes; gatilho no texto; fallback sem PDF).

**Tests**: unit · **Gate**: quick
**Commit**: `feat(ai): relatório clínico automático (Markdown→HTML/PDF)`

---

### T5: `app/metricas_fusao.py` — ganho da fusão (Tarefa 3.1b) [P]

**What**: Comparar fusão × só-vídeo × só-vitais × só-áudio/texto sobre os casos de exemplo; salvar
`models/metricas_fusao.json` com precisão/recall/taxa de FP por cenário.
**Where**: `ai-service/app/metricas_fusao.py`, `ai-service/tests/test_metricas_fusao.py`
**Depends on**: T3
**Reuses**: `app.baseline.metricas_modalidade`; `app/pipeline.py`, `app/fusao.py`; `data/casos/*.json`; `design.md` §4.6
**Requirement**: F3F-10

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Avalia os 4 cenários (3 modalidades isoladas + fusão) sobre os casos/mini-dataset.
- [ ] `python -m app.metricas_fusao` gera `models/metricas_fusao.json` (precisão, recall, taxa de FP por cenário).
- [ ] Teste unitário: cenário sintético conhecido → métricas esperadas (FP da fusão ≤ FP da modalidade única).
- [ ] Gate: `ruff check ai-service && pytest ai-service/tests/test_metricas_fusao.py -q`.
- [ ] Test count: ≥2 testes.

**Tests**: unit · **Gate**: quick
**Commit**: `feat(ai): métricas do ganho da fusão vs modalidade única`

---

### T6: `app/api/` — serviço FastAPI `POST /inferencia` + `/health` (Tarefa 3.2) [P]

**What**: Modelos Pydantic do contrato §1/§2 + app FastAPI servindo `POST /inferencia` (chama o pipeline)
e `GET /health`.
**Where**: `ai-service/app/api/__init__.py`, `ai-service/app/api/modelos.py`, `ai-service/app/api/main.py`, `ai-service/tests/test_api.py`
**Depends on**: T3
**Reuses**: `app/pipeline.py`; `docs/contrato-api.md`; `design.md` §4.3
**Requirement**: F3F-04

**Tools**: MCP: `context7` (API atual de FastAPI/Pydantic v2/TestClient) · Skill: NONE

**Done when**:

- [ ] `RequisicaoInferencia`/`RespostaRisco` (Pydantic v2) refletem o contrato §1/§2 com domínios válidos.
- [ ] `POST /inferencia` → `200` + JSON do contrato §2 para payload válido; `422` para inválido; `GET /health` → `200`.
- [ ] Falha de modalidade não vira `500` (tratada no pipeline).
- [ ] `uvicorn app.api.main:app` sobe sem erro (smoke).
- [ ] Gate: `ruff check ai-service && pytest ai-service/tests/test_api.py -q`.
- [ ] Test count: ≥3 testes (200, 422, /health) via `TestClient`.

**Tests**: integ · **Gate**: quick
**Commit**: `feat(ai): serviço FastAPI POST /inferencia + /health`

---

### T7: Scaffold do backend Node (Express + config + logging)

**What**: Criar `backend/` com `server.js` (Express + pino), `config.js` (dotenv) e estrutura de pastas;
`eslint` configurado; `npm run lint`/`npm test` definidos.
**Where**: `backend/src/server.js`, `backend/src/config.js`, `backend/.eslintrc.json`, `backend/package.json` (scripts)
**Depends on**: T1
**Reuses**: `design.md` §3/§4.7; convenção de logging com `case_id` (Fase 2 `common.get_logger`)
**Requirement**: F3F-05 (fundação)

**Tools**: MCP: `context7` (API atual de express/pino/eslint) · Skill: NONE

**Done when**:

- [ ] `npm start` sobe o Express na porta de `config` (env) com `/health` → `200`.
- [ ] `pino` loga JSON incluindo `case_id` quando presente.
- [ ] `npm run lint` passa (eslint) e `npm test` roda o jest (mesmo que vazio inicialmente).

**Tests**: none · **Gate**: build
**Commit**: `feat(backend): scaffold Express (config, logging, lint)`

---

### T8: `backend/src/storage/` — adaptador local (fallback) (parte de 3.4)

**What**: Interface de storage (`salvar`, `abrir`, `remover`) com implementação **local** (disco) e o
seletor por env (`STORAGE_BACKEND`). Espelha `app/storage.py` (Python).
**Where**: `backend/src/storage/index.js`, `backend/src/storage/local.js`, `ai-service/app/storage.py`, `ai-service/tests/test_storage.py`
**Depends on**: T7
**Reuses**: `design.md` §4.5; `.gitignore` (ignorar `data/_storage/`)
**Requirement**: F3F-11 (fallback)

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] `salvar(bytes, nome)` grava sob `data/_storage/` e devolve uma URL/caminho resolvível por `abrir`.
- [ ] Seletor escolhe `local` por padrão (sem credencial); interface idêntica à futura Azure.
- [ ] `app/storage.py` (Python) expõe a mesma interface e tem teste unitário do modo local.
- [ ] Gate: `ruff check ai-service && pytest ai-service/tests/test_storage.py -q`; `npm run lint`.

**Tests**: unit (Python local) · **Gate**: quick
**Commit**: `feat(fase3): adaptador de storage local (fallback Azure)`

---

### T9: `backend/src/db/` — persistência SQLite + CRUD de pacientes (Tarefa 3.3)

**What**: `better-sqlite3` com tabelas `pacientes`/`casos` (arquitetura §7), repositórios e rotas
`POST /pacientes`, `GET /pacientes`, `DELETE /pacientes/:id` (cascata).
**Where**: `backend/src/db/index.js`, `backend/src/db/repositorios.js`, `backend/src/rotas/pacientes.js`, `backend/tests/pacientes.test.js`
**Depends on**: T7
**Reuses**: `docs/arquitetura.md` §7; `design.md` §4.7/§5; `zod` (validação)
**Requirement**: F3F-06, F3F-07

**Tools**: MCP: `context7` (API atual de better-sqlite3/zod) · Skill: NONE

**Done when**:

- [ ] Migração cria `pacientes` e `casos` no boot; `DB_PATH` por env (ignorado pelo Git).
- [ ] `POST /pacientes` valida (zod) e cria; `GET /pacientes` lista; `DELETE /pacientes/:id` remove em cascata o `Caso` + artefatos.
- [ ] Teste (supertest): criar → listar → excluir; gestante=false zera `idade_gestacional_semanas`.
- [ ] Gate: `npm run lint && npm test`.
- [ ] Test count: ≥3 testes.

**Tests**: unit · **Gate**: quick
**Commit**: `feat(backend): persistência SQLite + CRUD de pacientes`

---

### T10: `POST /analisar` — upload → storage → Python → banco (Tarefa 3.3)

**What**: Rota com `multer` (upload) → `storage.salvar` → monta payload do contrato §1 → `axios` para
`{AI_SERVICE_URL}/inferencia` → grava `Caso` → devolve o JSON de risco.
**Where**: `backend/src/rotas/analisar.js`, `backend/src/servicos/inferencia.js`, `backend/tests/analisar.test.js`
**Depends on**: T8, T9
**Reuses**: `storage`, `repositorios`, `docs/contrato-api.md` §1; `design.md` §4.7
**Requirement**: F3F-05

**Tools**: MCP: `context7` (API atual de multer/axios) · Skill: NONE

**Done when**:

- [ ] Recebe upload (vídeo/áudio/CSV/texto) + `paciente_id`; sobe ao storage; monta o payload do contrato §1.
- [ ] Chama o serviço Python (`axios`) e persiste o `Caso` (resultado + URLs); responde o JSON de risco.
- [ ] Serviço Python indisponível → `502/504` claro com `case_id` logado (upload preservado).
- [ ] Teste (supertest + axios mockado): upload de exemplo → `Caso` salvo → resposta com risco.
- [ ] Gate: `npm run lint && npm test`.
- [ ] Test count: ≥2 testes (sucesso; Python indisponível).

**Tests**: integ · **Gate**: quick
**Commit**: `feat(backend): POST /analisar (upload→storage→IA→banco)`

---

### T11: Alerta em tempo real (socket.io) (Tarefa 3.3b)

**What**: Integrar `socket.io` ao server e emitir `alerta` quando o risco for `MEDIO`/`ALTO` no
`/analisar`.
**Where**: `backend/src/realtime/alertas.js`, `backend/src/server.js` (integrar io), `backend/src/rotas/analisar.js` (modificar), `backend/tests/analisar.test.js` (modificar)
**Depends on**: T10
**Reuses**: `design.md` §4.7; `docs/03` Tarefa 3.3b; `docs/frontend.md` §5
**Requirement**: F3F-08

**Tools**: MCP: `context7` (API atual de socket.io) · Skill: NONE

**Done when**:

- [ ] `MEDIO`/`ALTO` → `io.emit("alerta", {case_id, paciente, risco_detectado, mensagem_alerta})`; `BAIXO` → sem alerta de risco.
- [ ] Teste: cliente socket.io de teste recebe o evento ao processar um caso alto (Python mockado).
- [ ] Gate: `npm run lint && npm test`.
- [ ] Test count: ≥1 teste de emissão de alerta.

**Tests**: integ · **Gate**: quick
**Commit**: `feat(backend): alerta em tempo real via socket.io`

---

### T12: Cliente mínimo de demonstração do alerta

**What**: `backend/public/index.html` que conecta `socket.io-client` e exibe o alerta (banner por cor de
risco), servido como estático pelo Express.
**Where**: `backend/public/index.html`, `backend/src/server.js` (servir estático)
**Depends on**: T11
**Reuses**: `docs/frontend.md` §4 (cores de risco); `design.md` §4.8
**Requirement**: F3F-16

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Página conecta ao WebSocket e mostra o alerta (paciente, risco, mensagem) em tempo real.
- [ ] `ALTO` destaca em vermelho (banner); cores seguem docs/frontend §4 (verde/amarelo/vermelho).
- [ ] Servida em `/` (ou `/demo`) pelo Express; smoke manual com o E2E (T16).

**Tests**: none · **Gate**: build
**Commit**: `feat(backend): cliente mínimo de demonstração do alerta`

---

### T13: Storage Azure Blob (modo nuvem) (Tarefa 3.4)

**What**: Implementação Azure do adaptador de storage (Python `azure-storage-blob` + Node
`@azure/storage-blob`), selecionada por `STORAGE_BACKEND=azure` + connection string; SAS/expiração.
**Where**: `ai-service/app/storage.py` (modo azure), `backend/src/storage/azureBlob.js`
**Depends on**: T8
**Reuses**: `design.md` §4.5; `docs/07-privacidade-e-seguranca.md` (TLS/SAS/segredos)
**Requirement**: F3F-11

**Tools**: MCP: `context7` (API atual de azure-storage-blob / @azure/storage-blob) · Skill: NONE

**Done when**:

- [ ] Com `STORAGE_BACKEND=azure` + credencial → grava/lê no container; sem credencial → cai no local (T8).
- [ ] SAS/expiração aplicados às URLs de artefatos; segredos só via `.env`/Key Vault (nunca no Git).
- [ ] Smoke documentado (com credencial de teste); o modo local continua sendo o caminho do gate.

**Tests**: none (rede/IO — smoke) · **Gate**: build
**Commit**: `feat(fase3): storage Azure Blob (modo nuvem) com SAS`

---

### T14: Docker + docker-compose + `.env.example` (qualidade-testes-ci §1)

**What**: `ai-service/Dockerfile` (uvicorn) + `backend/Dockerfile` (Node) + `docker-compose.yml` na raiz
+ `.env.example` (sem segredos).
**Where**: `ai-service/Dockerfile`, `backend/Dockerfile`, `docker-compose.yml`, `.env.example`, `.dockerignore`
**Depends on**: T6, T10
**Reuses**: `docs/qualidade-testes-ci.md` §1; `design.md` §4.9
**Requirement**: F3F-12

**Tools**: MCP: `context7` (imagens base atuais python/node) · Skill: NONE

**Done when**:

- [ ] `docker compose up` sobe `ai-service` (8000) e `backend` (3000) com `env_file` e `depends_on`.
- [ ] `.env.example` lista todas as variáveis (URLs, portas, `STORAGE_BACKEND`, `AZURE_*`, `DB_PATH`) sem valores.
- [ ] `backend` chama `ai-service` pelo nome do serviço da rede do compose.

**Tests**: none · **Gate**: build
**Commit**: `chore(fase3): Docker + docker-compose + .env.example`

---

### T15: CI (GitHub Actions) — Python + Node (qualidade-testes-ci §3)

**What**: Workflow que roda `ruff`+`pytest` (Python) e `eslint`+`jest` (Node) a cada push/PR.
**Where**: `.github/workflows/ci.yml`
**Depends on**: T6, T10
**Reuses**: `docs/qualidade-testes-ci.md` §3; `pyproject.toml` (gate Python)
**Requirement**: F3F-13

**Tools**: MCP: `context7` (actions atuais setup-python/setup-node) · Skill: NONE

**Done when**:

- [ ] Job Python: instala `ai-service/requirements.txt`, roda `ruff check scripts ai-service` e `pytest -q`.
- [ ] Job Node: `npm ci` em `backend/`, `npm run lint` e `npm test`.
- [ ] Workflow dispara em `push`/`pull_request`; verde no PR.

**Tests**: none · **Gate**: build
**Commit**: `ci(fase3): lint + testes de Python e Node no GitHub Actions`

---

### T16: Teste ponta-a-ponta + observabilidade (Tarefa 3.5)

**What**: Script/teste que processa um `data/casos/*.json` ponta-a-ponta (upload local → `/analisar` →
`/inferencia` → JSON → alerta no cliente/log) e coleta evidências; confirma `case_id` nos logs dos dois serviços.
**Where**: `scripts/e2e_demo.py` (ou `.sh`), `scripts/tests/test_e2e_smoke.py` (opcional), doc no README
**Depends on**: T11, T6
**Reuses**: `data/casos/*.json`; `design.md` §4.9; `docs/03` Tarefa 3.5
**Requirement**: F3F-14

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] `scripts/e2e_demo` sobe/usa a stack, processa um caso e mostra o alerta (cliente/log) com evidências.
- [ ] `case_id` aparece nos logs estruturados do `ai-service` (pino do Node + `get_logger` do Python).
- [ ] Evidências (logs/prints) descritas para o relatório/vídeo (Fase 4).

**Tests**: integ (smoke) · **Gate**: build
**Commit**: `test(fase3): pipeline ponta-a-ponta com o caso de exemplo`

---

### T17: Deploy Azure (docs + scripts) com fallback (Tarefa 3.4)

**What**: Documentar e roteirizar o deploy do serviço Python na Azure (App Service / Container Instances)
+ criação do Blob, variáveis de ambiente e SAS; deixar claro o fallback local.
**Where**: `docs/deploy-azure.md` (novo), `scripts/azure/` (opcional: `az` CLI), `.env.example` (refs)
**Depends on**: T13, T14
**Reuses**: `docs/03` §3.4; `docs/07-privacidade-e-seguranca.md`; `docs/arquitetura.md`
**Requirement**: F3F-15

**Tools**: MCP: `context7` (Azure CLI / App Service / Blob atuais) · Skill: NONE

**Done when**:

- [ ] Passos reproduzíveis: criar Storage Account/container, publicar a imagem do `ai-service`, configurar env.
- [ ] Variáveis e SAS/expiração documentadas; segredos via Key Vault/`.env` (nunca no Git).
- [ ] Seção de **fallback local** caso a Azure esteja indisponível (garante a demo).

**Tests**: none · **Gate**: build
**Commit**: `docs(fase3): deploy na Azure (Blob + serviço) com fallback local`

---

### T18: Documentação — READMEs + STATE + contrato/cross-refs

**What**: Atualizar `README.md` (raiz: como rodar a stack, `docker compose up`, `.env`), `ai-service/README.md`
(fusão/pipeline/API/relatório/métricas), criar `backend/README.md`, e registrar a fusão/decisões no STATE.
**Where**: `README.md`, `ai-service/README.md`, `backend/README.md`, `.specs/project/STATE.md`, `docs/03-fase3-fusao-e-nuvem.md` (marcar itens)
**Depends on**: T16, T17
**Reuses**: `design.md`; `docs/04-fase4-entregaveis.md` (Tarefa 4.1)
**Requirement**: F3F-17

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] READMEs explicam como subir Python+Node (local e Docker), variáveis de ambiente e o fluxo do `/analisar`.
- [ ] STATE registra a Fase 3 (fusão + API + nuvem) e as decisões DD1–DD14; DoD de `docs/03` referenciado.
- [ ] Disclaimer ético (docs/07 §5) visível no README; nenhum segredo versionado.

**Tests**: none · **Gate**: build
**Commit**: `docs(fase3): READMEs + STATE + referências da fusão e nuvem`

---

## Parallel Execution Map

```
Fase A (Python — núcleo):
  T1 → T2 → T3 → ├── T4   [P]  (relatório)
                 ├── T5   [P]  (métricas da fusão)
                 └── T6   [P]  (FastAPI)

Fase B (Node — pode usar mock do Python, em paralelo à Fase A após T1):
  T7 → T8 → T9 → T10 → T11 → T12

Fase C (integração/nuvem/qualidade — após A e B):
  (T6 + T10) → T13 → T14 → T15 → T16 → T17 → T18
```

**Restrição de paralelismo**: T4/T5/T6 escrevem arquivos distintos sob `ai-service/app/` e dependem só de
T3 → `[P]` seguro. A Fase B (Node) é um repositório separado (`backend/`) e roda em paralelo à Fase A
usando um **mock** da resposta da IA (contrato já definido) — só precisa de T1 (deps). T13–T18 são
sequenciais por consumirem ambos os serviços / consolidarem nuvem, CI e docs.

---

## Task Granularity Check

| Task | Escopo                                          | Status      |
| ---- | ----------------------------------------------- | ----------- |
| T1   | deps (requirements + package.json)              | ✅ Granular |
| T2   | 1 módulo (fusão) + teste                        | ✅ Granular |
| T3   | 1 módulo (pipeline) + teste                     | ✅ Granular |
| T4   | 1 módulo (relatório) + teste                    | ✅ Granular |
| T5   | 1 módulo (métricas) + teste                     | ✅ Granular |
| T6   | API FastAPI (modelos + main) + teste            | ✅ Granular |
| T7   | scaffold Node (server+config+lint)              | ✅ Granular |
| T8   | adaptador storage local (Py+Node) + teste       | ✅ Granular |
| T9   | db SQLite + CRUD pacientes + teste              | ✅ Granular |
| T10  | rota /analisar + serviço axios + teste          | ✅ Granular |
| T11  | tempo real socket.io + teste                    | ✅ Granular |
| T12  | cliente mínimo (HTML)                           | ✅ Granular |
| T13  | storage Azure (Py+Node)                         | ✅ Granular |
| T14  | Docker + compose + env.example                  | ✅ Granular |
| T15  | CI GitHub Actions                               | ✅ Granular |
| T16  | E2E + observabilidade                           | ✅ Granular |
| T17  | deploy Azure (docs/scripts)                     | ✅ Granular |
| T18  | docs (READMEs + STATE)                          | ✅ Granular |

---

## Diagram-Definition Cross-Check

| Task | Depends On (body) | Diagrama mostra        | Status   |
| ---- | ----------------- | ---------------------- | -------- |
| T1   | None              | (raiz A/B)             | ✅ Match |
| T2   | T1                | T1→T2                  | ✅ Match |
| T3   | T2                | T2→T3                  | ✅ Match |
| T4   | T3                | T3→T4 [P]              | ✅ Match |
| T5   | T3                | T3→T5 [P]              | ✅ Match |
| T6   | T3                | T3→T6 [P]              | ✅ Match |
| T7   | T1                | T1→T7 (Fase B)         | ✅ Match |
| T8   | T7                | T7→T8                  | ✅ Match |
| T9   | T7                | T8→T9 (cadeia)         | ✅ Match |
| T10  | T8, T9            | T9→T10                 | ✅ Match |
| T11  | T10               | T10→T11                | ✅ Match |
| T12  | T11               | T11→T12                | ✅ Match |
| T13  | T8                | (C) T13                | ✅ Match |
| T14  | T6, T10           | (T6+T10)→…→T14         | ✅ Match |
| T15  | T6, T10           | →T15                   | ✅ Match |
| T16  | T11, T6           | →T16                   | ✅ Match |
| T17  | T13, T14          | →T17                   | ✅ Match |
| T18  | T16, T17          | →T18                   | ✅ Match |

> Nota: T9 depende de T7 (não de T8); o diagrama da Fase B é uma cadeia linear por conveniência de
> execução (um sub-agente por vez no Node), mas T8 e T9 poderiam ser `[P]` entre si após T7.

---

## Test Co-location Validation

| Task | Camada criada/modificada           | Matriz exige | Tarefa diz | Status |
| ---- | ---------------------------------- | ------------ | ---------- | ------ |
| T1   | deps                               | none         | none       | ✅ OK  |
| T2   | função pura (fusão)                | unit         | unit       | ✅ OK  |
| T3   | orquestração (pipeline)            | unit         | unit       | ✅ OK  |
| T4   | função pura (markdown) + IO        | unit         | unit       | ✅ OK  |
| T5   | função pura (métricas)             | unit         | unit       | ✅ OK  |
| T6   | API (FastAPI)                      | integ        | integ      | ✅ OK  |
| T7   | scaffold/IO                        | none         | none       | ✅ OK  |
| T8   | storage local (função)            | unit (Py)    | unit       | ✅ OK  |
| T9   | db/rotas                           | unit         | unit       | ✅ OK  |
| T10  | rota integração                    | integ        | integ      | ✅ OK  |
| T11  | tempo real                         | integ        | integ      | ✅ OK  |
| T12  | UI estática                        | none         | none       | ✅ OK  |
| T13  | storage Azure (rede/IO)            | none (DD11)  | none       | ✅ OK  |
| T14  | infra (Docker)                     | none         | none       | ✅ OK  |
| T15  | CI                                 | none         | none       | ✅ OK  |
| T16  | E2E (smoke)                        | integ        | integ      | ✅ OK  |
| T17  | docs/scripts deploy                | none         | none       | ✅ OK  |
| T18  | docs                               | none         | none       | ✅ OK  |

> Justificativa de `none`: T1/T7/T12/T13/T14/T15/T17/T18 são config/infra/IO/rede/docs (DD11). A lógica
> determinística testável está concentrada nas funções puras (fusão, relatório, métricas) e nas rotas
> Node (testadas com `supertest` + Python mockado).

---

## Gate de fim da Fase 3

Conforme [`docs/cronograma-dependencias.md`](../../../docs/cronograma-dependencias.md) §4:
**pipeline ponta-a-ponta + métricas da fusão**. Equivale a concluir T1–T16 e T18 (T17 — deploy real na
Azure — pode usar **fallback local** e não bloqueia o gate; ver `spec.md` Success Criteria). O **motor de
fusão** (T2) é o núcleo e deve ter cobertura de testes forte; a **métrica do ganho da fusão** (T5) prova o
valor da multimodalidade para o relatório técnico (Fase 4).
