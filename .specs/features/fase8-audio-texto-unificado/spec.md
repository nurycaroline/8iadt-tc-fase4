# Fase 8 — Áudio/Texto Unificado (depressão e violência) — Especificação

> **Status: IMPLEMENTADA.** Especificação seguindo a skill
> [`tlc-spec-driven`](../../../.cursor/skills/tlc-spec-driven/SKILL.md). Visão macro em
> [`docs/11-fase8-audio-texto-unificado.md`](../../../docs/11-fase8-audio-texto-unificado.md).
>
> ✅ **Escopo confirmado pelo pedido "implemente a Fase 8".** Aprofunda os requisitos de **Análise de
> Áudio Especializada** (depressão pós-parto e vítimas de violência) e de **texto**, trocando a
> abordagem por palavras-chave por **classificadores ML locais** em PT-BR e adicionando uma trilha
> **acústica** de violência. Tudo **local/offline** (sem Azure). **Gate verde:** `ruff` + `pytest`
> (**129 testes** Python, +17). Os pesos não são versionados (só métricas/amostras) e tudo
> **degrada por keywords** sem os modelos (DD10).

## Problem Statement

A solução analisava áudio e texto por **motores separados** e **palavras-chave**, com lacunas:

1. **Áudio sem modelo acústico** — a "classificação de áudio" rodava só sobre a **transcrição**
   (keywords). A violência no **som** (tom, grito, contexto) não era observada.
2. **Texto sem violência** e com **depressão dentro de `complicacao`** — `app/texto/nlp.py` não
   detectava violência e a depressão caía em `complicacao` (keyword), arriscando **dupla contagem**
   com o áudio na fusão.
3. **Dependência de Azure** documentada (Speech-to-Text / Text Analytics) — o projeto quer rodar
   **100% local/offline**.

A Fase 8 fecha essas lacunas com classificadores **ML treinados em PT-BR** (datasets EN traduzidos
offline), uma trilha **acústica** própria e a remoção das citações a Azure nos módulos reescritos.

## Goals

- [x] **Áudio com análise dupla:** classificador **acústico** de violência (`scikit-learn` sobre
      features MFCC) **e** transcrição reanalisada como texto unificado.
- [x] **Texto unificado:** depressão (ML) + violência (ML) + infecção/complicação (keywords
      preservadas); depressão **sai** de `complicacao` para o sinal dedicado.
- [x] **Pipeline de dados local:** download dos 3 datasets HF + **tradução EN→PT offline** (Argos
      padrão; X-ALMA opcional) + geração de **negativos** de violência.
- [x] **Schema/contrato** estendido (texto: `depressao`/`violencia`; áudio: `acustico`/`transcricao`/
      `texto` + legado **derivado**), com validação e testes.
- [x] **Fusão/limiares** com novos gatilhos (violência acústica `≥0.7`; violência/depressão no
      texto `≥0.6`), **sem regressão**.
- [x] **Sem Azure** nos módulos de áudio/texto reescritos; tudo offline.
- [x] **Gate verde** e **degradação graciosa** (fallback por keywords quando os modelos faltam).

## Out of Scope

| Item | Motivo |
| --- | --- |
| **Download em massa e treino pesado em nuvem** | Tudo roda **local** (mini-dataset). HF na 1ª vez; offline depois |
| **Baixar o X-ALMA 13B no fluxo padrão** | Argos é o default (CPU/MIT); X-ALMA fica **estruturado/opcional** por env |
| **Versionar dados/pesos** | Política do repo: só **métricas/amostras** (`metrics.json`, `*.png`) |
| **Reabrir o contrato/fusão como motor end-to-end** | Mantém-se o **motor de regras**; campos novos + legado derivado, sem quebra |
| **Deploy/escala** | Continua nas Fases 5+ |

## User Stories

### P1: Análise dupla de áudio (acústico + transcrição→texto) ⭐ MVP

**Acceptance Criteria**:

1. WHEN um áudio é submetido THEN o sistema SHALL rodar a trilha **acústica** (violência no som) e a
   **transcrição→texto unificado**, devolvendo `{acustico, transcricao, texto, categoria, confianca}`.
2. WHEN o **modelo acústico não existe** THEN a trilha acústica SHALL degradar para `neutro` sem
   quebrar, e a violência ainda SHALL ser captada pela trilha de texto (DD10).
3. WHEN a categoria legada é necessária (fusão/relatório) THEN ela SHALL ser **derivada** da análise
   dupla, mantendo a compatibilidade.

### P1: Texto unificado (depressão ML + violência ML + keywords) ⭐ MVP

**Acceptance Criteria**:

1. WHEN um texto é analisado THEN a evidência SHALL conter `achado`+`trecho` (keywords) e as
   subevidências `depressao` e `violencia` (ML ou fallback por keywords).
2. WHEN os classificadores ML estão presentes THEN a depressão/violência SHALL vir do **modelo**;
   caso contrário, do **fallback por palavras-chave**.
3. WHEN o texto cita depressão THEN o achado clínico **não** SHALL mais ser `complicacao` por esse
   motivo (depressão vive em `texto.depressao`).

### P2: Pipeline de dados local (download + tradução + negativos)

**Acceptance Criteria**:

1. WHEN o pipeline roda THEN ele SHALL baixar os 3 datasets HF, **traduzir EN→PT offline** (Argos) e
   **gerar negativos** de violência (neutros do ShreyaR + textos clínicos neutros).
2. WHEN a saída já existe THEN o pipeline SHALL ser **idempotente** (não retrabalhar).
3. WHEN a rede do HF está indisponível THEN o passo SHALL **avisar e seguir** (não travar) e os
   dados/pesos **não** SHALL ser versionados.

### P2: Treino dos classificadores (texto e acústico)

**Acceptance Criteria**:

1. WHEN há dados preparados THEN os treinos SHALL produzir artefatos `joblib` em `models/` e
   **métricas** (F1, matriz de confusão) em `metrics.json`.
2. WHEN o conjunto é pequeno THEN o treino SHALL funcionar (avaliação in-sample) — filosofia
   mini-dataset; **não** exige treino pesado para "concluir".

### P2: Fusão e limiares com os novos sinais

**Acceptance Criteria**:

1. WHEN a violência acústica tem confiança `≥ 0.7` **ou** a violência no texto (ML) tem `≥ 0.6` THEN
   a fusão SHALL acionar o protocolo de proteção (`ALTO`), mesmo isolada.
2. WHEN a depressão no texto (ML) tem `≥ 0.6` THEN a fusão SHALL elevar para `≥ MEDIO`
   (desconforto psicológico).
3. WHEN as evidências legadas chegam (formato pré-Fase 8) THEN a fusão SHALL continuar funcionando
   (sem regressão).

## Edge Cases

- WHEN os **modelos ML faltam** THEN texto/áudio degradam para **keywords** (DD10), sem quebrar.
- WHEN o **ASR falha** THEN a transcrição fica vazia e segue só a trilha acústica.
- WHEN o **pacote Argos `en→pt`** não está instalado THEN o pipeline o **baixa uma vez**; sem rede,
  avisa e não trava a tarefa.
- WHEN o dataset acústico vem com rótulo `Nonvoilence` (*sic*) THEN ele SHALL ser normalizado para 0.

## Requirement Traceability

| ID | Story | Phase | Status | Evidência |
| --- | --- | --- | --- | --- |
| F8-01 | Deps locais | Execute | **Implementado** | `ai-service/requirements.txt`, `scripts/requirements-data.txt` |
| F8-02 | Pipeline de dados + tradução + negativos | Execute | **Implementado** | `scripts/data_prep/fase8_datasets.py`, `scripts/data_prep/traducao.py` |
| F8-03 | Schema (texto/áudio) + validação | Execute | **Implementado** | `ai-service/app/schemas.py`, `tests/test_schemas.py` |
| F8-04 | Treino texto (depressão/violência) | Execute | **Implementado** | `ai-service/app/texto/treino.py`, `tests/test_treino_fase8.py` |
| F8-05 | Treino acústico (violência) | Execute | **Implementado** | `ai-service/app/audio/treino.py`, `ai-service/app/audio/features.py` |
| F8-06 | Áudio dupla | Execute | **Implementado** | `ai-service/app/audio/classificacao.py`, `tests/test_audio_classificacao.py` |
| F8-07 | Texto unificado | Execute | **Implementado** | `ai-service/app/texto/nlp.py`, `tests/test_texto_nlp.py` |
| F8-08 | Fusão + limiares | Execute | **Implementado** | `ai-service/app/fusao.py`, `ai-service/app/limiares.py`, `tests/test_fusao.py` |
| F8-09 | Testes | Execute | **Implementado** | +17 testes (`ruff`+`pytest` verdes, 129) |
| F8-10 | Docs | Execute | **Implementado** | `docs/11-…`, `datasets.md`, `02-fase2`, `contrato-api`, `PLANO`, `STATE` |

**ID format:** `F8-[NUMBER]` (Fase 8). **Coverage:** 10 requisitos — **10 implementados**.

## Decisões a confirmar com o grupo

> Conforme `AGENTS.md` (Princípio 1). Como o pedido foi **"implemente a Fase 8"**, resolvidas com os
> **defaults propostos** (✅ aplicados) — revisáveis.

1. **Negativos de violência (texto):** ✅ neutros (`is_depression=0`) do **ShreyaR** traduzidos +
   textos clínicos **neutros** de `data/texto_clinico/`.
2. **Tradução EN→PT:** ✅ **Argos Translate** (CPU, MIT) como **padrão**; **X-ALMA** preferencial
   **selecionável por env** (`TRADUCAO_BACKEND=xalma`), apenas estruturado — não baixa o 13B no
   fluxo padrão.
3. **Categorias antigas de áudio:** ✅ **mantidas por compatibilidade** e **derivadas** da análise
   dupla (não classificadas por keyword) — não quebra fusão/testes.
4. **Localização das deps de dados (`datasets`/`huggingface-hub`):** ✅ em
   `scripts/requirements-data.txt` (separação S2 — Fase 1/data prep), enquanto `argostranslate`/
   `librosa`/`faster-whisper`/`sentence-transformers` ficam em `ai-service/requirements.txt`
   (treino/inferência/tradução). **Revisável** se o grupo preferir tudo num arquivo só.

## Success Criteria

- [x] Áudio com análise dupla; texto unificado; sem Azure nos módulos reescritos.
- [x] Pipeline de dados idempotente, offline após download, tolerante a falha de rede.
- [x] Schema/contrato estendido com validação e testes; fusão/limiares com novos gatilhos.
- [x] Gate verde (`ruff`+`pytest`, 129) e degradação graciosa sem os modelos.
- [x] STATE/docs atualizados (Fase 8 registrada; decisões com defaults).
