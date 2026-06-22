# Fase 7 — Privacidade e Segurança (LGPD)

> Objetivo: **fechar a lacuna** entre os controles de privacidade/segurança descritos em
> [`07-privacidade-e-seguranca.md`](07-privacidade-e-seguranca.md) (componente obrigatório do PDF — "os mais
> altos padrões de privacidade e segurança para dados sensíveis") e o que o **código realmente implementa**,
> de modo que a seção §5 do [`relatorio-tecnico.md`](relatorio-tecnico.md) deixe de ser **aspiracional**.
> Planejamento detalhado (Specify) em
> [`.specs/features/fase7-privacidade-e-seguranca/`](../.specs/features/fase7-privacidade-e-seguranca/spec.md).

> ✅ **Implementada.** Escopo confirmado pelo pedido **"implemente a fase 7"**; decisões resolvidas com os
> defaults propostos (ver [spec §Decisões a confirmar](../.specs/features/fase7-privacidade-e-seguranca/spec.md#decisões-a-confirmar-com-o-grupo)).
> Se "Fase 7" significasse **outro desafio (8IADT)** com enunciado próprio, traga o PDF e o escopo será
> reescrito.

## Motivação (o que falta para cumprir o `docs/07`)

| # | Controle do `docs/07` | Estado atual no código | Lacuna |
|---|------------------------|------------------------|--------|
| 1 | **Acesso / Rede (§2)** — "não expor publicamente sem auth"; RBAC | `POST /inferencia` e rotas Express **sem auth**; `ai-service` publicado em `8000:8000` | **Autenticação/credencial de serviço** ausente em todas as camadas |
| 2 | **Em trânsito (§2)** — HTTPS/TLS em todas as chamadas | Node↔Python em `http://`; `nginx` em `:80`; compose sem TLS | **Terminação TLS** na borda + TLS interno opcional |
| 3 | **Auditoria (§2)** — "log de quem acessou qual caso e quando" | `pino-http` loga `case_id` (processamento), sem identidade nem trilha de **acesso** | **Trilha de auditoria** de acesso persistida |
| 4 | **Retenção (§2)** — expiração/limpeza após o uso | Só `DELETE` manual (cascade); **sem TTL/job** | **Política de retenção** automatizável |
| 5 | **Minimização/Pseudonimização (§1)** — `case_id` opaco | `randomUUID()` na criação, mas `case_id` legível aceito; `primeiro_nome` trafega ao `ai-service` | **`case_id` sempre opaco** + **enxugar PII** do payload |
| 6 | **Acesso/Rede (§2)** — hardening HTTP | Sem `helmet`; `socket.io` CORS `*`; sem security headers; upload sem filtro de MIME | **Helmet + CORS allowlist + headers + validação de upload** |

> **Já satisfeito (não é desenvolvimento desta fase):** **SAS token com expiração**
> (`AZURE_SAS_EXPIRY_MINUTES`), **`.env`/`data/` no `.gitignore`**, **disclaimer ético** (README + relatório),
> **seção §5 LGPD** no relatório técnico e **dados sintéticos** (`scripts/data_prep/`). A Fase 7 **realça e
> atualiza** esses itens (F7-08), mas não os recria.
>
> **Permanece ação humana / bloqueado por ambiente** (não é desenvolvimento desta fase): provisionar
> **RBAC/Private Endpoint reais na Azure** (depende de conta — ligado ao F5-03) e **gravar o vídeo**
> (DD-F4-5).

## Estado da implementação

> **Implementada.** Escopo confirmado pelo pedido **"implemente a fase 7"**; decisões resolvidas com os
> defaults propostos (ver [spec §Decisões a confirmar](../.specs/features/fase7-privacidade-e-seguranca/spec.md#decisões-a-confirmar-com-o-grupo)).
> **Gate verde:** `ruff`+`pytest` (**111 testes** Python; +4), `eslint`+`jest` (**32 testes** Node; +14) e
> `eslint`+`vitest`+`build` do frontend (**7 testes**), além do novo job **conformidade** no CI. Os controles
> preservam a demo/fallback local (DD10): auth/TLS/Key Vault são **opt-in por variável de ambiente**.

| Req | Item | Estado | Evidência |
|-----|------|--------|-----------|
| F7-01 | Autenticação e restrição de acesso aos serviços | ✅ **Implementado** | `backend/src/middleware/auth.js` + `ai-service/app/api/seguranca.py` (`x-api-key`); cliente envia a credencial (`backend/src/servicos/inferencia.js`) |
| F7-02 | TLS/HTTPS em trânsito | ✅ **Implementado** | `frontend/nginx.tls.conf` + `docker-compose.tls.yml` + `scripts/gerar-cert-dev.sh` (HSTS); Node↔Python aceita `https://`; fallback HTTP (DD10) |
| F7-03 | Auditoria de acesso (quem/quando/qual caso) | ✅ **Implementado** | tabela `auditoria` (`backend/src/db/index.js`/`repositorios.js`) + registro em `rotas/casos.js` e `rotas/analisar.js` |
| F7-04 | Política de retenção/expiração | ✅ **Implementado** | `backend/src/servicos/retencao.js` + `scripts/retencao.js` (`npm run retencao`); TTL `RETENTION_DAYS` |
| F7-05 | Pseudonimização reforçada (`case_id` + PII) | ✅ **Implementado** | `backend/src/seguranca/pseudonimizacao.js` (UUID validado + `pacienteMinimo`); `rotas/analisar.js` |
| F7-06 | Hardening HTTP (helmet/CORS/headers/upload) | ✅ **Implementado** | `helmet` + `backend/src/middleware/cors.js` + headers em `frontend/nginx.conf` + `fileFilter` em `rotas/analisar.js` |
| F7-07 | Segredos via Azure Key Vault (opcional) | ✅ **Implementado** | `backend/src/seguranca/segredos.js` + `backend/src/bootstrap.js` (fallback `.env`) |
| F7-08 | Conformidade no CI + documentação sincronizada | ✅ **Implementado** | `scripts/check_conformidade.py` + job `conformidade` no CI; checklist `docs/07 §6` e §5 do relatório atualizados; disclaimer realçado no README |

> **Permanece ação humana / bloqueado por ambiente:** provisionar **RBAC/Private Endpoint reais na Azure**
> (depende de conta — F5-03) e **gravar o vídeo** demonstrando os controles (DD-F4-5).

## Resultado esperado (Definition of Done)

- [x] **Auth ativa**: `ai-service` e rotas de dados do backend recusam chamadas sem credencial (quando
      configurada); `/health` e `/ready` seguem públicos — F7-01.
- [x] **TLS na borda** e Node↔Python por `https://` quando configurado, com HSTS e **fallback HTTP** em dev —
      F7-02.
- [x] **Trilha de auditoria** persistida (quem/quando/caso/ação) sem conteúdo clínico sensível — F7-03.
- [x] **Retenção** com TTL configurável e rotina de limpeza (banco + storage), auditada — F7-04.
- [x] **Pseudonimização**: `case_id` opaco/validado e payload ao `ai-service` sem PII desnecessária — F7-05.
- [x] **Hardening**: helmet, CORS por allowlist (REST + socket.io), security headers no `nginx` e validação de
      upload — F7-06.
- [x] **Segredos**: Key Vault opcional com fallback `.env` — F7-07.
- [x] **Conformidade**: CI falha ao commitar segredo/dado real; checklist `docs/07 §6` e §5 do relatório
      atualizados; disclaimer realçado no README — F7-08.
- [x] **Gate verde** preservado (`ruff`+`pytest` / `eslint`+`jest`+`vitest`) e `docker compose up`
      reprodutível, **sem regressão** das Fases 2–6 e **sem reabrir** o contrato de API.

---

## Tarefas (visão macro)

> Quebra atômica (com dependências, "done when" e gate por tarefa) virá no `tasks.md` da feature **após** a
> confirmação do escopo e a fase de **Design**. Visão macro abaixo, em ordem sugerida de caminho crítico.

### Tarefa 7.1 — Autenticação e restrição de acesso (F7-01)
- Adicionar **dependência de credencial de serviço** (API key por env) no `ai-service`
  ([`app/api/main.py`](../ai-service/app/api/main.py)) e middleware de auth no backend
  ([`backend/src/app.js`](../backend/src/app.js)), preservando `/health` e `/ready` públicos.
- Backend envia a credencial nas chamadas ao `ai-service` ([`servicos/inferencia.js`](../backend/src/servicos/inferencia.js)).
- Flag de dev (auth off) com **default seguro em produção**.

### Tarefa 7.2 — TLS/HTTPS em trânsito (F7-02)
- Terminação **TLS no `nginx`** ([`frontend/nginx.conf`](../frontend/nginx.conf)) + HSTS; aceitar
  `AI_SERVICE_URL=https://` no backend; ajustar [`docker-compose.yml`](../docker-compose.yml).
- **Fallback HTTP** documentado quando não houver certificado (DD10).

### Tarefa 7.3 — Auditoria de acesso (F7-03)
- Tabela `auditoria` (SQLite) + registro nas leituras (`GET /casos`, `/casos/:id`, `/casos/:id/relatorio`) e
  na análise (`POST /analisar`), com **identidade + `case_id` + ação + timestamp**, sem conteúdo clínico.
- Estender o logger ([`backend/src/logger.js`](../backend/src/logger.js)) e os repositórios
  ([`db/repositorios.js`](../backend/src/db/repositorios.js)).

### Tarefa 7.4 — Política de retenção/expiração (F7-04)
- **TTL por env** + script/comando de limpeza reusando o caminho de remoção existente
  ([`rotas/pacientes.js`](../backend/src/rotas/pacientes.js) → cascade + storage), removendo o **blob** no modo
  Azure; ação auditada (7.3).

### Tarefa 7.5 — Pseudonimização reforçada (F7-05)
- Forçar/validar `case_id` opaco (UUID) em `POST /analisar` ([`rotas/analisar.js`](../backend/src/rotas/analisar.js));
  **omitir `primeiro_nome`** no payload ao `ai-service` ([`servicos/inferencia.js`](../backend/src/servicos/inferencia.js)),
  mantendo o nome só no backend.

### Tarefa 7.6 — Hardening HTTP (F7-06)
- `helmet` no Express + CORS por **allowlist** (REST e `socket.io` em [`server.js`](../backend/src/server.js));
  security headers no `nginx`; **validação de MIME/extensão** no upload ([`rotas/analisar.js`](../backend/src/rotas/analisar.js)).

### Tarefa 7.7 — Segredos via Key Vault, opcional (F7-07)
- Carregar segredos do **Azure Key Vault** quando `AZURE_KEY_VAULT_URL` existir, com **fallback `.env`**;
  falhar de forma explícita se faltar segredo em produção.

### Tarefa 7.8 — Conformidade no CI + docs (F7-08)
- Job no [`ci.yml`](../.github/workflows/ci.yml) que **falha** ao commitar `.env`/dado real e confirma o
  `.gitignore`; atualizar o **checklist** ([`07-privacidade-e-seguranca.md §6`](07-privacidade-e-seguranca.md)),
  a **§5** do [`relatorio-tecnico.md`](relatorio-tecnico.md) e **realçar o disclaimer** no
  [`README.md`](../README.md).

---

## Caminho crítico e paralelização

- **Caminho crítico:** 7.1 (auth — base dos demais controles) → 7.3 (auditoria depende da identidade do
  chamador) → 7.8 (docs/CI refletem o implementado).
- **Paralelizável:** 7.2 (TLS/nginx), 7.4 (retenção), 7.5 (pseudonimização) e 7.6 (hardening) tocam pontos
  independentes (infra, limpeza, payload, headers) e podem correr em paralelo após 7.1.
- **Sem certificado/Key Vault/Azure?** 7.2 degrada para **HTTP local**, 7.7 cai no **`.env`** e a parte Azure
  da 7.4 documenta a limpeza do blob — tudo sem quebrar o `docker compose up` (DD10).

## Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Auth quebrar a demo local e os testes | Flag de dev (auth off por padrão **local**), default **seguro em produção**; injeção de credencial nos testes |
| TLS exigir certificado/infra | `nginx` com self-signed em dev; cert/ingress gerenciado em produção; fallback HTTP documentado (DD10) |
| Trilha de auditoria vazar dado sensível | Registrar **identificadores** (`case_id`, ação, usuário), **nunca** conteúdo clínico |
| Retenção apagar dado em uso | TTL conservador + no-op sem TTL; remover só itens fora do período; ação auditada |
| Regressão das Fases 2–6 / contrato de API | Gate verde obrigatório; **não** reabrir o contrato; controles adicionados **em volta** dos serviços |
| RBAC/Private Endpoint reais na Azure | **Fora de escopo** (ação humana/infra — F5-03); código Azure-ready e documentado em [`deploy-azure.md`](deploy-azure.md) |
| Escopo divergente ("outro 8IADT") | Confirmar com o grupo **antes** do Design (`AGENTS.md`) |
