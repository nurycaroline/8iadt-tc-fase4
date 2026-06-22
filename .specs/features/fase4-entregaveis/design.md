# Fase 4 — Empacotamento e Entregáveis — Design

> Como vamos produzir o que o [`spec.md`](spec.md) descreve. Esta fase **não cria código de produto**:
> ela **empacota, documenta e evidencia** a solução das Fases 1–3. Alinha-se a
> [docs/04](../../../docs/04-fase4-entregaveis.md), ao [checklist](../../../docs/05-checklist-entrega.md),
> ao template de [relatórios](../../../docs/06-relatorios-automaticos.md), à
> [privacidade/LGPD](../../../docs/07-privacidade-e-seguranca.md), à
> [arquitetura](../../../docs/arquitetura.md) e à [qualidade/CI](../../../docs/qualidade-testes-ci.md).

## 1. Visão geral

A Fase 4 produz **três entregáveis** a partir de artefatos que **já existem** no repositório:

```
                         ┌──────────────────── Artefatos já existentes (Fases 1–3) ───────────────────┐
                         │ models/metricas_fusao.json · models/sinais_vitais/{metrics.json,            │
                         │ matriz_confusao.png} · models/cicatriz/metrics.json · models/baseline.json  │
                         │ app/relatorio.py (exemplo) · scripts/e2e_demo.py (logs) · docs/* · .specs/* │
                         └───────────────┬───────────────────────────┬──────────────────┬─────────────┘
                                         │                           │                  │
                          consolida      ▼          escreve          ▼      roteiriza    ▼
        ┌──────────────── Evidências ────────────┐  ┌─ Relatório técnico ─┐  ┌─ Roteiro de vídeo ─┐
        │ docs/relatorio/ (exemplo de relatório,  │  │ docs/relatorio-     │  │ docs/roteiro-       │
        │ tabela de métricas, prints/logs E2E)    │──►│ tecnico.md (6 seções)│ │ video.md (8 pontos) │
        └─────────────────────────────────────────┘  └──────────┬──────────┘  └─────────┬──────────┘
                                                                 │ exporta (fallback)     │ grava (humano)
                                                                 ▼                        ▼
                                                        docs/relatorio-tecnico.pdf   Vídeo "Não listado"
                                                                                          │ link
                          ┌──────────────── Repositório auditado (4.1) ──────────────────┘
                          │ README (execução do zero + créditos + link do vídeo) · .gitignore · disclaimer
                          │ gate verde (ruff+pytest / eslint+jest) · checklist de entrega
                          └─────────────────────────────────────────────────────────────────────────────
```

**Princípio guia (do `AGENTS.md`):** **nunca inventar** números. Toda métrica/afirmação do relatório
**aponta para um artefato de origem** no repositório. Onde o ambiente degrada (cicatriz em smoke,
áudio/fisioterapia sem dados), o relatório **documenta a limitação honestamente** (DD10 da Fase 3).

## 2. Stack e ferramentas

Esta fase é majoritariamente **documentação**. Não adiciona dependências de produto. Ferramentas usadas:

| Finalidade                         | Ferramenta                              | Observação                                            |
| ---------------------------------- | --------------------------------------- | ----------------------------------------------------- |
| Geração do exemplo de relatório    | `ai-service/app/relatorio.py` (Fase 3)  | Reuso — não reescrever                                |
| Evidência ponta-a-ponta            | `scripts/e2e_demo.py` (Fase 3)          | Rodar e capturar log com `case_id`                    |
| Exportação Markdown → PDF          | `markdown` + `weasyprint` (já em `requirements.txt`) **ou** `pandoc` | Fallback p/ HTML/Markdown se ausente (DD-F4-2) |
| Diagramas                          | `mermaid-studio` (skill, **se instalada**) ou Mermaid inline | Recomendação única se ausente (DD-F4-3)      |
| Gate de qualidade                  | `ruff`, `pytest`, `eslint`, `jest`      | Já configurados (Fases 2–3) — apenas verificar verde  |
| Versões de libs                    | `context7` / registries                 | Confirmar antes de fixar qualquer versão nova (raro aqui) |

> Não se prevê novas dependências de produto. Se a exportação para PDF exigir uma lib nova, confirmar a
> **última estável** via `context7` (princípio do `AGENTS.md`) — mas o caminho preferido é reusar o que
> `app/relatorio.py` já usa.

## 3. Estrutura de arquivos (a criar / atualizar)

```
docs/
├── relatorio-tecnico.md          # ENTREGÁVEL 4.2 — 6 seções do PDF (F4E-04..F4E-09)
├── roteiro-video.md              # ENTREGÁVEL 4.3 — roteiro dos 8 pontos (F4E-11)
├── relatorio-tecnico.pdf         # exportação (gerado; opcional/fallback) (F4E-10)
├── relatorio/                    # evidências consolidadas p/ o relatório (F4E-02)
│   ├── exemplo-relatorio-automatico.md (+ .html)   # gerado por app/relatorio.py sobre data/casos/caso_alto.json
│   ├── metricas-fusao.md         # tabela legível derivada de models/metricas_fusao.json
│   └── e2e-log.txt               # trecho do log do scripts/e2e_demo.py com case_id
├── 04-fase4-entregaveis.md       # marcar itens do DoD ao fechar (F4E-14)
└── 05-checklist-entrega.md       # percorrer e marcar/justificar (F4E-13)

(raiz)
└── README.md                     # execução do zero + créditos/integrantes + link do vídeo (F4E-01, F4E-12)

.specs/project/STATE.md           # registrar a Fase 4 e decisões (F4E-14)

scripts/ (opcional)
└── exportar_relatorio.py         # Markdown → HTML/PDF com fallback (F4E-10) — só se não usar pandoc direto
```

> **Privacidade:** as evidências consolidadas usam **apenas** o caso sintético (`data/casos/*.json`) e
> métricas de datasets públicos — nenhum dado real (LGPD, [docs/07](../../../docs/07-privacidade-e-seguranca.md)).
> Artefatos versionados são **pequenos e legíveis** (Markdown/PNG já existente); o PDF é melhor-esforço.

## 4. Componentes (o conteúdo de cada entregável)

### 4.1 Repositório auditado (F4E-01, F4E-12)

Auditoria contra a [Tarefa 4.1](../../../docs/04-fase4-entregaveis.md) e o
[checklist](../../../docs/05-checklist-entrega.md), corrigindo lacunas:

- **Estrutura**: confirmar `/ai-service`, `/backend`, `/docs`, `/scripts` (já existem).
- **Dependências**: `ai-service/requirements.txt` e `backend/package.json` com **versões fixadas**
  (já feito na Fase 3 — apenas conferir).
- **README**: validar o passo a passo "do zero" (Docker e local); adicionar **seção de créditos/integrantes**
  e um **placeholder do link do vídeo** claramente marcado.
- **`.gitignore`**: confirmar `data/`, `.env`, pesos/`runs/` cobertos; decisão **pesos via métricas** (não LFS)
  registrada (alinha com STATE).
- **Disclaimer ético**: já presente no README; garantir que aparece também no relatório técnico.

### 4.2 Evidências consolidadas (F4E-02)

Reaproveitar artefatos **reais** (sem regerar treino):

- `models/metricas_fusao.json` → tabela legível em `docs/relatorio/metricas-fusao.md`.
- `models/sinais_vitais/metrics.json` + `matriz_confusao.png` → citados na seção de resultados.
- `models/cicatriz/metrics.json` (mAP do smoke) e `models/baseline.json` → citados, com a ressalva de smoke.
- **Exemplo de relatório automático**: rodar `app/relatorio.py` sobre `data/casos/caso_alto.json` e salvar
  o Markdown/HTML em `docs/relatorio/exemplo-relatorio-automatico.md` (Tarefa 4.2 item 6).
- **Log E2E**: rodar `scripts/e2e_demo.py`, capturar o trecho com `case_id` em `docs/relatorio/e2e-log.txt`.

### 4.3 Relatório técnico — `docs/relatorio-tecnico.md` (F4E-04..F4E-09)

Estrutura fixa (espelha [docs/04 §4.2](../../../docs/04-fase4-entregaveis.md)):

1. **Fluxo multimodal + arquitetura** (F4E-04): contexto clínico (pós-parto), as 4 modalidades, o diagrama
   (de §4 deste design) e o fluxo upload → storage → IA → fusão → alerta/relatório.
2. **Modelos por modalidade + justificativas** (F4E-05): cicatriz (**YOLOv8** — detecção), fisioterapia
   (**YOLOv8-pose** — keypoints), sinais vitais (**Random Forest**, Isolation Forest opcional), áudio
   (transcrição + classificação), texto (**NLP por regras/palavras-chave**). Justificar **por que** cada
   escolha (maturidade do ecossistema, explicabilidade, dados tabulares) — reusa as decisões da
   [Fase 2 design](../fase2-modelos/design.md).
3. **Lógica de fusão + ganho** (F4E-06): o **motor de regras** (matriz base do
   [contrato §4](../../../docs/contrato-api.md) + regras de elevação), exemplos de gatilhos, e a **tabela
   comparativa** fusão × só-vídeo × só-vitais × só-áudio/texto (de `metricas_fusao.json`) com a conclusão
   (redução de FP / aumento de recall).
4. **Resultados e anomalias** (F4E-07): métricas reais (acurácia/F1 dos vitais + matriz de confusão; mAP da
   cicatriz; baseline por modalidade), prints do alerta/E2E, e **exemplos de anomalias** detectadas
   (caso_alto → ALTO). **Limitações** documentadas (smoke da cicatriz; modalidades que degradam sem dados).
5. **Privacidade e segurança (LGPD)** (F4E-08): princípios e controles de
   [docs/07](../../../docs/07-privacidade-e-seguranca.md) + dados sintéticos como estratégia + disclaimer.
6. **Exemplo de relatório automático** (F4E-09): embutir/linkar `docs/relatorio/exemplo-relatorio-automatico.md`.

Cada afirmação técnica leva **link para a origem** (`docs/`, `.specs/`, arquivo de métrica).

### 4.4 Exportação para PDF (F4E-10)

- Caminho preferido: reusar a abordagem de `app/relatorio.py` (`markdown` → HTML → `weasyprint`) num
  pequeno utilitário/instrução, ou `pandoc docs/relatorio-tecnico.md -o docs/relatorio-tecnico.pdf`.
- **Fallback (DD-F4-2)**: se as libs/sistema não estão disponíveis, manter HTML/Markdown e documentar no
  README como gerar o PDF localmente. Não bloqueia a entrega.

### 4.5 Roteiro de vídeo — `docs/roteiro-video.md` (F4E-11)

Tabela bloco a bloco (≤15 min) com os **8 pontos** de [docs/04 §4.3](../../../docs/04-fase4-entregaveis.md):
para cada bloco — **fala**, **o que mostrar**, **comando** (`docker compose up`, `scripts/e2e_demo.py`,
`POST /analisar` do `caso_alto`, abrir o cliente em `http://localhost:3000/`) e **duração estimada**.
Inclui a **degradação documentada** (sem pesos YOLO/ASR, a fusão decide com vitais+texto) e a instrução de
**publicar "Não listado" + inserir o link no README**.

### 4.6 Diagrama (F4E-03)

Reaproveita os diagramas de [docs/arquitetura.md](../../../docs/arquitetura.md) e
[docs/casos-de-uso.md](../../../docs/casos-de-uso.md). Se `mermaid-studio` estiver instalada → renderizar
(SVG/PNG) e embutir; senão, **Mermaid inline** no relatório (DD-F4-3).

## 5. Decisões de design

| #       | Decisão                                                                      | Justificativa                                                                       |
| ------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| DD-F4-1 | **Relatório em `docs/relatorio-tecnico.md`** (Markdown), PDF como exportação | Sugestão de [docs/04](../../../docs/04-fase4-entregaveis.md); versionável e revisável |
| DD-F4-2 | **PDF com fallback** para HTML/Markdown                                      | Mesma política do relatório automático (Fase 3 DD7); libs de PDF exigem sistema      |
| DD-F4-3 | **Diagramas Mermaid inline**; `mermaid-studio` se instalada                  | Skill não está instalada no ambiente; reusa diagramas já existentes nos docs         |
| DD-F4-4 | **Reusar artefatos reais** (métricas/exemplo/log), **não** regerar treino    | Fase 2/3 já produziram; princípio "não inventar" do `AGENTS.md`                      |
| DD-F4-5 | **Vídeo = roteiro + placeholder de link** (gravação/publicação humana)       | Sem captura/credencial no agente; o entregável "vídeo" depende de ação do grupo      |
| DD-F4-6 | **Limitações documentadas honestamente** (smoke da cicatriz, degradação)     | DD10 da Fase 3; integridade técnica do relatório                                     |
| DD-F4-7 | **Pesos via métricas versionadas** (não Git LFS) no MVP                      | Decisão pendente do grupo no STATE; relatório registra a escolha atual               |
| DD-F4-8 | **Gate verde é critério de fechamento** (rodar num clone limpo)              | Item do checklist; prova de reprodutibilidade                                        |

## 6. Estratégia de testes / verificação

Esta fase produz **documentação**; não há código testável novo. A "verificação" é:

| Item                                  | Tipo            | Como verificar                                                       |
| ------------------------------------- | --------------- | -------------------------------------------------------------------- |
| Exemplo de relatório automático       | execução (smoke)| `app/relatorio.py` sobre `caso_alto` gera o Markdown esperado        |
| Log E2E com `case_id`                 | execução (smoke)| `scripts/e2e_demo.py` roda e o `case_id` aparece no log              |
| Tabela do ganho da fusão              | conferência     | valores batem com `models/metricas_fusao.json`                       |
| Gate de qualidade                     | gate            | `ruff check scripts ai-service` + `pytest -q`; `npm run lint`/`npm test` |
| Links/rastreabilidade do relatório    | revisão         | cada métrica aponta para o artefato de origem                        |
| README "do zero"                      | revisão/smoke   | seguir o passo a passo num clone limpo até o alerta da demo          |

- **Gate Python:** `ruff check scripts ai-service && pytest -q` (deve permanecer verde — 96 testes da Fase 3).
- **Gate Node:** `npm run lint && npm test` (deve permanecer verde — 11 testes da Fase 3).
- **Não** se adicionam testes novos (não há lógica nova); a Fase 4 **não pode regredir** o gate existente.

## 7. Riscos e mitigação

| Risco                                                   | Mitigação na Fase 4                                                            |
| ------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Citar métrica **sem artefato** (fabricação)             | Regra DD-F4-4: toda métrica linka para o arquivo de origem; lacuna é sinalizada |
| Libs de **PDF** ausentes no ambiente                    | Fallback HTML/Markdown (DD-F4-2); instrução de geração local no README          |
| `mermaid-studio` indisponível                           | Mermaid inline (DD-F4-3); recomendação única                                    |
| Ambiente **sem pesos YOLO/ASR** enfraquece a demo       | Documentar a degradação (DD-F4-6); roteiro usa o caminho válido (vitais+texto)  |
| **Vídeo** depende de gravação humana                    | Entregar roteiro + placeholder de link (DD-F4-5); não bloqueia os outros itens  |
| **Deploy Azure** indisponível para a demo               | Descrever integração + fallback local; referenciar `docs/deploy-azure.md`       |
| Relatório **divergir** da implementação real            | Escrever a partir de `.specs/` + código + métricas; revisar contra o repo       |
| Gate **quebrar** por edição acidental                   | Fase só edita docs/README/STATE; rodar o gate antes de fechar (DD-F4-8)         |

## 8. Rastreabilidade design → requisito

| Componente / Entregável                          | Requisito(s)             |
| ------------------------------------------------ | ------------------------ |
| Repositório auditado + README (créditos/link)    | F4E-01, F4E-12           |
| Evidências consolidadas (`docs/relatorio/`)      | F4E-02                   |
| Diagrama de arquitetura/fluxo                    | F4E-03                   |
| `docs/relatorio-tecnico.md` (6 seções)           | F4E-04..F4E-09           |
| Exportação para PDF (com fallback)               | F4E-10                   |
| `docs/roteiro-video.md`                          | F4E-11                   |
| Checklist + gate verde                           | F4E-13                   |
| STATE + docs/04 atualizados                      | F4E-14                   |
