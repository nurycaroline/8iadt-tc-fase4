# Fase 7 — Privacidade e Segurança (LGPD) — Especificação

> **Status: PLANEJAMENTO (Specify).** Especificação gerada a partir do requisito
> [`docs/07-privacidade-e-seguranca.md`](../../../docs/07-privacidade-e-seguranca.md) (componente próprio
> citado no PDF do Tech Challenge — "os mais altos padrões de privacidade e segurança para dados sensíveis"),
> seguindo a skill [`tlc-spec-driven`](../../../.cursor/skills/tlc-spec-driven/SKILL.md). Visão macro em
> [`docs/10-fase7-privacidade-e-seguranca.md`](../../../docs/10-fase7-privacidade-e-seguranca.md).
>
> ⚠️ **Rascunho de planejamento (escopo a confirmar — `AGENTS.md`).** As Fases 1–4 já entregam o Tech
> Challenge; a documentação de LGPD (disclaimer + seção §5 do relatório técnico) **já existe**. **Todo
> requisito desta fase rastreia uma lacuna real entre o que o `docs/07` descreve e o que o código
> implementa — nenhum foi inventado** (mesmo espírito da Fase 6). As
> [Decisões a confirmar](#decisões-a-confirmar-com-o-grupo) trazem **defaults propostos**, mas o **Design** e o
> **Tasks** (quebra atômica) só vêm **após** a confirmação do escopo pelo grupo.

## Problem Statement

O `docs/07-privacidade-e-seguranca.md` define os controles de privacidade/segurança exigidos para **dados
sensíveis de saúde** (LGPD, Lei 13.709/2018): minimização/pseudonimização, TLS em trânsito, criptografia em
repouso, segredos fora do Git, **RBAC/restrição de acesso**, **auditoria de acesso**, **retenção/expiração** e
disclaimer ético. Hoje a documentação está madura (disclaimer no README e seção §5 do
[`relatorio-tecnico.md`](../../../docs/relatorio-tecnico.md)), mas **vários controles do `docs/07` são
descritos como prática e não estão implementados no código** — a seção §5 do relatório é, em parte,
**aspiracional**.

A auditoria do código (backend Node, `ai-service` FastAPI, frontend, infra) revelou **lacunas concretas**:

1. **Sem autenticação/autorização** em nenhuma camada. O `ai-service` expõe
   [`POST /inferencia`](../../../ai-service/app/api/main.py) sem `Depends`/API key e fica acessível na rede do
   compose ([`docker-compose.yml`](../../../docker-compose.yml) publica `8000:8000`); as rotas Express
   (`/pacientes`, `/analisar`, `/casos`) também não têm middleware de auth
   ([`backend/src/app.js`](../../../backend/src/app.js)). O `docs/07 §2` exige **"restringir origem das
   chamadas ao serviço Python (não expor publicamente sem auth)"** e **RBAC/controle de acesso**.
2. **Tráfego interno em texto claro.** A chamada Node↔Python usa `http://`
   ([`config.aiServiceUrl`](../../../backend/src/config.js)); o `nginx` do frontend escuta `:80` sem TLS; o
   compose não termina TLS. O `docs/07 §2` exige **"HTTPS/TLS em todas as chamadas"**.
3. **Auditoria de processamento, não de acesso.** O logger ([`backend/src/logger.js`](../../../backend/src/logger.js),
   `pino-http`) anexa `case_id`, mas registra **processamento** — não **quem acessou qual caso e quando**
   (sem identidade do chamador nos `GET /casos`, `/casos/:id`, `/relatorio`) nem trilha persistida. O
   `docs/07 §2` exige **"log de quem acessou qual caso e quando"**.
4. **Sem política de retenção/expiração.** Existe `DELETE /pacientes/:id`
   ([`backend/src/rotas/pacientes.js`](../../../backend/src/rotas/pacientes.js), cascade no banco), mas
   **nenhum TTL, job ou rotina automática** de limpeza. O `docs/07 §2` exige **"política de
   expiração/limpeza de dados após o uso"**.
5. **Pseudonimização parcial.** O `case_id`/`paciente_id` usam `randomUUID()` na criação
   ([`backend/src/db/repositorios.js`](../../../backend/src/db/repositorios.js)), mas `POST /analisar` aceita
   `case_id` **legível** vindo do corpo, e o **`primeiro_nome` (PII)** é enviado no payload ao `ai-service`
   ([`RequisicaoInferencia`](../../../ai-service/app/api/modelos.py)) mesmo sem ser usado na decisão de risco.
   O `docs/07 §1` pede **minimização** e **`case_id` opaco**.
6. **Hardening HTTP ausente.** O Express **não usa `helmet`**; o `socket.io` usa `cors: { origin: '*' }`
   ([`backend/src/server.js`](../../../backend/src/server.js)); o `nginx` não envia security headers; os
   uploads (`multer`, limite de 50 MB em [`analisar.js`](../../../backend/src/rotas/analisar.js)) **não
   filtram MIME/extensão**. São controles de **acesso/rede** do `docs/07 §2`.

O **disclaimer ético** (`docs/07 §5`) e a **seção LGPD do relatório** (`docs/07 §6`) **já existem** — a Fase 7
**não os reinventa**; apenas (a) **fecha a lacuna** entre os controles descritos e o código e (b) deixa a
seção §5 deixar de ser aspiracional, atualizando o **checklist de conformidade** (`docs/07 §6`).

## Goals

- [ ] **Autenticar e restringir o acesso** aos serviços: o `ai-service` (FastAPI) e as rotas do backend
      (Express) SHALL exigir credencial de serviço; o `ai-service` SHALL deixar de ser publicamente acessível
      sem auth (`docs/07 §2` — Acesso/Rede).
- [ ] **Cifrar o tráfego em trânsito** na stack conteinerizada (terminação TLS/HTTPS), com fallback HTTP
      apenas em dev/local sem quebrar (`docs/07 §2` — Em trânsito).
- [ ] **Trilha de auditoria de acesso** (quem/quando/qual caso) nas leituras de caso/relatório, persistida e
      consultável (`docs/07 §2` — Auditoria).
- [ ] **Política de retenção/expiração** configurável (TTL) com rotina de limpeza de casos e artefatos
      (`docs/07 §2` — Retenção).
- [ ] **Pseudonimização reforçada**: `case_id` sempre opaco e validado; **minimizar a PII** enviada ao
      `ai-service` (não trafegar `primeiro_nome` quando não for necessário à decisão) (`docs/07 §1`).
- [ ] **Hardening HTTP**: `helmet`, CORS por allowlist (REST + socket.io), security headers no `nginx` e
      validação de MIME/tipo nos uploads (`docs/07 §2`).
- [ ] **Sincronizar documentação e checklist**: atualizar o **checklist de conformidade** (`docs/07 §6`) e a
      seção §5 do relatório técnico para refletir o que passou a ser **implementado** (não aspiracional);
      manter/realçar o disclaimer ético.
- [ ] **Manter o gate verde** (`ruff`+`pytest` / `eslint`+`jest`+`vitest`) e a reprodutibilidade por
      `docker compose up`, **sem regressão** das Fases 2–6 e **sem reabrir** o contrato de API.

## Out of Scope

Explicitamente excluído para evitar scope creep. Cada item é ação humana, depende de ambiente/infra externa,
ou é decisão de arquitetura já fechada.

| Item | Motivo / Onde entra |
| --- | --- |
| **Provisionar RBAC/Private Endpoint reais na Azure** | **Ação humana/infra** (conta + portal); bloqueado por ambiente como na Fase 5 (F5-03). Documentado em [`deploy-azure.md`](../../../docs/deploy-azure.md); o código fica Azure-ready |
| **IAM completo / cadastro de usuários / SSO / login de UI** | Fora do escopo acadêmico de **apoio à decisão**; a Fase 7 usa **credencial de serviço** (token), não gestão de identidades |
| **Anonimização irreversível** dos dados | O caso clínico **precisa** correlacionar modalidades da mesma paciente; usamos **pseudonimização** (`case_id` opaco), não anonimização que quebre a fusão |
| **Criptografia em repouso do storage local** (campo a campo no SQLite) | O modo `local` é **só demonstração com dados sintéticos** (sem dados reais — `docs/07 §3/§4`); SSE real fica no Blob (default Azure) |
| **Trocar o motor de fusão, o contrato de API ou o relatório** | Decisões fechadas (S12, contrato estável, Fase 6); a Fase 7 adiciona controles **em volta**, sem reabri-los |
| **Gravar/publicar o vídeo** demonstrando os controles | **Ação humana** do grupo (DD-F4-5) |

---

## User Stories

### P1: Autenticação e restrição de acesso aos serviços ⭐ MVP

**User Story**: Como responsável pela solução, quero que o `ai-service` e as rotas do backend **exijam uma
credencial de serviço**, para que dados sensíveis de saúde não fiquem acessíveis sem autorização — cumprindo
o `docs/07 §2` ("não expor publicamente sem auth").

**Why P1**: É a maior lacuna de LGPD: hoje qualquer um na rede chama `POST /inferencia` ou lê `GET /casos` sem
credencial. Sem isso, os demais controles (TLS, auditoria) protegem um endpoint ainda aberto.

**Acceptance Criteria**:

1. WHEN uma requisição chega a `POST /inferencia` (FastAPI) **sem** credencial válida THEN o serviço SHALL
   responder **401/403** e **não** processar o caso.
2. WHEN o backend (Express) chama o `ai-service` THEN ele SHALL enviar a credencial de serviço configurada por
   variável de ambiente (segredo fora do Git).
3. WHEN uma requisição chega às rotas que expõem dados de caso/paciente (`/pacientes`, `/analisar`, `/casos`,
   `/casos/:id`, `/casos/:id/relatorio`) **sem** credencial válida THEN o backend SHALL responder **401/403**.
4. WHEN a autenticação está **desabilitada por flag de dev** (default seguro em produção) THEN o
   comportamento atual SHALL ser preservado para a demo local, sem expor isso por padrão em produção.
5. WHEN `/health` e `/ready` são chamados THEN eles SHALL permanecer **públicos** (probes), sem vazar dados
   sensíveis.

**Independent Test**: Chamar `POST /inferencia` e `GET /casos` sem credencial → 401/403; com a credencial
correta → 200. Cobertura por testes (`pytest` no FastAPI; `jest` no Express).

---

### P1: TLS/HTTPS em trânsito ⭐ MVP

**User Story**: Como operador, quero que **todas as chamadas** (cliente↔backend, Node↔Python) trafeguem por
**HTTPS/TLS** na stack conteinerizada, para proteger dados sensíveis em trânsito (`docs/07 §2` — Em trânsito).

**Why P1**: O `docs/07` exige TLS "em todas as chamadas"; hoje a stack é HTTP puro. É controle de base sobre o
qual auth e auditoria se apoiam.

**Acceptance Criteria**:

1. WHEN a stack sobe conteinerizada THEN a borda (ex.: `nginx`) SHALL servir **HTTPS** e o backend SHALL poder
   falar com o `ai-service` por **TLS** quando `AI_SERVICE_URL` usar `https://`.
2. WHEN o cliente acessa por HTTPS THEN a resposta SHALL incluir **HSTS** (cabeçalho de segurança de
   transporte) na borda.
3. WHEN não há certificado disponível (dev/local) THEN a stack SHALL **degradar para HTTP** documentado, sem
   quebrar o `docker compose up` (mesma filosofia de fallback do projeto — DD10).
4. WHEN o deploy real na Azure ocorrer (ação humana/infra) THEN a configuração SHALL aceitar o
   certificado/ingress gerenciado sem mudança de código (Azure-ready).

**Independent Test**: Subir a stack com TLS habilitado e validar handshake HTTPS na borda + chamada
`https://` Node↔Python; subir sem certificado e confirmar fallback HTTP sem erro.

---

### P1: Auditoria de acesso (quem/quando/qual caso) ⭐ MVP

**User Story**: Como encarregado de dados (DPO), quero uma **trilha de auditoria** que registre **quem**
acessou **qual caso** e **quando**, para atender à rastreabilidade da LGPD (`docs/07 §2` — Auditoria).

**Why P1**: O `docs/07` lista auditoria como controle explícito; hoje os logs são de **processamento**, sem
identidade do chamador nem trilha de **acesso** persistida.

**Acceptance Criteria**:

1. WHEN um caso/relatório é **lido** (`GET /casos`, `GET /casos/:id`, `GET /casos/:id/relatorio`) THEN o
   sistema SHALL registrar um evento de auditoria com **identidade do chamador**, **`case_id`** (quando
   aplicável), **ação** e **timestamp**.
2. WHEN um caso é **criado/analisado** (`POST /analisar`) THEN o evento SHALL ser auditado com a mesma
   estrutura.
3. WHEN o evento é registrado THEN ele SHALL ser **persistido** (não apenas em stdout) e consultável, sem
   gravar conteúdo clínico sensível na própria trilha (registrar o identificador, não o dado).
4. WHEN a identidade do chamador não está disponível (auth desabilitada em dev) THEN o evento SHALL registrar
   um marcador explícito (ex.: `anonimo`/`dev`) sem quebrar.

**Independent Test**: Executar leituras/escritas autenticadas e conferir que a trilha registra
identidade+`case_id`+ação+timestamp; conferir que conteúdo clínico não é copiado para a trilha.

---

### P2: Política de retenção e expiração de dados

**User Story**: Como DPO, quero uma **política de retenção** com expiração automática dos dados após o uso,
para cumprir a **minimização temporal** do `docs/07 §2` (Retenção).

**Why P2**: É controle exigido pelo `docs/07`, mas o `DELETE` manual já existe; a automação é incremento de
conformidade, não pré-requisito dos controles P1.

**Acceptance Criteria**:

1. WHEN um TTL de retenção está configurado (por env) THEN o sistema SHALL fornecer uma **rotina de limpeza**
   (script/comando) que remove casos e artefatos cujo `timestamp` excede o TTL, reusando o caminho de remoção
   existente (banco em cascade + storage).
2. WHEN a rotina roda THEN ela SHALL **não** remover casos dentro do período de retenção e SHALL registrar a
   ação na trilha de auditoria.
3. WHEN o storage é Azure THEN a limpeza SHALL remover o **blob** correspondente (não só a URL/SAS, que já
   expira).
4. WHEN o TTL não está configurado THEN o comportamento atual SHALL ser preservado (sem expiração automática),
   documentando o default.

**Independent Test**: Semear casos antigos/novos, rodar a rotina com um TTL e confirmar que só os expirados
saem (banco + storage), com evento de auditoria.

---

### P2: Pseudonimização reforçada (case_id opaco + minimização de PII)

**User Story**: Como DPO, quero que o `case_id` seja **sempre opaco** e que a **PII** (nome) **não trafegue**
ao motor de IA quando não for necessária à decisão, para cumprir a minimização/pseudonimização do
`docs/07 §1`.

**Why P2**: Reduz a superfície de PII; o `randomUUID()` já existe na criação, então o esforço é validar/forçar
opacidade e enxugar o payload — incremento sobre uma base já razoável.

**Acceptance Criteria**:

1. WHEN um caso é criado/analisado THEN o `case_id`/`paciente_id` SHALL ser **opaco** (UUID) e, se vier do
   corpo, SHALL ser **validado** quanto ao formato (rejeitar identificadores legíveis em produção).
2. WHEN o backend chama o `ai-service` THEN o payload SHALL **omitir o `primeiro_nome`** (e qualquer PII não
   usada na decisão de risco), mantendo o `ai-service` funcional (o campo já é opcional em
   [`Paciente`](../../../ai-service/app/api/modelos.py)).
3. WHEN o relatório é gerado THEN o nome SHALL ser usado apenas no **backend** (onde o caso é exibido à
   equipe), não propagado a logs/trilha de auditoria.
4. WHEN dados sintéticos versionados (`data/casos/*.json`) usam nomes fictícios THEN isso SHALL ser mantido
   como **estratégia de privacidade** (`docs/07 §4`), sem dados reais.

**Independent Test**: Analisar um caso e inspecionar o payload enviado ao `ai-service` (sem `primeiro_nome`);
enviar `case_id` legível em modo "produção" e confirmar rejeição/validação.

---

### P2: Hardening HTTP (helmet, CORS, headers, upload)

**User Story**: Como engenheiro de segurança, quero **cabeçalhos de segurança**, **CORS restrito** e
**validação de upload**, para reduzir a superfície de ataque sobre os endpoints que servem dados sensíveis
(`docs/07 §2` — Acesso/Rede).

**Why P2**: Hardening padrão de aplicações web; complementa os P1 sem ser pré-requisito deles.

**Acceptance Criteria**:

1. WHEN o Express responde THEN ele SHALL aplicar `helmet` (CSP/headers padrão) e o `nginx` de produção SHALL
   enviar security headers (ex.: `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`).
2. WHEN o CORS é avaliado (REST e `socket.io`) THEN a origem SHALL vir de uma **allowlist** por env, deixando
   de ser `*` em produção.
3. WHEN um upload chega a `POST /analisar` THEN o backend SHALL **validar MIME/extensão** (vídeo/áudio/CSV/
   imagem esperados) além do limite de tamanho já existente, rejeitando tipos inesperados.
4. WHEN um header/ origem inválida é recebido THEN a resposta SHALL ser segura por padrão (negar), sem vazar
   detalhes internos.

**Independent Test**: Inspecionar headers da resposta (helmet/nginx); chamar de origem fora da allowlist e
confirmar bloqueio; subir upload com MIME inválido e confirmar rejeição.

---

### P3: Gestão de segredos com Azure Key Vault (opcional)

**User Story**: Como operador na nuvem, quero **carregar segredos do Azure Key Vault** (mantendo o `.env`
como fallback), para cumprir o "Key Vault **ou** `.env`" do `docs/07 §2` com a opção mais robusta em produção.

**Why P3**: O `.env` + `.gitignore` **já satisfaz** o `docs/07 §2` ("Key Vault **ou** `.env`"); o Key Vault é
um reforço de produção, não uma lacuna obrigatória.

**Acceptance Criteria**:

1. WHEN `AZURE_KEY_VAULT_URL` está configurado THEN os segredos (connection string, credencial de serviço)
   SHALL ser lidos do Key Vault na inicialização.
2. WHEN o Key Vault **não** está configurado THEN o sistema SHALL cair no `.env`/variáveis de ambiente atuais
   (fallback), sem quebrar.
3. WHEN um segredo não é encontrado em nenhuma fonte THEN o serviço SHALL falhar de forma **explícita e
   segura** (não iniciar com segredo vazio em produção).

**Independent Test**: Configurar um Key Vault (ou mock) e confirmar leitura; remover a config e confirmar
fallback para `.env`.

---

### P3: Conformidade verificável (CI) + documentação sincronizada

**User Story**: Como mantenedor, quero **verificação automática** contra vazamento de dados/segredos e o
**checklist de conformidade** atualizado, para que o `docs/07 §6` deixe de ser aspiracional e a §5 do
relatório reflita o implementado.

**Why P3**: Qualidade/rastreabilidade; depende de P1/P2 estarem prontos para a documentação refletir a
realidade.

**Acceptance Criteria**:

1. WHEN o CI ([`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml)) roda THEN ele SHALL incluir uma
   verificação que **falha** se `.env` (com segredos) ou dados sensíveis forem commitados, e que confirma que
   `data/` (exceto metadados sintéticos permitidos) está ignorado.
2. WHEN a Fase 7 conclui um controle THEN o **checklist de conformidade** (`docs/07 §6`) e a seção §5 de
   [`relatorio-tecnico.md`](../../../docs/relatorio-tecnico.md) SHALL ser atualizados para `implementado`
   (sem prometer o que não foi feito — `AGENTS.md`).
3. WHEN o README é lido THEN o **disclaimer ético** SHALL estar **visível** (não apenas uma linha ao final),
   conforme `docs/07 §5`.

**Independent Test**: Rodar o job de conformidade do CI (verde no estado limpo; vermelho ao simular um
`.env`/dado real); revisar o checklist e a §5 atualizados.

---

## Edge Cases

- WHEN não há **certificado TLS** (dev/local) THEN a stack SHALL degradar para HTTP documentado sem quebrar o
  `docker compose up` (DD10).
- WHEN a **credencial de serviço** não está configurada em produção THEN o serviço SHALL **recusar iniciar**
  (ou negar todas as chamadas), em vez de abrir sem auth silenciosamente.
- WHEN a **auth está desabilitada por flag de dev** THEN a auditoria SHALL registrar `anonimo/dev` e a flag
  SHALL ser **off por padrão** em produção.
- WHEN a **rotina de retenção** roda sem TTL configurado THEN ela SHALL **não apagar nada** (no-op
  documentado).
- WHEN o **storage é local** (fallback) THEN a limpeza/retenção SHALL operar sobre os arquivos locais e a
  auditoria sobre o banco, sem assumir endpoints Azure inexistentes.
- WHEN um **upload** tem MIME inesperado ou excede o limite THEN o backend SHALL rejeitar com erro claro, sem
  persistir o artefato.
- WHEN o **Key Vault** está configurado mas indisponível THEN o sistema SHALL falhar de forma explícita
  (não cair silenciosamente para segredo vazio em produção).

---

## Requirement Traceability

| Requirement ID | Story | Fonte (lacuna real) | Phase | Status |
| --- | --- | --- | --- | --- |
| F7-01 | P1: Autenticação e restrição de acesso | `docs/07 §2` (Acesso/Rede) vs. `ai-service`/Express sem auth | Pending | Pending |
| F7-02 | P1: TLS/HTTPS em trânsito | `docs/07 §2` (Em trânsito) vs. stack HTTP puro | Pending | Pending |
| F7-03 | P1: Auditoria de acesso (quem/quando/caso) | `docs/07 §2` (Auditoria) vs. logs só de processamento | Pending | Pending |
| F7-04 | P2: Política de retenção/expiração | `docs/07 §2` (Retenção) vs. sem TTL/limpeza automática | Pending | Pending |
| F7-05 | P2: Pseudonimização reforçada (case_id + PII) | `docs/07 §1` vs. `case_id` legível + `primeiro_nome` no payload | Pending | Pending |
| F7-06 | P2: Hardening HTTP (helmet/CORS/headers/upload) | `docs/07 §2` vs. sem helmet, CORS `*`, sem filtro de MIME | Pending | Pending |
| F7-07 | P3: Segredos via Azure Key Vault (opcional) | `docs/07 §2` (Segredos) — reforço sobre `.env` já válido | Pending | Pending |
| F7-08 | P3: Conformidade no CI + docs sincronizadas | `docs/07 §6` (checklist) + §5 aspiracional | Pending | Pending |

**ID format:** `F7-[NUMBER]` (Fase 7).
**Status values:** Pending → In Design → In Tasks → Implementing → Verified | Bloqueado (ambiente).
**Coverage:** 8 requisitos — **0 mapeados a tarefas** ⚠️ (Tasks vem após Design e confirmação do escopo).

> **Já satisfeito pelo código atual (não vira requisito da Fase 7):** SAS token **com expiração** já existe
> ([`azureBlob.js`](../../../backend/src/storage/azureBlob.js) / [`storage_azure.py`](../../../ai-service/app/storage_azure.py),
> `AZURE_SAS_EXPIRY_MINUTES`); `.env`/`data/` no [`.gitignore`](../../../.gitignore); **disclaimer ético** no
> README e relatório; **seção §5 LGPD** no [`relatorio-tecnico.md`](../../../docs/relatorio-tecnico.md);
> **dados sintéticos** ([`scripts/data_prep/caso_sintetico.py`](../../../scripts/data_prep/caso_sintetico.py)).
> A Fase 7 **realça/atualiza** esses itens (F7-08), mas não os recria.

---

## Decisões a confirmar com o grupo

> Conforme `AGENTS.md` (Princípio 1 — não presumir). Como o pedido foi **"planeje o desenvolvimento"**, estas
> escolhas estão como **defaults propostos** e devem ser **confirmadas antes do Design**.

1. **Esta é a "Fase 7" pretendida?** Default: **Privacidade e Segurança (LGPD)**, fechando a lacuna entre o
   [`docs/07`](../../../docs/07-privacidade-e-seguranca.md) e o código. Se "Fase 7" significar **outro desafio
   8IADT** com enunciado próprio, fornecer o PDF para reescrever a spec.
2. **Modelo de autenticação (F7-01):** proposta = **credencial de serviço** (API key estática por env, header
   `X-API-Key`) entre cliente↔backend↔`ai-service`, com **identidade do chamador** num header dedicado
   (ex.: `X-User-Id`) para a auditoria. Alternativa: JWT/OAuth (maior esforço, fora do escopo acadêmico).
3. **Terminação TLS (F7-02):** proposta = **`nginx` da borda** com certificado **autoassinado em dev** e
   cert/ingress gerenciado em produção (Azure), mantendo **fallback HTTP** local. Alternativa: TLS só no
   ingress da nuvem.
4. **Trilha de auditoria (F7-03):** proposta = **tabela no SQLite** (`auditoria`) + log estruturado, sem
   copiar conteúdo clínico (só identificadores). Alternativa: arquivo append-only/serviço externo.
5. **Retenção (F7-04):** proposta = **TTL por env** (ex.: default 90 dias) + **script/comando** de limpeza
   acionável (e cron documentado no deploy). Alternativa: job agendado embutido.
6. **Minimização de PII (F7-05):** proposta = **omitir `primeiro_nome`** no payload ao `ai-service` (o campo é
   opcional e não usado na decisão) e **forçar `case_id` opaco** em produção (validação de formato).
7. **Key Vault (F7-07):** proposta = **P3/opcional** — `.env` já satisfaz o `docs/07 §2` ("Key Vault **ou**
   `.env`"); Key Vault como reforço de produção com fallback.
8. **Profundidade da Fase 7:** dado o escopo cruzado (backend + `ai-service` + frontend/`nginx` + infra + CI),
   esta é uma feature **Large**; após a confirmação, seguir com **Design** (decisões técnicas e impacto por
   componente) e **Tasks** (quebra atômica com dependências e gate por tarefa).

---

## Success Criteria

Como saberemos que a Fase 7 está pronta:

- [ ] **Auth ativa**: `ai-service` e rotas de dados do backend recusam chamadas sem credencial; `/health` e
      `/ready` seguem públicos — F7-01.
- [ ] **TLS na borda** e Node↔Python por `https://` quando configurado, com HSTS e fallback HTTP em dev —
      F7-02.
- [ ] **Trilha de auditoria** persistida (quem/quando/caso/ação) nas leituras e na análise, sem conteúdo
      clínico sensível — F7-03.
- [ ] **Retenção** com TTL configurável e rotina de limpeza (banco + storage), auditada — F7-04.
- [ ] **Pseudonimização**: `case_id` opaco/validado e payload ao `ai-service` sem PII desnecessária — F7-05.
- [ ] **Hardening**: helmet, CORS por allowlist (REST + socket.io), security headers no `nginx` e validação de
      upload — F7-06.
- [ ] **Segredos**: Key Vault opcional com fallback `.env` (ou decisão de manter só `.env`) — F7-07.
- [ ] **Conformidade**: CI falha ao commitar segredo/dado real; checklist `docs/07 §6` e §5 do relatório
      atualizados; disclaimer realçado no README — F7-08.
- [ ] **Gate verde** preservado (`ruff`+`pytest` / `eslint`+`jest`+`vitest`) e `docker compose up`
      reprodutível, **sem regressão** das Fases 2–6 e **sem reabrir** o contrato de API.
- [ ] **STATE** e **docs** atualizados (Fase 7 registrada; decisões confirmadas).

> **Itens que permanecem ação humana / bloqueados por ambiente** (não bloqueiam o planejamento): provisionar
> **RBAC/Private Endpoint reais na Azure** (depende de conta — F5-03) e **gravar o vídeo** (DD-F4-5).
