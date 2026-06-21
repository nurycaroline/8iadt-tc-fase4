# Fase 2 — Desenvolvimento dos Modelos Individuais — Tasks

**Spec**: [`spec.md`](spec.md)
**Design**: [`design.md`](design.md)
**Status**: Implementado (T1–T14) em `ai-service/`. Gate verde: `ruff check scripts ai-service` +
`pytest -q` (63 testes). Treinos reais executados: sinais vitais (Random Forest, 451 amostras) e
cicatriz (YOLOv8n smoke, 6 imagens → ONNX). Áudio/fisioterapia degradam sem dados (obtenção manual).

> Cada tarefa = 1 entregável atômico (um arquivo/uma função/uma capacidade), com `Done when` testável
> e um commit. Funções puras carregam testes na própria tarefa (co-located), conforme `design.md` §6.
> Insumo: mini-dataset da Fase 1 em `data/` (não re-baixar — DD2).

---

## Execution Plan

### Fase A: Fundação (Sequencial)

Estrutura do serviço, contrato de saída e limiares vêm antes das modalidades.

```
T1 → T2 → T3 → T4
```

### Fase B: Modalidades (Paralelizável)

Após a fundação, cada modalidade é uma subárvore independente (uma por sub-agente).

```
            ┌→ T5  → T6   (sinais vitais)       [P]
            ├→ T7  → T8 → T9 (cicatriz YOLO)    [P]
T4 ─────────┼→ T10         (texto/NLP)          [P]
            ├→ T11         (áudio)              [P]
            └→ T12         (fisioterapia, P3)   [P]
```

### Fase C: Integração (Sequencial)

O baseline consome as inferências; a documentação consolida métricas/limiares.

```
T6, T9, T10, T11 → T13 → T14
```

---

## Task Breakdown

### T1: `ai-service/requirements.txt` (dependências do serviço de IA)

**What**: Criar `ai-service/requirements.txt` com os pacotes do `design.md` §2 (última estável).
**Where**: `ai-service/requirements.txt`
**Depends on**: None
**Reuses**: `design.md` §2
**Requirement**: F2M-01

**Tools**: MCP: `context7` (confirmar versões/APIs atuais de ultralytics, scikit-learn, whisper) · Skill: NONE

**Done when**:

- [ ] Lista inclui ultralytics, opencv-python, Pillow, onnx, onnxruntime, scikit-learn, pandas, numpy,
      joblib, matplotlib, openai-whisper, pyyaml, pytest, ruff.
- [ ] `pip install -r ai-service/requirements.txt` resolve sem conflito num venv limpo (Python 3.13).

**Tests**: none · **Gate**: build
**Commit**: `chore(ai): requirements do serviço de IA da Fase 2`

---

### T2: Fundação — `common.py` + integração de testes/`.gitignore`

**What**: Criar o pacote `ai-service/app/` com `common.py` (paths `data/`/`models/`, logging, IO de
métricas, matriz de confusão), ignorar pesos em `models/` e integrar os testes ao `pyproject` da raiz.
**Where**: `ai-service/app/__init__.py`, `ai-service/app/common.py`, `ai-service/models/.gitkeep`,
`.gitignore`, `pyproject.toml`
**Depends on**: T1
**Reuses**: `scripts/data_prep/common.py` (padrão de logging/IO); `design.md` §4.1
**Requirement**: F2M-01

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] `models_dir(modalidade)` e `data_dir(modalidade)` resolvem/criam caminhos corretos.
- [ ] `salvar_metricas`/`carregar_metricas` e `salvar_matriz_confusao` funcionam (idempotentes).
- [ ] `.gitignore` ignora `ai-service/models/**` exceto `.gitkeep`, `*.json` de métricas e `*.png`.
- [ ] `pyproject.toml` inclui `ai-service` em `pythonpath` e `ai-service/tests` em `testpaths`.
- [ ] Gate check passes: `ruff check scripts ai-service`.

**Tests**: none · **Gate**: quick
**Commit**: `feat(ai): fundação do serviço de IA (common, models, gitignore, pytest)`

---

### T3: `schemas.py` — dicionários de evidência padronizados

**What**: Implementar os construtores de evidência por modalidade que validam o domínio do contrato.
**Where**: `ai-service/app/schemas.py`, `ai-service/tests/test_schemas.py`
**Depends on**: T2
**Reuses**: `docs/contrato-api.md` §3; `design.md` §4.2
**Requirement**: F2M-02

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Construtores `evidencia_cicatriz/_fisioterapia/_sinais_vitais/_audio/_texto` com valores válidos.
- [ ] Valor fora do domínio → `ValueError`.
- [ ] Teste unitário: valores válidos aceitos; inválidos rejeitados; campos opcionais omitidos.
- [ ] Gate check passes: `ruff check ai-service && pytest ai-service/tests/test_schemas.py -q`.
- [ ] Test count: ≥4 testes passam.

**Tests**: unit · **Gate**: quick
**Commit**: `feat(ai): schemas de evidência alinhados ao contrato de API`

---

### T4: `limiares.py` — gatilhos clínicos (Tarefa 2.7)

**What**: Centralizar os limiares clínicos (PA, confiança mínima, classe de risco) num módulo.
**Where**: `ai-service/app/limiares.py`, `ai-service/tests/test_limiares.py`
**Depends on**: T2
**Reuses**: `docs/02-fase2-modelos.md` (Tarefa 2.7); `design.md` §4.3
**Requirement**: F2M-03

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Constantes `PA_SISTOLICA_ALERTA=140`, `PA_DIASTOLICA_ALERTA=90`, `CONFIANCA_MINIMA=0.7`.
- [ ] `pa_em_alerta(sis, dia)` e `risco_alto_sinais_vitais(...)` implementadas.
- [ ] Teste unitário: 139/89 → não alerta; 140/90 → alerta; confiança 0.69 vs 0.7.
- [ ] Gate check passes: `ruff check ai-service && pytest ai-service/tests/test_limiares.py -q`.
- [ ] Test count: ≥3 testes passam.

**Tests**: unit · **Gate**: quick
**Commit**: `feat(ai): limiares clínicos centralizados (Tarefa 2.7)`

---

### T5: Sinais vitais — treino + métricas + persistência [P]

**What**: Treinar Random Forest sobre `maternal_clean.csv`, avaliar (acurácia/F1/matriz de confusão) e
persistir o modelo + métricas.
**Where**: `ai-service/app/sinais_vitais/__init__.py`, `ai-service/app/sinais_vitais/treino.py`
**Depends on**: T4
**Reuses**: `common.py`; `data/sinais_vitais/maternal_clean.csv` (Fase 1); `design.md` §4.4
**Requirement**: F2M-04, F2M-05

**Tools**: MCP: `context7` (API scikit-learn atual) · Skill: NONE

**Done when**:

- [ ] Treina `RandomForestClassifier` com alvo `RiskLevel` e split estratificado robusto a poucos dados.
- [ ] Salva `models/sinais_vitais/{modelo.joblib, metrics.json, matriz_confusao.png}` (acurácia, F1, matriz).
- [ ] Roda como módulo (`python -m app.sinais_vitais.treino`) sem quebrar com amostra pequena.
- [ ] Gate check passes: `ruff check ai-service`.

**Tests**: none · **Gate**: quick
**Commit**: `feat(ai): treino e métricas do modelo de sinais vitais`

---

### T6: Sinais vitais — inferência → dicionário padronizado [P]

**What**: Implementar `prever(registro)` e a derivação pura `derivar_tipo(classe, sis, dia)` → dict do contrato.
**Where**: `ai-service/app/sinais_vitais/inferencia.py`, `ai-service/tests/test_sinais_vitais.py`
**Depends on**: T5
**Reuses**: `schemas.evidencia_sinais_vitais`, `limiares.pa_em_alerta`; `design.md` §4.4
**Requirement**: F2M-06

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] `derivar_tipo` (pura) mapeia classe + PA → `normal/risco_medio/hipertensao/pre_eclampsia`.
- [ ] `prever(registro)` carrega o `.joblib` e devolve `{tipo, valor}` válido; sem modelo → erro/neutro claro.
- [ ] Teste unitário: PA alta → `hipertensao`; classe `high` sem PA → `risco_medio`; `low` → `normal`.
- [ ] Gate check passes: `ruff check ai-service && pytest ai-service/tests/test_sinais_vitais.py -q`.
- [ ] Test count: ≥3 testes passam.

**Tests**: unit · **Gate**: quick
**Commit**: `feat(ai): inferência de sinais vitais com saída padronizada`

---

### T7: Cicatriz — treino YOLOv8 + métricas [P]

**What**: Fine-tuning de YOLOv8n sobre `data/video_cicatriz/data.yaml` e extração de mAP/precisão/recall.
**Where**: `ai-service/app/cicatriz/__init__.py`, `ai-service/app/cicatriz/treino.py`
**Depends on**: T4
**Reuses**: `common.py`; `data/video_cicatriz/` (Fase 1); `design.md` §4.5
**Requirement**: F2M-07, F2M-08

**Tools**: MCP: `context7` (API Ultralytics train/results atual) · Skill: NONE

**Done when**:

- [ ] `python -m app.cicatriz.treino` treina YOLOv8n (poucas épocas) com o `data.yaml` da Fase 1.
- [ ] Extrai **mAP@0.5, precisão, recall por classe** para `models/cicatriz/metrics.json`; copia `best.pt`.
- [ ] `extrair_metricas(results_csv)` é função pura testável.
- [ ] Gate check passes: `ruff check ai-service && pytest ai-service/tests/test_cicatriz.py -q` (métricas).
- [ ] Test count: ≥2 testes passam (parsing de métricas).

**Tests**: unit · **Gate**: quick
**Commit**: `feat(ai): treino e métricas do detector de cicatriz (YOLOv8)`

---

### T8: Cicatriz — export ONNX/PT [P]

**What**: Exportar o melhor modelo treinado para ONNX (fallback `.pt`).
**Where**: `ai-service/app/cicatriz/exportar.py`
**Depends on**: T7
**Reuses**: `models/cicatriz/best.pt`; `design.md` §4.5
**Requirement**: F2M-09

**Tools**: MCP: `context7` (API `YOLO.export` atual) · Skill: NONE

**Done when**:

- [ ] `exportar()` gera `models/cicatriz/best.onnx` (ou mantém `.pt` com erro claro se ONNX falhar).
- [ ] Roda como módulo sem quebrar quando o `best.pt` existe.
- [ ] Gate check passes: `ruff check ai-service`.

**Tests**: none · **Gate**: quick
**Commit**: `feat(ai): export do modelo de cicatriz para ONNX`

---

### T9: Cicatriz — inferência → dicionário padronizado [P]

**What**: `detectar(imagem)` + `mapear_evento(classe, confianca)` puro → dict do contrato.
**Where**: `ai-service/app/cicatriz/inferencia.py`, `ai-service/tests/test_cicatriz.py` (modificar)
**Depends on**: T7
**Reuses**: `schemas.evidencia_cicatriz`, `limiares.CONFIANCA_MINIMA`; `design.md` §4.5
**Requirement**: F2M-10

**Tools**: MCP: `context7` (API `YOLO.predict` atual) · Skill: NONE

**Done when**:

- [ ] `mapear_evento` (puro): `ferida_alerta`+conf≥0.7 → `sinal_infeccao`; `ferida_ok` → `ferida_ok`; baixo → `nenhum`.
- [ ] `detectar(imagem)` devolve `{evento, confianca}` válido; sem pesos → `nenhum` com mensagem clara.
- [ ] Teste unitário: mapeamento e limiar de confiança.
- [ ] Gate check passes: `ruff check ai-service && pytest ai-service/tests/test_cicatriz.py -q`.
- [ ] Test count: ≥3 testes passam (incluindo T7).

**Tests**: unit · **Gate**: quick
**Commit**: `feat(ai): inferência da cicatriz com saída padronizada`

---

### T10: Texto/NLP — análise → dicionário padronizado [P]

**What**: `analisar(texto)` por palavras-chave/regras → `{achado, trecho}`; exemplos sobre os 5 documentos da Fase 1.
**Where**: `ai-service/app/texto/__init__.py`, `ai-service/app/texto/nlp.py`, `ai-service/tests/test_texto_nlp.py`
**Depends on**: T4
**Reuses**: `schemas.evidencia_texto`; `data/texto_clinico/` (Fase 1); `design.md` §4.6
**Requirement**: F2M-11

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] `analisar(texto)` (pura) retorna achado em `complicacao/sinal_infeccao/neutro` + trecho disparador.
- [ ] Executa sobre os 5 documentos e os achados batem com `data/texto_clinico/rotulos.json`.
- [ ] Teste unitário: febre/dor → `sinal_infeccao`; proteinúria/PA alta → `complicacao`; texto limpo → `neutro`.
- [ ] Gate check passes: `ruff check ai-service && pytest ai-service/tests/test_texto_nlp.py -q`.
- [ ] Test count: ≥3 testes passam.

**Tests**: unit · **Gate**: quick
**Commit**: `feat(ai): módulo de texto/NLP com saída padronizada`

---

### T11: Áudio — transcrição + classificação → dicionário padronizado [P] (P2)

**What**: Transcrever (reaproveitando a Fase 1) e classificar a categoria de risco → `{categoria, confianca}`.
**Where**: `ai-service/app/audio/__init__.py`, `ai-service/app/audio/transcricao.py`,
`ai-service/app/audio/classificacao.py`, `ai-service/tests/test_audio_classificacao.py`
**Depends on**: T4
**Reuses**: `scripts/data_prep/audio_transcrever.py` (lógica de transcrição); `schemas.evidencia_audio`; `design.md` §4.7
**Requirement**: F2M-12

**Tools**: MCP: `context7` (API Whisper atual) · Skill: NONE

**Done when**:

- [ ] `classificar(transcricao)` (pura) → categoria em `neutro/ansiedade/depressao_pos_parto/violencia/fadiga` + confiança.
- [ ] Transcrição reaproveita Whisper local (Azure trocável por env); sem áudio → degrada com mensagem clara.
- [ ] Teste unitário: transcrição com termos de violência/depressão → categoria esperada.
- [ ] Gate check passes: `ruff check ai-service && pytest ai-service/tests/test_audio_classificacao.py -q`.
- [ ] Test count: ≥3 testes passam.

**Tests**: unit · **Gate**: quick
**Commit**: `feat(ai): módulo de áudio (transcrição + classificação)`

---

### T12: Fisioterapia — pose + ângulos + execução [P] (P3)

**What**: Extrair keypoints (YOLOv8-pose), derivar ângulos/amplitude (puro) e classificar execução → `{execucao, amplitude}`.
**Where**: `ai-service/app/fisioterapia/__init__.py`, `ai-service/app/fisioterapia/pose.py`,
`ai-service/app/fisioterapia/angulos.py`, `ai-service/app/fisioterapia/inferencia.py`,
`ai-service/tests/test_fisioterapia_angulos.py`
**Depends on**: T4
**Reuses**: `schemas.evidencia_fisioterapia`; `data/video_fisioterapia/` (Fase 1); `design.md` §4.8
**Requirement**: F2M-13

**Tools**: MCP: `context7` (API Ultralytics pose) · Skill: NONE

**Done when**:

- [ ] `angulo(a,b,c)`, `amplitude(serie)`, `classificar_execucao(...)` (puras) implementadas.
- [ ] `avaliar(amostra)` → `{execucao, amplitude}` válido; sem amostra → `nao_avaliado`.
- [ ] Teste unitário: keypoints sintéticos com ângulo conhecido → amplitude/execução esperadas.
- [ ] Gate check passes: `ruff check ai-service && pytest ai-service/tests/test_fisioterapia_angulos.py -q`.
- [ ] Test count: ≥3 testes passam.

**Tests**: unit · **Gate**: quick
**Commit**: `feat(ai): análise de fisioterapia (YOLOv8-pose + execução)`

---

### T13: Baseline por modalidade única

**What**: Rodar cada inferência isolada sobre o mini-dataset/casos, calcular precisão/recall/FP e salvar `baseline.json`.
**Where**: `ai-service/app/baseline.py`, `ai-service/tests/test_baseline.py`
**Depends on**: T6, T9, T10, T11 (T12 opcional)
**Reuses**: inferências das modalidades; rótulos da Fase 1; `design.md` §4.9
**Requirement**: F2M-14

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] `metricas_modalidade(y_true, y_pred)` (pura) calcula precisão, recall e taxa de falsos positivos.
- [ ] `python -m app.baseline` gera `models/baseline.json` por modalidade; modalidade ausente é omitida.
- [ ] Teste unitário: y_true/y_pred conhecidos → métricas esperadas (incl. FP).
- [ ] Gate check passes: `ruff check ai-service && pytest ai-service/tests/test_baseline.py -q`.
- [ ] Test count: ≥2 testes passam.

**Tests**: unit · **Gate**: quick
**Commit**: `feat(ai): baseline por modalidade única`

---

### T14: Documentação — README do serviço + limiares/métricas

**What**: Criar `ai-service/README.md` (como treinar/avaliar cada modelo, onde ficam pesos/métricas) e
registrar os limiares/baseline no docs para o relatório técnico.
**Where**: `ai-service/README.md`, `README.md` (raiz, link), `docs/02-fase2-modelos.md` (referências de saída)
**Depends on**: T13
**Reuses**: `design.md`; `docs/02-fase2-modelos.md` (Tarefa 2.7)
**Requirement**: F2M-15

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] README do serviço explica comandos de treino/inferência por modalidade e a saída padronizada.
- [ ] Tabela de limiares clínicos e a localização das métricas/baseline documentadas.
- [ ] Link do `ai-service/` adicionado ao README/raiz e às referências da Fase 2.

**Tests**: none · **Gate**: build
**Commit**: `docs(ai): README do serviço de IA + limiares/métricas da Fase 2`

---

## Parallel Execution Map

```
Fase A (Sequencial):
  T1 → T2 → T3 → T4

Fase B (Paralela, após T4):
  ├── T5 → T6   [P]  (sinais vitais)
  ├── T7 → T8   [P]  (cicatriz: treino → export)
  │      └→ T9  [P]  (cicatriz: inferência, depende de T7)
  ├── T10       [P]  (texto/NLP)
  ├── T11       [P]  (áudio, P2)
  └── T12       [P]  (fisioterapia, P3)

Fase C (Sequencial, após T6+T9+T10+T11):
  T13 → T14
```

**Restrição de paralelismo**: cada modalidade escreve em subpacote/subpasta distintos de `app/` e
`models/` — sem estado mutável compartilhado, logo `[P]` é seguro entre modalidades. Dentro da cicatriz,
T8 (export) e T9 (inferência) dependem de T7 (treino) mas escrevem arquivos distintos (podem ser `[P]`
entre si após T7). T12 (fisio) é P3 e pode ser adiada sem bloquear T13 (baseline omite modalidade
ausente). T13/T14 são sequenciais (consomem todas as saídas / consolidam docs).

---

## Task Granularity Check

| Task | Escopo                                       | Status      |
| ---- | -------------------------------------------- | ----------- |
| T1   | 1 arquivo (requirements)                     | ✅ Granular |
| T2   | 1 módulo de fundação + config                | ✅ Granular |
| T3   | 1 módulo (schemas) + teste                   | ✅ Granular |
| T4   | 1 módulo (limiares) + teste                  | ✅ Granular |
| T5   | 1 script de treino                           | ✅ Granular |
| T6   | 1 módulo de inferência + teste               | ✅ Granular |
| T7   | 1 script de treino                           | ✅ Granular |
| T8   | 1 script de export                           | ✅ Granular |
| T9   | 1 módulo de inferência + teste               | ✅ Granular |
| T10  | 1 módulo (NLP) + teste                       | ✅ Granular |
| T11  | 2 arquivos (transcrição+classificação)+teste | ✅ Granular |
| T12  | subpacote pose/ângulos + teste               | ✅ Granular |
| T13  | 1 módulo (baseline) + teste                  | ✅ Granular |
| T14  | docs (README + referências)                  | ✅ Granular |

---

## Diagram-Definition Cross-Check

| Task | Depends On (body)   | Diagrama mostra      | Status   |
| ---- | ------------------- | -------------------- | -------- |
| T1   | None                | (raiz)               | ✅ Match |
| T2   | T1                  | T1→T2                | ✅ Match |
| T3   | T2                  | T2→T3                | ✅ Match |
| T4   | T2                  | T3→T4 (cadeia)       | ✅ Match |
| T5   | T4                  | T4→T5                | ✅ Match |
| T6   | T5                  | T5→T6                | ✅ Match |
| T7   | T4                  | T4→T7                | ✅ Match |
| T8   | T7                  | T7→T8                | ✅ Match |
| T9   | T7                  | T7→T9                | ✅ Match |
| T10  | T4                  | T4→T10               | ✅ Match |
| T11  | T4                  | T4→T11               | ✅ Match |
| T12  | T4                  | T4→T12               | ✅ Match |
| T13  | T6,T9,T10,T11       | (B)→T13              | ✅ Match |
| T14  | T13                 | T13→T14              | ✅ Match |

> Nota: T3 e T4 dependem ambos apenas de T2 (poderiam ser `[P]`); mantidos em cadeia na Fase A por serem
> rápidos e de fundação. T8 e T9 dependem de T7 e poderiam rodar `[P]` entre si após o treino.

---

## Test Co-location Validation

| Task | Camada criada/modificada           | Matriz exige | Tarefa diz | Status |
| ---- | ---------------------------------- | ------------ | ---------- | ------ |
| T1   | config (requirements)              | none         | none       | ✅ OK  |
| T2   | utilidades IO/config               | none (DD5)   | none       | ✅ OK  |
| T3   | função pura (schemas)              | unit         | unit       | ✅ OK  |
| T4   | função pura (limiares)             | unit         | unit       | ✅ OK  |
| T5   | treino/IO (sklearn)                | none (DD5)   | none       | ✅ OK  |
| T6   | função pura (derivar_tipo)         | unit         | unit       | ✅ OK  |
| T7   | treino/IO (YOLO) + parsing métrica | unit         | unit       | ✅ OK  |
| T8   | export/IO (ONNX)                   | none (DD5)   | none       | ✅ OK  |
| T9   | função pura (mapear_evento)        | unit         | unit       | ✅ OK  |
| T10  | função pura (NLP)                  | unit         | unit       | ✅ OK  |
| T11  | função pura (classificar)          | unit         | unit       | ✅ OK  |
| T12  | função pura (ângulos)              | unit         | unit       | ✅ OK  |
| T13  | função pura (métricas)             | unit         | unit       | ✅ OK  |
| T14  | docs                               | none         | none       | ✅ OK  |

> Justificativa de `none`: T1/T2/T5/T8 são predominantemente config/IO/treino/rede (DD5 em `design.md`);
> a lógica determinística testável está concentrada nas funções puras (schemas, limiares, derivações,
> mapeamentos, classificadores e métricas).

---

## Gate de fim da Fase 2

Conforme `docs/cronograma-dependencias.md` §4: **4 modelos com métricas individuais**. Equivale a
concluir T1–T11, T13 e T14 (T12 — fisioterapia — é P3/opcional para o gate, mas exigida pelo DoD do
`docs/02-fase2-modelos.md`; deve ser concluída antes do fechamento da fase). Cada modalidade entrega o
**dicionário padronizado** (contrato §3) e suas **métricas próprias**, e o **baseline** fica salvo para
a comparação da fusão na Fase 3.
