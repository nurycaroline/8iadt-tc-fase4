# Fase 5 — Produção, Escala e Robustez

> Objetivo: elevar a solução de **demo-grade** para **produção**, fechando os itens que ficaram **abertos**
> no [checklist de entrega](05-checklist-entrega.md) e nos `todos`/`ideias adiadas` do
> [`STATE.md`](../.specs/project/STATE.md). Planejamento detalhado (Specify) em
> [`.specs/features/fase5-producao-e-escala/`](../.specs/features/fase5-producao-e-escala/spec.md).

> ⚠️ **Rascunho de planejamento (escopo a confirmar — `AGENTS.md`).** As Fases 1–4 já entregam o Tech
> Challenge atual; **não havia "Fase 5"** no plano. Esta fase foi proposta como **Produção/Escala/Robustez**
> porque é o que resta em aberto. Se "Fase 5" significar **outro desafio (8IADT)** com enunciado próprio,
> traga o PDF e o escopo será reescrito. Pontos a confirmar com o grupo na seção
> [Decisões a confirmar](../.specs/features/fase5-producao-e-escala/spec.md#decisões-a-confirmar-com-o-grupo).

## Motivação (o que ainda está em aberto)

| # | Item em aberto | Onde está registrado | Estado atual |
|---|----------------|----------------------|--------------|
| 1 | Detector de **cicatriz** detecta abaixo do limiar (smoke, 6 imagens) | STATE `todos`/`blockers`; [checklist §Escopo](05-checklist-entrega.md) | `caso_alto` fecha **MÉDIO** (vitais+texto), não ALTO |
| 2 | **Áudio** e **fisioterapia** degradam por falta de dados (DD10) | STATE `todos`/`blockers`; [checklist §Técnico](05-checklist-entrega.md) | Sem métricas reais dessas 2 modalidades |
| 3 | **Deploy real na Azure** (Blob testado, serviços hospedados) | [checklist §Pré-requisitos](05-checklist-entrega.md); STATE | Só **fallback local** (`STORAGE_BACKEND=local`) |
| 4 | **Dashboard React** completo | STATE `ideias adiadas` / out-of-scope da Fase 4; [`frontend.md`](frontend.md) | Apenas **cliente mínimo** (HTML + socket.io) |
| 5 | **Pré-eclâmpsia**: reforçar sinais vitais com dados sintéticos | STATE `ideias adiadas` | Modelo com métricas reais (acurácia≈0.65/F1≈0.62) |

> **Permanece ação humana** (não é desenvolvimento desta fase): gravar/publicar o **vídeo** e preencher os
> **integrantes** no README — itens `[ ]` do [checklist §Vídeo/§Antes de submeter](05-checklist-entrega.md).

## Resultado esperado (Definition of Done)

- [ ] **Cicatriz escalada**: treino em GPU/Colab com dataset ampliado; `caso_alto` fecha **ALTO** ponta a
      ponta **com evidência de vídeo real** (sem degradação) — F5-01.
- [ ] **Áudio + fisioterapia completas**: amostras obtidas, baseline rodado e **métricas reais** publicadas
      em `ai-service/models/` — F5-02.
- [ ] **Deploy Azure** validado por **smoke pós-deploy** (Blob testado, `/health` ok, alerta), mantendo o
      **fallback local** — F5-03.
- [ ] **Dashboard React** (`frontend/`) com a tela de **detalhe do caso** + alerta em tempo real,
      substituindo o cliente mínimo — F5-04.
- [ ] **Sinais vitais** reavaliados com dados extras de pré-eclâmpsia (métricas comparadas) — F5-05.
- [ ] **Hardening**: observabilidade/health, CI/CD com build+push de imagens e revisão de segurança do
      ambiente em nuvem — F5-06.
- [ ] **Gate verde** preservado (`ruff`+`pytest` / `eslint`+`jest`) e `docker compose up` reprodutível.

---

## Tarefas (visão macro)

> Quebra atômica (com dependências, "done when" e gate por tarefa) virá no `tasks.md` da feature **após** a
> confirmação do escopo e a fase de **Design**. Visão macro abaixo, em ordem sugerida de caminho crítico.

### Tarefa 5.1 — Escalar o detector de cicatriz (F5-01)
- Ampliar o dataset (AZH Wound + classe "ferida com sinal de alerta") — ver [`datasets.md`](datasets.md).
- Treinar YOLOv8n/s em **GPU/Colab**; registrar métricas reais em `ai-service/models/cicatriz/metrics.json`.
- Ajustar/validar o limiar em [`app/limiares.py`](../ai-service/app/limiares.py) e rodar `scripts/e2e_demo.py`
  com o `caso_alto` (deve fechar **ALTO**).
- Decidir versionamento dos pesos (Git LFS vs. métricas + download).

### Tarefa 5.2 — Completar áudio e fisioterapia (F5-02)
- Obter amostras (obtenção manual: Androids/DEPAC para áudio; IntelliRehabDS para pose) — ver
  [`data/README.md`](../data/README.md) e [`01-fase1-dados.md`](01-fase1-dados.md).
- Preparar via `scripts/data_prep/`; rodar baseline de áudio (Whisper local **ou** Azure Speech — decidir) e
  de fisioterapia (YOLOv8-pose); publicar métricas.
- Manter a degradação graciosa (DD10) onde ainda faltarem dados.

### Tarefa 5.3 — Deploy real na Azure (F5-03)
- Seguir [`deploy-azure.md`](deploy-azure.md): Storage Account + container, publicar `ai-service` e `backend`
  (Opção A=ACI ou B=App Service — decidir).
- Segredos via Key Vault / `.env`; TLS; SAS com expiração ([`07-privacidade-e-seguranca.md`](07-privacidade-e-seguranca.md)).
- **Smoke pós-deploy** (`/health` + `POST /analisar`); confirmar paridade com o **fallback local**.

### Tarefa 5.4 — Dashboard React de produção (F5-04)
- Criar `frontend/` (React + Vite + TS) conforme [`frontend.md`](frontend.md), consumindo o backend
  (REST + socket.io) pelo [contrato existente](contrato-api.md).
- Implementar a **tela de detalhe do caso** (painéis por modalidade + fusão), lista/entrada de pacientes,
  upload e download do relatório; alerta em tempo real (acessível: cor+ícone+texto).

### Tarefa 5.5 — Reforço dos sinais vitais (F5-05)
- Gerar/agregar dados sintéticos de pré-eclâmpsia (esquema tabular existente) via `scripts/`.
- Retreinar e **comparar** métricas com o baseline (sem regressão silenciosa).

### Tarefa 5.6 — Hardening (F5-06)
- Observabilidade/health além do `case_id` já logado; CI/CD com build+push de imagens (ACR) — ver
  [`qualidade-testes-ci.md`](qualidade-testes-ci.md).
- Revisão de segurança/LGPD do ambiente em nuvem (RBAC, TLS, SAS, segredos fora do Git).

---

## Caminho crítico e paralelização

- **Caminho crítico:** 5.1 (treino do YOLO é o item mais demorado — começar cedo) → 5.3 (deploy) → 5.6 (CI/CD do deploy).
- **Paralelizável:** 5.2 (dados/áudio/pose), 5.4 (frontend) e 5.5 (vitais) podem correr em paralelo, pois
  dependem do contrato/artefatos já estáveis das Fases 2–3.
- **Sem GPU/Azure?** As tarefas 5.1 e 5.3 degradam para o estado atual (smoke + fallback local) sem quebrar
  o gate — ver Edge Cases na [spec](../.specs/features/fase5-producao-e-escala/spec.md).

## Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Sem GPU para treinar o YOLO | Usar Colab/GPU gratuita; manter smoke reprodutível como fallback documentado |
| Datasets de áudio/pose exigem login/licença | Obtenção manual documentada ([`data/README.md`](../data/README.md)); degradar sem quebrar |
| Custo/limite da conta Azure | Tier gratuito; fallback local sempre disponível; deploy real como passo opcional |
| Pesos grandes no Git | Git LFS **ou** métricas + script de download (decidir no Design) |
| Regressão das Fases 2–4 | Gate verde obrigatório em toda mudança; `docker compose up` reprodutível |
