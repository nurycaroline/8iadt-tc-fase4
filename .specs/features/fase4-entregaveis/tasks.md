# Fase 4 — Empacotamento e Entregáveis — Tasks

**Spec**: [`spec.md`](spec.md)
**Design**: [`design.md`](design.md)
**Status**: **Implementado** (T1–T9). Gate verde (ruff + 96 testes Python; eslint + 11 testes Node).
Entregáveis do agente prontos (repositório auditado + relatório técnico + roteiro do vídeo); a
**gravação/publicação do vídeo** e os **nomes dos integrantes** são ação humana (placeholders no README).
Insumos: stack ponta-a-ponta da [Fase 3](../fase3-fusao-e-nuvem/) + métricas reais da
[Fase 2](../fase2-modelos/) (`ai-service/models/*`) + casos de exemplo (`data/casos/*.json`).

> Cada tarefa = 1 entregável atômico (um documento / uma capacidade), com `Done when` verificável e um
> commit. Esta fase **não cria código de produto**: consolida evidências e escreve a documentação de
> entrega. **Nunca inventar** métricas — toda afirmação linka para o artefato de origem (`AGENTS.md`).
> **Não regredir o gate** existente (ruff+pytest / eslint+jest).

---

## Execution Plan

### Fase A — Auditoria e evidências (base factual) — Sequencial→Paralela

Primeiro garantir a base de fatos (repo + evidências), pois relatório e vídeo dependem dela.

```
T1 (auditoria do repo) → ┌→ T2 (evidências consolidadas)  [P]
                         └→ T3 (diagrama de arquitetura)   [P]
```

### Fase B — Relatório técnico — Sequencial (após A)

```
(T2 + T3) → T4 (relatório técnico: 6 seções) → T5 (exportação PDF c/ fallback)
```

### Fase C — Vídeo + fechamento — Sequencial (após B)

```
T4 → T6 (roteiro de vídeo) → T7 (README: créditos + link do vídeo) → T8 (checklist + gate) → T9 (STATE + docs/04)
```

> **Ação humana (fora do agente):** gravar e publicar o vídeo "Não listado" e colar o link no README
> (preparado por T6/T7). Ver `spec.md` Out of Scope e DD-F4-5.

---

## Task Breakdown

### T1: Auditoria do repositório (Tarefa 4.1)

**What**: Conferir, contra a [Tarefa 4.1](../../../docs/04-fase4-entregaveis.md) e o
[checklist](../../../docs/05-checklist-entrega.md), a estrutura de pastas, `requirements.txt`/`package.json`
(versões fixadas), `.gitignore` (`data/`, `.env`, pesos/`runs/`) e a presença do **disclaimer ético**.
Corrigir lacunas pequenas; registrar pendências maiores como justificativa.
**Where**: `README.md`, `.gitignore`, `ai-service/requirements.txt`, `backend/package.json` (apenas se houver lacuna)
**Depends on**: None
**Reuses**: `design.md` §4.1; `docs/05-checklist-entrega.md`
**Requirement**: F4E-01

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Estrutura `/ai-service`, `/backend`, `/docs`, `/scripts` confirmada; deps com versões fixadas conferidas.
- [ ] `.gitignore` cobre `data/`, `.env`, pesos e `runs/`; disclaimer ético presente no README.
- [ ] Itens 4.1 do checklist marcados ou com justificativa (ex.: pesos via métricas, não LFS — DD-F4-7).
- [ ] Nenhuma alteração regride o gate (`ruff`/`pytest`, `eslint`/`jest`).

**Tests**: none · **Gate**: build
**Commit**: `docs(fase4): auditoria do repositório (estrutura, deps, gitignore, disclaimer)`

---

### T2: Evidências consolidadas (métricas, exemplo, log E2E) [P]

**What**: Reunir em `docs/relatorio/` os artefatos reais: tabela legível de `models/metricas_fusao.json`
(`metricas-fusao.md`); **exemplo de relatório automático** gerado por `app/relatorio.py` sobre
`data/casos/caso_alto.json` (`exemplo-relatorio-automatico.md`/`.html`); e o **trecho de log** do
`scripts/e2e_demo.py` com `case_id` (`e2e-log.txt`).
**Where**: `docs/relatorio/metricas-fusao.md`, `docs/relatorio/exemplo-relatorio-automatico.md` (+`.html`), `docs/relatorio/e2e-log.txt`
**Depends on**: T1
**Reuses**: `ai-service/models/metricas_fusao.json`, `models/sinais_vitais/*`, `models/cicatriz/metrics.json`, `models/baseline.json`, `ai-service/app/relatorio.py`, `scripts/e2e_demo.py`; `design.md` §4.2
**Requirement**: F4E-02

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] `metricas-fusao.md` reproduz a tabela de `metricas_fusao.json` (fusão × modalidade única) sem alterar números.
- [ ] `exemplo-relatorio-automatico.md` é gerado pelo `app/relatorio.py` sobre o `caso_alto` (não escrito à mão).
- [ ] `e2e-log.txt` contém um trecho real do `scripts/e2e_demo.py` com `case_id` rastreável.
- [ ] Nenhum dado real de paciente (só caso sintético/datasets públicos — LGPD).

**Tests**: none (execução/smoke) · **Gate**: build
**Commit**: `docs(fase4): evidências consolidadas (métricas, exemplo de relatório, log E2E)`

---

### T3: Diagrama de arquitetura / fluxo multimodal [P]

**What**: Produzir o diagrama do fluxo (Node orquestrador + Python/IA + storage + fusão + alerta) para o
relatório e o vídeo, reaproveitando [docs/arquitetura.md](../../../docs/arquitetura.md) e
[docs/casos-de-uso.md](../../../docs/casos-de-uso.md).
**Where**: bloco Mermaid em `docs/relatorio-tecnico.md` (ou imagem em `docs/relatorio/` se `mermaid-studio` instalada)
**Depends on**: T1
**Reuses**: `docs/arquitetura.md` §1; `docs/casos-de-uso.md`; `design.md` §4.6
**Requirement**: F4E-03

**Tools**: MCP: NONE · Skill: `mermaid-studio` (se instalada; senão Mermaid inline + recomendação única)

**Done when**:

- [ ] Diagrama representa os 2 serviços, o storage (Azure/local), a fusão e o alerta em tempo real.
- [ ] Coerente com `docs/arquitetura.md`; renderizado (se `mermaid-studio`) ou Mermaid inline válido.

**Tests**: none · **Gate**: build
**Commit**: `docs(fase4): diagrama de arquitetura e fluxo multimodal`

---

### T4: Relatório técnico — `docs/relatorio-tecnico.md` (Tarefa 4.2) ⭐

**What**: Escrever o relatório com as **6 seções** do PDF: (1) fluxo multimodal + diagrama; (2) modelos por
modalidade + justificativas; (3) lógica de fusão + **métrica do ganho**; (4) resultados e exemplos de
anomalias (métricas, matriz de confusão, mAP); (5) privacidade/LGPD; (6) exemplo de relatório automático.
Cada métrica/afirmação linka para o artefato de origem.
**Where**: `docs/relatorio-tecnico.md`
**Depends on**: T2, T3
**Reuses**: `docs/relatorio/*` (T2), diagrama (T3), [Fase 2 design](../fase2-modelos/design.md), [Fase 3 design](../fase3-fusao-e-nuvem/design.md), `docs/contrato-api.md` §4, `docs/07-privacidade-e-seguranca.md`; `design.md` §4.3
**Requirement**: F4E-04, F4E-05, F4E-06, F4E-07, F4E-08, F4E-09

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] As 6 seções existem e seguem [docs/04 §4.2](../../../docs/04-fase4-entregaveis.md).
- [ ] Seção 3 traz a tabela fusão × modalidade única **idêntica** a `metricas_fusao.json` + conclusão (FP↓/recall↑).
- [ ] Seção 4 usa métricas reais (vitais: acurácia/F1 + matriz de confusão; cicatriz: mAP) e **documenta limitações** (smoke/degradação — DD-F4-6).
- [ ] Seção 5 cobre LGPD (princípios + controles de docs/07) e inclui o **disclaimer ético**.
- [ ] Seção 6 embute/linka o exemplo de relatório automático (T2).
- [ ] Toda métrica citada tem **link/origem**; nenhuma fabricada (`AGENTS.md`).

**Tests**: none (revisão de rastreabilidade) · **Gate**: build
**Commit**: `docs(fase4): relatório técnico (fluxo, modelos, fusão, resultados, LGPD)`

---

### T5: Exportação do relatório para PDF (com fallback) (Tarefa 4.2)

**What**: Gerar `docs/relatorio-tecnico.pdf` a partir do Markdown (reusar `markdown`+`weasyprint` de
`app/relatorio.py`, ou `pandoc`); se as libs/sistema faltarem, **degradar para HTML/Markdown** e documentar
no README como gerar localmente.
**Where**: `docs/relatorio-tecnico.pdf` (ou `.html`), `scripts/exportar_relatorio.py` (opcional), `README.md` (instrução)
**Depends on**: T4
**Reuses**: `ai-service/app/relatorio.py` (conversão); `design.md` §4.4
**Requirement**: F4E-10

**Tools**: MCP: `context7` (apenas se precisar confirmar API de `pandoc`/`weasyprint`) · Skill: NONE

**Done when**:

- [ ] Com libs disponíveis → PDF gerado a partir do mesmo Markdown versionado.
- [ ] Sem libs → HTML/Markdown mantido + instrução de geração local no README (sem quebrar — DD-F4-2).

**Tests**: none (execução/smoke) · **Gate**: build
**Commit**: `docs(fase4): exportação do relatório técnico para PDF (com fallback)`

---

### T6: Roteiro de vídeo — `docs/roteiro-video.md` (Tarefa 4.3)

**What**: Roteiro bloco a bloco (≤15 min) com os **8 pontos** de
[docs/04 §4.3](../../../docs/04-fase4-entregaveis.md): para cada bloco — fala, o que mostrar, comando
(`docker compose up`, `scripts/e2e_demo.py`, `POST /analisar` do `caso_alto`, cliente em
`http://localhost:3000/`) e duração estimada. Inclui a degradação documentada e a instrução de publicar
"Não listado" + colar o link no README.
**Where**: `docs/roteiro-video.md`
**Depends on**: T4
**Reuses**: `README.md` (comandos), `scripts/e2e_demo.py`, `data/casos/*.json`; `docs/04` §4.3; `design.md` §4.5
**Requirement**: F4E-11

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Os 8 pontos do roteiro estão cobertos, com comandos reais e durações que somam ≤15 min.
- [ ] Caminho de demonstração válido mesmo sem pesos YOLO/ASR (fusão decide com vitais+texto — DD-F4-6).
- [ ] Instrução de publicação "Não listado" + onde inserir o link no README.

**Tests**: none · **Gate**: build
**Commit**: `docs(fase4): roteiro do vídeo de demonstração (8 pontos, ≤15 min)`

---

### T7: README — créditos/integrantes + link do vídeo (Tarefa 4.1/4.3)

**What**: Adicionar ao `README.md` a seção de **créditos/integrantes** e um **placeholder claro do link do
vídeo** (a ser preenchido após a publicação humana); apontar para o relatório técnico e o roteiro.
**Where**: `README.md`
**Depends on**: T6
**Reuses**: `docs/relatorio-tecnico.md`, `docs/roteiro-video.md`; `design.md` §4.1
**Requirement**: F4E-12

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] README tem seção de créditos/integrantes e placeholder do link do vídeo (marcado como pendente humano).
- [ ] README linka o relatório técnico e o roteiro; disclaimer ético visível.

**Tests**: none · **Gate**: build
**Commit**: `docs(fase4): README com créditos e espaço para o link do vídeo`

---

### T8: Checklist de entrega + verificação do gate

**What**: Percorrer [docs/05-checklist-entrega.md](../../../docs/05-checklist-entrega.md) marcando/justificando
cada item; rodar o **gate** num clone limpo (`ruff check scripts ai-service` + `pytest -q`; `npm run lint`
+ `npm test`) e registrar o resultado.
**Where**: `docs/05-checklist-entrega.md`
**Depends on**: T7
**Reuses**: `pyproject.toml`, `backend/package.json` (scripts); `design.md` §6
**Requirement**: F4E-13

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Todos os itens do checklist marcados ou com justificativa (ex.: vídeo = ação humana; Azure = fallback).
- [ ] Gate verde registrado (contagem de testes Python e Node) — sem regressão.

**Tests**: gate (lint+testes existentes) · **Gate**: full
**Commit**: `docs(fase4): checklist de entrega revisado + gate verde`

---

### T9: STATE + docs/04 atualizados (fechamento da fase)

**What**: Registrar a Fase 4 no `STATE.md` (fase atual, decisões DD-F4-1..DD-F4-8, todos concluídos) e
marcar os itens do DoD em `docs/04-fase4-entregaveis.md`.
**Where**: `.specs/project/STATE.md`, `docs/04-fase4-entregaveis.md`
**Depends on**: T8
**Reuses**: `spec.md`, `design.md`; `design.md` §5
**Requirement**: F4E-14

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] STATE registra a Fase 4 (entregáveis + decisões); todos da Fase 4 marcados.
- [ ] DoD de `docs/04` marcado (repo/relatório prontos; vídeo = pendência humana com roteiro entregue).

**Tests**: none · **Gate**: build
**Commit**: `docs(fase4): STATE + DoD da Fase 4 atualizados`

---

## Parallel Execution Map

```
Fase A (base factual):
  T1 → ├── T2  [P]  (evidências)
       └── T3  [P]  (diagrama)

Fase B (relatório):
  (T2 + T3) → T4 → T5

Fase C (vídeo + fechamento):
  T4 → T6 → T7 → T8 → T9
```

**Restrição de paralelismo**: T2 e T3 escrevem arquivos distintos sob `docs/` e dependem só de T1 → `[P]`
seguro. T4 consolida T2+T3 e é o entregável central. T5–T9 são sequenciais (exportação depende do relatório;
README/checklist/STATE consolidam o fechamento). A **gravação do vídeo** é externa (humana), preparada por T6/T7.

---

## Task Granularity Check

| Task | Escopo                                          | Status      |
| ---- | ----------------------------------------------- | ----------- |
| T1   | auditoria do repo (correções pontuais)          | ✅ Granular |
| T2   | evidências consolidadas (3 artefatos)           | ✅ Granular |
| T3   | 1 diagrama                                      | ✅ Granular |
| T4   | 1 documento (relatório, 6 seções)               | ✅ Granular |
| T5   | exportação PDF (1 capacidade + fallback)        | ✅ Granular |
| T6   | 1 documento (roteiro)                           | ✅ Granular |
| T7   | README (créditos + link)                        | ✅ Granular |
| T8   | checklist + gate                                | ✅ Granular |
| T9   | STATE + docs/04                                 | ✅ Granular |

> Nota: T4 cobre 6 requisitos (F4E-04..09) por ser **um documento único** com 6 seções — manter coeso evita
> fragmentar o relatório em arquivos soltos. Se a escrita revelar >5 subtarefas independentes, considerar
> dividir por seção.

---

## Diagram-Definition Cross-Check

| Task | Depends On (body) | Diagrama mostra   | Status   |
| ---- | ----------------- | ----------------- | -------- |
| T1   | None              | (raiz A)          | ✅ Match |
| T2   | T1                | T1→T2 [P]         | ✅ Match |
| T3   | T1                | T1→T3 [P]         | ✅ Match |
| T4   | T2, T3            | (T2+T3)→T4        | ✅ Match |
| T5   | T4                | T4→T5             | ✅ Match |
| T6   | T4                | T4→T6             | ✅ Match |
| T7   | T6                | T6→T7             | ✅ Match |
| T8   | T7                | T7→T8             | ✅ Match |
| T9   | T8                | T8→T9             | ✅ Match |

---

## Test Co-location Validation

| Task | Camada criada/modificada     | Matriz exige | Tarefa diz | Status |
| ---- | ---------------------------- | ------------ | ---------- | ------ |
| T1   | docs/config (auditoria)      | none         | none       | ✅ OK  |
| T2   | evidências (execução/smoke)  | none         | none       | ✅ OK  |
| T3   | diagrama (doc)               | none         | none       | ✅ OK  |
| T4   | relatório (doc)              | none         | none       | ✅ OK  |
| T5   | exportação (IO/sistema)      | none         | none       | ✅ OK  |
| T6   | roteiro (doc)                | none         | none       | ✅ OK  |
| T7   | README (doc)                 | none         | none       | ✅ OK  |
| T8   | checklist + gate             | gate         | gate       | ✅ OK  |
| T9   | STATE/docs (doc)             | none         | none       | ✅ OK  |

> Justificativa de `none`: a Fase 4 é **documentação/empacotamento** — não há lógica nova testável. A
> garantia de qualidade é **não regredir o gate** das Fases 2–3 (T8 verifica `ruff`/`pytest`/`eslint`/`jest`)
> e a **rastreabilidade** das métricas (T4 revisa que cada número aponta para um artefato real).

---

## Gate de fim da Fase 4

A Fase 4 está pronta quando os **3 entregáveis** estiverem prontos (conforme o DoD de
[docs/04](../../../docs/04-fase4-entregaveis.md) e o [checklist](../../../docs/05-checklist-entrega.md)):

1. **Repositório** auditado (T1, T7), com README de execução do zero, deps fixadas, `.gitignore` e disclaimer.
2. **Relatório técnico** (T4) com as 6 seções e métricas reais rastreáveis (+ PDF/HTML por T5).
3. **Roteiro de vídeo** (T6) pronto para gravação; **gravação/publicação do vídeo é ação humana**
   (DD-F4-5), com o **placeholder de link** no README (T7) a preencher após a publicação.

Verificação final: **checklist marcado/justificado** e **gate verde** num clone limpo (T8), com STATE e
`docs/04` atualizados (T9). Itens dependentes de ação humana (vídeo) ou de ambiente (PDF, deploy Azure)
**não bloqueiam** o fechamento do planejamento/empacotamento — entram com roteiro/fallback documentados.
