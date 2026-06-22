# Fase 5 — Produção, Escala e Robustez — Especificação

> **Status: RASCUNHO / planejamento.** Documento gerado a partir dos itens **em aberto** do
> [`docs/05-checklist-entrega.md`](../../../docs/05-checklist-entrega.md) e dos `todos`/`ideias adiadas`
> registrados em [`.specs/project/STATE.md`](../../project/STATE.md), seguindo a skill
> [`tlc-spec-driven`](../../../.cursor/skills/tlc-spec-driven/SKILL.md) (fase **Specify**).
>
> ⚠️ **Decisão de escopo a confirmar (`AGENTS.md` — em caso de dúvida, perguntar):** as Fases 1–4 do
> projeto já estão **implementadas** e cobrem o Tech Challenge atual. **Não existia uma "Fase 5" definida**
> no plano. Esta especificação propõe a Fase 5 como **"Produção, Escala e Robustez"**: pegar a solução
> **demo-grade** (que funciona ponta-a-ponta, mas com modalidades **degradadas** e nuvem em **fallback
> local**) e elevá-la a **produção**, fechando exatamente os itens que ficaram **abertos** no checklist e no
> STATE. **Todo requisito abaixo rastreia um item pendente real do repositório — nenhum foi inventado.**
> Antes de avançar para Design/Tasks, **confirmar com o grupo** a seção
> [Decisões a confirmar](#decisões-a-confirmar-com-o-grupo).

## Problem Statement

As Fases 1–4 entregaram a solução **funcionando ponta-a-ponta** com **gate verde**, mas em estado
**demo-grade**: (1) o detector de **cicatriz** é um **smoke** (6 imagens) que **não detecta acima do
limiar** de confiança, então o `caso_alto` fecha **MÉDIO** (decidido por vitais+texto) em vez de **ALTO**
ponta a ponta; (2) as modalidades de **áudio** e **fisioterapia** **degradam** (DD10) por falta de dados de
obtenção manual, sem métricas reais; (3) a integração com a **nuvem (Azure)** existe no código, mas a demo
roda em **fallback local** — não há deploy real validado; (4) o front-end é um **cliente mínimo** (HTML +
socket.io), não o **dashboard** de monitoramento descrito em [`docs/frontend.md`](../../../docs/frontend.md).

Enquanto esses itens permanecerem abertos, a solução **prova o conceito** mas **não está pronta para
produção** nem demonstra o cenário-alvo (infecção puerperal disparando **ALTO** com evidência de vídeo
real). A Fase 5 **fecha essa lacuna**: treina/escala os modelos com dados reais, completa as modalidades
degradadas, faz o **deploy real na Azure** (mantendo o fallback) e entrega o **dashboard de produção** —
sem reabrir as decisões de arquitetura já tomadas (S1–S25).

## Goals

- [ ] **Escalar o detector de cicatriz (YOLOv8)** com dataset ampliado e treino em **GPU/Colab** até
      **detectar acima do limiar**, de modo que o `caso_alto` feche **ALTO** ponta a ponta **sem mock/degradação**
      (fonte: STATE `todos`/`blockers`; checklist §Escopo "escalar p/ produção (STATE)").
- [ ] **Completar as modalidades degradadas (áudio + fisioterapia)**: obter as amostras (obtenção manual,
      Fase 1), rodar o **baseline completo** dessas modalidades e publicar **métricas reais** — eliminando a
      degradação documentada (DD10) (fonte: STATE `todos`/`blockers`; checklist §Técnico nota "áudio/fisioterapia
      degradam sem dados").
- [ ] **Deploy real na Azure** (Blob testado + serviço de IA + backend hospedados), **validado por smoke
      pós-deploy**, mantendo o **fallback local** como caminho de contingência (fonte: checklist
      §Pré-requisitos "Conta Azure ativa + Blob testado"; STATE decisão pendente; [`docs/deploy-azure.md`](../../../docs/deploy-azure.md)).
- [ ] **Dashboard React de produção** (`frontend/`) conforme [`docs/frontend.md`](../../../docs/frontend.md),
      substituindo o cliente mínimo, com a **tela de detalhe do caso** (o "money shot"), alerta em tempo real,
      gestão de pacientes e download do relatório (fonte: STATE `ideias adiadas`/out-of-scope da Fase 4; `docs/frontend.md`).
- [ ] **Reforçar sinais vitais** com **datasets sintéticos extras de pré-eclâmpsia** e **reavaliar as
      métricas** do modelo (fonte: STATE `ideias adiadas`).
- [ ] **Hardening para produção**: observabilidade (health/métricas além do `case_id` já logado),
      **CI/CD** que faz build+push das imagens e deploy, e revisão de segurança/LGPD do ambiente em nuvem
      (fonte: [`docs/qualidade-testes-ci.md`](../../../docs/qualidade-testes-ci.md), [`docs/07`](../../../docs/07-privacidade-e-seguranca.md)).
- [ ] **Manter o gate verde** dos dois serviços (ruff+pytest / eslint+jest) e a reprodutibilidade por
      `docker compose up` em **todas** as mudanças, sem regressão das Fases 2–4.

## Out of Scope

Explicitamente excluído para evitar scope creep. Cada item é ação humana, pertence a outra fase, ou é uma
decisão de arquitetura já fechada.

| Item                                                              | Motivo / Onde entra                                                                 |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Gravar/publicar o vídeo** e preencher **integrantes** no README | **Ação humana** do grupo (itens `[ ]` do checklist §Vídeo/§Antes de submeter) — a Fase 4 entregou roteiro + placeholders |
| **Trocar o motor de fusão** por modelo end-to-end                 | Decisão fechada (S12 — motor de regras explicável); Fase 5 **não** reabre arquitetura |
| **Login / permissionamento** no dashboard                         | Fora de escopo do projeto ([`docs/frontend.md §2`](../../../docs/frontend.md))      |
| **Reescrever** API/contrato entre serviços                        | Contrato estável ([`docs/contrato-api.md`](../../../docs/contrato-api.md)); Fase 5 consome o existente |
| **Dados reais de pacientes**                                      | LGPD — só dados públicos/sintéticos ([`docs/07`](../../../docs/07-privacidade-e-seguranca.md)) |
| Migrar **toda** a persistência para Postgres/Cosmos               | Opcional (S18); só se o deploy de produção exigir — avaliar no Design, não obrigatório |

---

## User Stories

### P1: Detector de cicatriz escalado (vídeo real fecha ALTO) ⭐ MVP

**User Story**: Como equipe clínica, quero que o sistema **detecte de fato** o sinal de infecção na cicatriz
a partir do vídeo/foto, para que o cenário de **infecção puerperal** dispare **ALTO** com evidência visual
real — e não dependa só de vitais+texto.

**Why P1**: É a degradação mais visível hoje (smoke não detecta acima do limiar) e o coração da
**multimodalidade** demonstrável; sem ela, o `caso_alto` fecha MÉDIO.

**Acceptance Criteria**:

1. WHEN o detector é treinado THEN ele SHALL usar um **dataset ampliado** (além das 6 imagens smoke, via
   AZH Wound + classe "ferida com sinal de alerta", ver [`docs/datasets.md`](../../../docs/datasets.md)) e
   treino em **GPU/Colab** (YOLOv8n/s), com **métricas reais** registradas em
   `ai-service/models/cicatriz/metrics.json`.
2. WHEN uma imagem com sinal de infecção é inferida THEN o detector SHALL retornar `ferida_alerta` **acima
   do limiar** de confiança definido em [`app/limiares.py`](../../../ai-service/app/limiares.py).
3. WHEN o `caso_alto` roda no `scripts/e2e_demo.py` THEN a fusão SHALL fechar **ALTO** **sem mock**, com a
   evidência de vídeo presente (não omitida por degradação — DD10).
4. WHEN os pesos não cabem no Git THEN a estratégia de versionamento SHALL ser decidida (Git LFS vs. só
   métricas + script de download), coerente com a decisão pendente do STATE.

**Independent Test**: Rodar `scripts/e2e_demo.py` com o `caso_alto` e os pesos treinados e observar `ALTO`
com a evidência de cicatriz; conferir `metrics.json` com mAP acima do baseline smoke.

---

### P1: Modalidades de áudio e fisioterapia completas ⭐ MVP

**User Story**: Como avaliador, quero que **áudio** (depressão pós-parto/ansiedade/violência) e
**fisioterapia** (pose) produzam **saída real com métricas**, para que as 4 modalidades estejam de fato
funcionando — não degradadas.

**Why P1**: A própria Definition of Done do projeto exige "4 modalidades produzem saída individual com
métricas" ([`docs/00 §8`](../../../docs/00-visao-geral-e-escopo.md)); hoje duas degradam (DD10).

**Acceptance Criteria**:

1. WHEN as amostras de áudio e fisioterapia são obtidas (Fase 1, obtenção manual: Androids/DEPAC,
   IntelliRehabDS — ver [`data/README.md`](../../../data/README.md)) THEN elas SHALL ser preparadas pelos
   scripts de `scripts/data_prep/` sem dados sensíveis no Git.
2. WHEN o baseline de áudio roda THEN ele SHALL transcrever (Whisper local **ou** Azure Speech — backend
   trocável por env, blocker do STATE a resolver) e classificar, com **métricas reais** registradas em
   `ai-service/models/`.
3. WHEN o baseline de fisioterapia roda THEN o **YOLOv8-pose** SHALL avaliar a execução do exercício com
   métricas registradas.
4. WHEN qualquer modalidade ainda não tiver dados THEN o sistema SHALL **continuar degradando sem quebrar**
   (DD10 preservado) — a meta é remover a degradação onde houver dados, não introduzir falhas.

**Independent Test**: Rodar a inferência de cada modalidade e o baseline; confirmar saída padronizada do
contrato §3 com métricas em `ai-service/models/` (não mais "nenhum"/omitido).

---

### P1: Deploy real na Azure (com fallback local)

**User Story**: Como responsável pela infraestrutura, quero a stack **rodando de fato na Azure** (Blob +
serviço de IA + backend), para cumprir o requisito de nuvem do desafio com um ambiente real validado.

**Why P1**: É item **aberto** do checklist (§Pré-requisitos) e decisão pendente do STATE; hoje só há
fallback local.

**Acceptance Criteria**:

1. WHEN o deploy é executado seguindo [`docs/deploy-azure.md`](../../../docs/deploy-azure.md) THEN SHALL
   existir uma **Storage Account + container** e o **upload via código** SHALL funcionar com
   `STORAGE_BACKEND=azure` (Blob testado de verdade).
2. WHEN o serviço de IA e o backend estão publicados (ACI/App Service) THEN o **smoke pós-deploy** SHALL
   passar (`GET /health` → `{"status":"ok"}` e um `POST /analisar` gerando alerta).
3. WHEN segredos são necessários THEN eles SHALL vir de **Key Vault / variáveis de ambiente** (nunca do
   Git), com **TLS** e **SAS com expiração** (controles de [`docs/07`](../../../docs/07-privacidade-e-seguranca.md)).
4. WHEN a Azure estiver indisponível/limitada THEN o **fallback local** (`STORAGE_BACKEND=local` +
   `docker compose up`) SHALL continuar funcionando sem alteração de código.

**Independent Test**: Executar os passos do `docs/deploy-azure.md` numa conta Azure, rodar o smoke
pós-deploy e obter o alerta; depois alternar para `local` e confirmar paridade.

---

### P2: Dashboard React de produção

**User Story**: Como equipe de monitoramento, quero o **dashboard** completo (lista de pacientes, dar
entrada, upload, visão geral e **detalhe do caso** com painéis por modalidade + fusão), para acompanhar
risco em tempo real — substituindo o cliente mínimo.

**Why P2**: Valoriza a entrega e é a "cena principal" do vídeo, mas o cliente mínimo já demonstra o alerta;
por isso não é MVP da Fase 5.

**Acceptance Criteria**:

1. WHEN o front-end é criado THEN ele SHALL ficar em `frontend/` com a stack de
   [`docs/frontend.md §2`](../../../docs/frontend.md) (React + Vite + TypeScript; tempo real via
   socket.io-client) e consumir o backend Node via REST + WebSocket (contrato existente).
2. WHEN a **tela de detalhe do caso** é aberta THEN ela SHALL exibir os painéis por modalidade
   (cicatriz/YOLO, fisioterapia/pose, sinais vitais, áudio, texto) e o **painel de fusão** com o medidor de
   risco e a `mensagem_alerta`, além do botão de **relatório**.
3. WHEN chega um risco **MÉDIO/ALTO** em tempo real THEN a UI SHALL disparar o **alerta visual** (banner +
   cor + ícone + texto — acessibilidade, não só cor).
4. WHEN o caso ainda está processando THEN os **estados de UI** (loading/processando/erro/vazio) SHALL ser
   tratados, e o **disclaimer** "apoio à decisão, não diagnóstico" SHALL estar visível.

**Independent Test**: Subir backend + frontend, dar entrada de um paciente, enviar o `caso_alto` e ver o
detalhe do caso com o alerta vermelho da fusão em tempo real.

---

### P2: Reforço dos sinais vitais (pré-eclâmpsia)

**User Story**: Como autor do modelo, quero **mais dados (sintéticos) de pré-eclâmpsia** para reforçar o
classificador de sinais vitais e **reavaliar as métricas**, melhorando a confiança nessa modalidade.

**Why P2**: É uma "ideia adiada" do STATE que melhora a qualidade, mas o modelo atual já tem métricas reais
(acurácia≈0.65/F1≈0.62).

**Acceptance Criteria**:

1. WHEN dados sintéticos de pré-eclâmpsia são gerados/agregados THEN eles SHALL seguir o esquema tabular
   existente (PA, FC, glicemia, temperatura) e ser produzidos por `scripts/` (sem dados reais).
2. WHEN o modelo é retreinado THEN as **novas métricas** SHALL ser registradas e **comparadas** ao baseline
   anterior (sem regressão silenciosa), atualizando `ai-service/models/sinais_vitais/`.

**Independent Test**: Retreinar e comparar `metrics.json` antes/depois; confirmar melhoria ou empate
documentado.

---

### P3: Hardening (observabilidade, CI/CD, segurança de produção)

**User Story**: Como mantenedor, quero **observabilidade, CI/CD e segurança** adequados a um ambiente real,
para operar a solução com confiança após o deploy.

**Why P3**: Importante para "produção", mas depende dos P1/P2 estarem no ar; o logging com `case_id` já
existe (Fase 3).

**Acceptance Criteria**:

1. WHEN os serviços rodam em produção THEN eles SHALL expor **health/observabilidade** além do `case_id` já
   logado (ex.: métricas básicas, readiness), sem expor dados sensíveis.
2. WHEN há push na branch principal THEN o **CI/CD** SHALL, além do gate atual, **construir e publicar as
   imagens** (ACR) e suportar o deploy (ver [`docs/qualidade-testes-ci.md`](../../../docs/qualidade-testes-ci.md)).
3. WHEN o ambiente em nuvem é revisado THEN ele SHALL atender aos controles de
   [`docs/07`](../../../docs/07-privacidade-e-seguranca.md) (RBAC, TLS, SAS, segredos fora do Git).

**Independent Test**: Disparar o pipeline e ver imagens publicadas; conferir os endpoints de health e a
checklist de segurança do ambiente.

---

## Edge Cases

- WHEN **não houver GPU/Colab** disponível THEN o treino da cicatriz SHALL permanecer reprodutível como
  **smoke** e a degradação SHALL continuar documentada (DD10) — a Fase 5 não pode quebrar o gate por falta
  de hardware.
- WHEN as **amostras de áudio/fisioterapia** não puderem ser obtidas (licença/login) THEN essas modalidades
  SHALL **continuar degradando sem quebrar** e o item permanece como blocker no STATE.
- WHEN a **conta Azure** não estiver disponível (custo/limite) THEN o **fallback local** SHALL ser o caminho
  válido e o deploy real fica como passo documentado/ação humana — sem travar o gate.
- WHEN os **pesos treinados** forem grandes demais para o Git THEN a entrega SHALL usar **Git LFS** ou
  **métricas + script de download**, decidido no Design (não versionar binários grandes às cegas).
- WHEN o **dashboard** consumir um endpoint inexistente THEN ele SHALL falhar de forma graciosa e o backend
  SHALL ser estendido **sem quebrar** o contrato existente.

---

## Requirement Traceability

| Requirement ID | Story                                                       | Fonte (item aberto)                                   | Phase | Status  |
| -------------- | ----------------------------------------------------------- | ----------------------------------------------------- | ----- | ------- |
| F5-01          | P1: Detector de cicatriz escalado (fecha ALTO)              | STATE todos/blockers; checklist §Escopo               | —     | **Bloqueado (ambiente: GPU/Colab + dataset)** |
| F5-02          | P1: Áudio + fisioterapia completas (métricas reais)         | STATE todos/blockers; checklist §Técnico (DD10)       | —     | **Bloqueado (ambiente: dados c/ licença)** |
| F5-03          | P1: Deploy real na Azure (com fallback)                     | checklist §Pré-requisitos; STATE decisão pendente     | —     | **Bloqueado (ambiente: conta/credenciais Azure)** |
| F5-04          | P2: Dashboard React de produção                             | STATE ideias adiadas / out-of-scope F4; `docs/frontend.md` | Execute | **Implementado** |
| F5-05          | P2: Reforço dos sinais vitais (pré-eclâmpsia)               | STATE ideias adiadas                                  | Execute | **Implementado** |
| F5-06          | P3: Hardening (observabilidade/CI-CD/segurança)             | `docs/qualidade-testes-ci.md`; `docs/07`              | Execute | **Implementado (parcial)** |

**ID format:** `F5-[NUMBER]` (Fase 5).
**Status values:** Pending → In Design → In Tasks → Implementing → Verified | Bloqueado (ambiente).
**Coverage:** 6 requisitos — **3 implementados** (F5-04/05/06), **3 bloqueados por ambiente** (F5-01/02/03:
exigem GPU/Colab, datasets com licença e conta Azure; o código já está pronto/Azure-ready e a degradação
está documentada — DD10). Detalhe do implementado em [`docs/08-fase5-producao-e-escala.md`](../../../docs/08-fase5-producao-e-escala.md).

---

## Decisões a confirmar com o grupo

> Conforme `AGENTS.md` (Princípio 1 — não presumir). Estas escolhas mudam significativamente o esforço e
> devem ser confirmadas **antes** do Design.

1. **Esta é a "Fase 5" pretendida?** A proposta é **Produção/Escala/Robustez** (fechar os itens abertos do
   checklist/STATE). Se "Fase 5" se referir a **outro Tech Challenge da pós (8IADT)** com enunciado próprio,
   forneça o **PDF/requisitos** para reescrever esta spec.
2. **Whisper local vs. Azure Speech-to-Text** para o áudio (blocker aberto do STATE).
3. **Versionamento dos pesos do YOLO:** Git LFS vs. apenas métricas + script de download.
4. **Deploy:** Opção A (Azure Container Instances) vs. B (App Service) do `docs/deploy-azure.md`; e se há
   **conta/orçamento Azure** disponível ou se o deploy real fica como ação humana.
5. **Persistência em produção:** manter **SQLite** (S18) ou migrar para **Postgres/Cosmos**.
6. **Profundidade do dashboard:** todas as telas de `docs/frontend.md` ou apenas o **detalhe do caso** + lista.

---

## Success Criteria

Como saberemos que a Fase 5 está pronta:

- [ ] **Cicatriz** treinada/escala: `caso_alto` fecha **ALTO** ponta a ponta com evidência de vídeo real
      (sem degradação), métricas em `models/cicatriz/metrics.json` acima do baseline smoke.
- [ ] **Áudio e fisioterapia** com **saída real + métricas** registradas (degradação DD10 removida onde há dados).
- [ ] **Deploy Azure** validado por smoke pós-deploy (Blob testado, `/health` ok, alerta), com **fallback
      local** intacto.
- [ ] **Dashboard React** (`frontend/`) com a tela de **detalhe do caso** + alerta em tempo real, substituindo
      o cliente mínimo.
- [ ] **Sinais vitais** reavaliados com dados extras (métricas comparadas, sem regressão).
- [ ] **Hardening**: observabilidade/health, CI/CD com build+push de imagens e revisão de segurança do ambiente.
- [ ] **Gate verde** preservado (ruff+pytest / eslint+jest) e `docker compose up` reprodutível em todas as mudanças.
- [ ] **STATE** e **docs** atualizados (Fase 5 fechada, decisões registradas).

> **Itens que permanecem ação humana** (não bloqueiam o desenvolvimento da Fase 5): gravar/publicar o
> **vídeo** e preencher os **integrantes** no README (itens `[ ]` do [checklist](../../../docs/05-checklist-entrega.md)).
