# Fase 1 — Aquisição e Preparação de Dados — Tasks

**Spec**: [`spec.md`](spec.md)
**Design**: [`design.md`](design.md)
**Status**: Done (implementado em `scripts/data_prep/` + `data/`; gate `ruff` + `pytest` verde, 12 testes)

> Cada tarefa = 1 entregável atômico (um arquivo/uma função/uma capacidade), com `Done when` testável
> e um commit. Funções puras carregam testes na própria tarefa (co-located), conforme `design.md` §6.

---

## Execution Plan

### Fase A: Fundação (Sequencial)

Layout, gitignore e utilidades compartilhadas vêm antes de tudo.

```
T1 → T2 → T3 → T4
```

### Fase B: Modalidades (Paralelizável)

Após a fundação, cada modalidade é independente (uma por sub-agente).

```
            ┌→ T5  (sinais vitais) [P]
            ├→ T6  (cicatriz YOLO) [P]
T4 ─────────┼→ T7  (áudio)         [P]
            ├→ T8  (texto clínico) [P]
            └→ T9  (fisioterapia)  [P]
```

### Fase C: Integração (Sequencial)

O caso sintético consome as saídas das modalidades.

```
T5, T6, T7, T8 → T10 → T11
```

---

## Task Breakdown

### T1: Criar estrutura de pastas `data/` + `.gitignore`

**What**: Criar o layout de `data/` (com `.gitkeep`) e um `.gitignore` que ignora dados mas versiona metadados permitidos.
**Where**: `.gitignore`, `data/**/.gitkeep`
**Depends on**: None
**Reuses**: Layout de `PLANO_DE_DESENVOLVIMENTO.md` §7
**Requirement**: F1D-01, F1D-02

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Existem `data/{sinais_vitais,video_cicatriz,video_fisioterapia,audio,texto_clinico,casos}/` com `.gitkeep`.
- [ ] `.gitignore` ignora `data/**` exceto `.gitkeep`, `data/README.md` e arquivos de metadados (`*.json` de rótulos/casos definidos).
- [ ] `git status` não lista arquivos de dados de exemplo criados manualmente.

**Tests**: none · **Gate**: build
**Commit**: `chore(data): estrutura de pastas e gitignore da Fase 1`

---

### T2: README de dados (origem + licença + como obter)

**What**: Criar `data/README.md` com tabela de origem/licença e instruções de download por modalidade.
**Where**: `data/README.md`
**Depends on**: T1
**Reuses**: `docs/datasets.md`
**Requirement**: F1D-03

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Tabela com dataset, origem (link), licença e o que baixar (amostra) para as 4 modalidades.
- [ ] Instruções de obtenção manual para o caso de o download automático falhar.
- [ ] Nota de limitações (AZH não é de cesárea; sem base de depressão pós-parto).

**Tests**: none · **Gate**: build
**Commit**: `docs(data): README com origem, licença e obtenção dos datasets`

---

### T3: Dependências de preparação de dados

**What**: Criar `scripts/requirements-data.txt` com os pacotes do `design.md` §2 (última versão estável).
**Where**: `scripts/requirements-data.txt`
**Depends on**: T1
**Reuses**: `design.md` §2
**Requirement**: F1D-01

**Tools**: MCP: `context7` (confirmar APIs/pacotes atuais) · Skill: NONE

**Done when**:

- [ ] Lista inclui pandas, requests/ucimlrepo, opencv-python, Pillow, ultralytics, pyyaml, openai-whisper, pytest, ruff.
- [ ] `pip install -r scripts/requirements-data.txt` resolve sem conflito num venv limpo.

**Tests**: none · **Gate**: build
**Commit**: `chore(data): requirements de preparação de dados`

---

### T4: Utilidades compartilhadas (`common.py`)

**What**: Implementar `download()` seguro, resolução de paths, escrita idempotente (JSON/CSV) e logger estruturado.
**Where**: `scripts/data_prep/common.py`, `scripts/data_prep/__init__.py`
**Depends on**: T3
**Reuses**: `design.md` §4.1
**Requirement**: F1D-01

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] `download(url, dest)` grava em arquivo temporário e renomeia ao final; erro claro com instrução manual.
- [ ] `data_dir(modalidade)` cria/resolve caminhos sob `data/`.
- [ ] `write_json`/`write_csv` são idempotentes; `get_logger(case_id)` emite log JSON.
- [ ] Gate check passes: `ruff check scripts`.

**Tests**: none · **Gate**: quick
**Commit**: `feat(data): utilidades compartilhadas de preparação`

---

### T5: Sinais vitais — download, limpeza e amostras [P]

**What**: Script que baixa o Maternal Health Risk, limpa (outliers/unidades/faltantes) e exporta ≥5 amostras rotuladas.
**Where**: `scripts/data_prep/sinais_vitais.py`, `scripts/tests/test_sinais_vitais.py`
**Depends on**: T4
**Reuses**: `common.py`; `docs/datasets.md` §3
**Requirement**: F1D-04, F1D-05

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Baixa o CSV para `data/sinais_vitais/`.
- [ ] `limpar(df)` remove outliers fisiologicamente implausíveis e padroniza unidades (função pura).
- [ ] Exporta `maternal_clean.csv` com ≥5 amostras rotuladas `low/mid/high`.
- [ ] Teste unitário: entrada com outliers conhecidos → descartados; faltantes tratados.
- [ ] Gate check passes: `ruff check scripts && pytest scripts/tests/test_sinais_vitais.py -q`.
- [ ] Test count: ≥3 testes passam.

**Tests**: unit · **Gate**: quick
**Commit**: `feat(data): preparação de sinais vitais (Maternal Health Risk)`

---

### T6: Cicatriz — amostra AZH Wound → YOLOv8 + visualização [P]

**What**: Script que baixa 1 amostra do AZH Wound, converte para formato YOLOv8 (`ferida_ok`/`ferida_alerta`), gera `data.yaml` e salva imagem anotada.
**Where**: `scripts/data_prep/cicatriz_yolo.py`, `scripts/tests/test_cicatriz_yolo.py`
**Depends on**: T4
**Reuses**: `common.py`; `docs/datasets.md` §1
**Requirement**: F1D-06, F1D-07, F1D-08

**Tools**: MCP: `context7` (API Ultralytics atual) · Skill: NONE

**Done when**:

- [ ] Baixa **apenas uma amostra** para `data/video_cicatriz/images/`.
- [ ] `converter_para_yolo()` gera `.txt` normalizado em `labels/` (função pura testável).
- [ ] Gera `data.yaml` válido (2 classes + paths).
- [ ] Salva ≥1 imagem com anotações sobrepostas.
- [ ] Teste unitário: coords conhecidas → normalização correta; `data.yaml` bem formado.
- [ ] Gate check passes: `ruff check scripts && pytest scripts/tests/test_cicatriz_yolo.py -q`.
- [ ] Test count: ≥3 testes passam.

**Tests**: unit · **Gate**: quick
**Commit**: `feat(data): conversão da amostra de cicatriz para formato YOLOv8`

---

### T7: Áudio — coleta + transcrição + rótulos [P]

**What**: Script que reúne 5 áudios das categorias-alvo, transcreve (Whisper) e grava metadados rotulados.
**Where**: `scripts/data_prep/audio_transcrever.py`
**Depends on**: T4
**Reuses**: `common.py`; `docs/datasets.md` §4
**Requirement**: F1D-11, F1D-12

**Tools**: MCP: `context7` (API Whisper atual) · Skill: NONE

**Done when**:

- [ ] 5 áudios cobrindo `depressao_pos_parto`, `ansiedade`, `neutro`, `violencia`, `fadiga` em `data/audio/`.
- [ ] Transcreve cada áudio (Whisper local; backend Azure trocável por env var).
- [ ] `data/audio/metadados.json` com `[{arquivo, transcricao, categoria}]`.
- [ ] Gate check passes: `ruff check scripts`.

**Tests**: none · **Gate**: quick
**Commit**: `feat(data): coleta e transcrição de áudios com rótulos`

---

### T8: Texto clínico — documentos + rótulos [P]

**What**: Gerar/reunir ~5 documentos de texto clínico em texto simples e marcar achados de risco.
**Where**: `scripts/data_prep/texto_clinico.py`, `data/texto_clinico/`
**Depends on**: T4
**Reuses**: `common.py`; `docs/datasets.md` §5
**Requirement**: F1D-13

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] ~5 documentos com achados normais e de risco (PA alta, proteinúria, febre/dor na cicatriz).
- [ ] `data/texto_clinico/rotulos.json` com `[{arquivo, achado, trechos}]` (`complicacao`/`sinal_infeccao`/`neutro`).
- [ ] Gate check passes: `ruff check scripts`.

**Tests**: none · **Gate**: quick
**Commit**: `feat(data): documentos de texto clínico rotulados`

---

### T9: Fisioterapia — amostras preparadas para pose [P] (P3)

**What**: Script que baixa amostras de exercícios e prepara para YOLOv8-pose, com rótulo correto/incorreto.
**Where**: `scripts/data_prep/fisioterapia_pose.py`
**Depends on**: T4
**Reuses**: `common.py`; `docs/datasets.md` §2
**Requirement**: F1D-14

**Tools**: MCP: `context7` (API Ultralytics pose) · Skill: NONE

**Done when**:

- [ ] Baixa amostras de exercícios para `data/video_fisioterapia/`.
- [ ] Prepara keypoints (reaproveita os fornecidos quando existirem).
- [ ] Rotula repetições `correto`/`incorreto`.
- [ ] Gate check passes: `ruff check scripts`.

**Tests**: none · **Gate**: quick
**Commit**: `feat(data): preparação de amostras de fisioterapia para pose`

---

### T10: Caso sintético — builder conforme contrato de API

**What**: Implementar a montagem de um pacote de caso (JSON) juntando 1 amostra de cada modalidade, conforme o objeto de requisição do contrato.
**Where**: `scripts/data_prep/caso_sintetico.py`, `scripts/tests/test_caso_sintetico.py`
**Depends on**: T5, T6, T7, T8
**Reuses**: `common.py`; `docs/contrato-api.md` §1
**Requirement**: F1D-09

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] `montar_caso(...)` produz JSON com `case_id`, `paciente` e referências por modalidade (função pura).
- [ ] Modalidade ausente → campo omitido sem erro.
- [ ] Teste unitário: JSON conforme schema do contrato; campo opcional omitido corretamente.
- [ ] Gate check passes: `ruff check scripts && pytest scripts/tests/test_caso_sintetico.py -q`.
- [ ] Test count: ≥3 testes passam.

**Tests**: unit · **Gate**: quick
**Commit**: `feat(data): builder do caso de exemplo sintético`

---

### T11: Caso sintético — variantes BAIXO/MÉDIO/ALTO

**What**: Gerar os 3 casos coerentes (normal, risco isolado, multi-risco) em `data/casos/`.
**Where**: `scripts/data_prep/caso_sintetico.py` (modificar), `scripts/tests/test_caso_sintetico.py` (modificar)
**Depends on**: T10
**Reuses**: `montar_caso()` de T10; `docs/contrato-api.md` §3-4
**Requirement**: F1D-10

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Gera `data/casos/caso_baixo.json`, `caso_medio.json`, `caso_alto.json` coerentes.
- [ ] Cada variante referencia arquivos existentes em `data/`.
- [ ] Teste unitário: cada variante tem as evidências esperadas (ex.: ALTO = cicatriz alerta + PA alta).
- [ ] Gate check passes: `ruff check scripts && pytest scripts/tests/test_caso_sintetico.py -q`.
- [ ] Test count: ≥3 testes passam (cobrindo as 3 variantes).

**Tests**: unit · **Gate**: quick
**Commit**: `feat(data): variantes BAIXO/MÉDIO/ALTO do caso sintético`

---

## Parallel Execution Map

```
Fase A (Sequencial):
  T1 → T2 → T3 → T4

Fase B (Paralela, após T4):
  ├── T5 [P]  (sinais vitais)
  ├── T6 [P]  (cicatriz)
  ├── T7 [P]  (áudio)
  ├── T8 [P]  (texto)
  └── T9 [P]  (fisioterapia, P3)

Fase C (Sequencial, após T5+T6+T7+T8):
  T10 → T11
```

**Restrição de paralelismo**: T5–T9 escrevem em diretórios distintos de `data/` e arquivos distintos
em `scripts/data_prep/` — sem estado mutável compartilhado, logo `[P]` é seguro. T9 (fisio) é P3 e pode
ser adiada sem bloquear T10 (o builder lida com modalidade ausente). T10/T11 editam o mesmo arquivo →
sequenciais.

---

## Task Granularity Check

| Task | Escopo                                   | Status      |
| ---- | ---------------------------------------- | ----------- |
| T1   | layout + 1 arquivo (.gitignore)          | ✅ Granular |
| T2   | 1 arquivo (README)                       | ✅ Granular |
| T3   | 1 arquivo (requirements)                 | ✅ Granular |
| T4   | 1 módulo de utilidades                   | ✅ Granular |
| T5   | 1 script + 1 teste                       | ✅ Granular |
| T6   | 1 script + 1 teste                       | ✅ Granular |
| T7   | 1 script                                 | ✅ Granular |
| T8   | 1 script                                 | ✅ Granular |
| T9   | 1 script                                 | ✅ Granular |
| T10  | 1 função builder + 1 teste               | ✅ Granular |
| T11  | variantes na mesma função + teste        | ✅ Granular |

---

## Diagram-Definition Cross-Check

| Task | Depends On (body) | Diagrama mostra | Status   |
| ---- | ----------------- | --------------- | -------- |
| T1   | None              | (raiz)          | ✅ Match |
| T2   | T1                | T1→T2           | ✅ Match |
| T3   | T1                | T2→T3 (cadeia)  | ✅ Match |
| T4   | T3                | T3→T4           | ✅ Match |
| T5   | T4                | T4→T5           | ✅ Match |
| T6   | T4                | T4→T6           | ✅ Match |
| T7   | T4                | T4→T7           | ✅ Match |
| T8   | T4                | T4→T8           | ✅ Match |
| T9   | T4                | T4→T9           | ✅ Match |
| T10  | T5,T6,T7,T8       | (T5..T8)→T10    | ✅ Match |
| T11  | T10               | T10→T11         | ✅ Match |

> Nota: T2 e T3 ambos dependem apenas de T1 (poderiam ser `[P]`); foram mantidos em cadeia na Fase A
> por serem rápidos e sequenciais de fundação. Nenhum deles é marcado `[P]`, então não há conflito.

---

## Test Co-location Validation

| Task | Camada criada/modificada       | Matriz exige | Tarefa diz | Status |
| ---- | ------------------------------ | ------------ | ---------- | ------ |
| T1   | config (gitignore/estrutura)   | none         | none       | ✅ OK  |
| T2   | docs                           | none         | none       | ✅ OK  |
| T3   | config (requirements)          | none         | none       | ✅ OK  |
| T4   | utilidades IO/rede             | none (DD5)   | none       | ✅ OK  |
| T5   | função pura `limpar`/outliers  | unit         | unit       | ✅ OK  |
| T6   | função pura normalização/yaml  | unit         | unit       | ✅ OK  |
| T7   | script IO/ASR                  | none (DD5)   | none       | ✅ OK  |
| T8   | geração/IO de texto            | none (DD5)   | none       | ✅ OK  |
| T9   | script IO/pose                 | none (DD5)   | none       | ✅ OK  |
| T10  | função pura builder            | unit         | unit       | ✅ OK  |
| T11  | função pura (variantes)        | unit         | unit       | ✅ OK  |

> Justificativa de `none`: T4/T7/T8/T9 são predominantemente IO/rede/geração (DD5 em `design.md`); a
> lógica determinística testável está concentrada em T5, T6, T10 e T11.

---

## Gate de fim da Fase 1

Conforme `docs/cronograma-dependencias.md` §4: **mini-dataset (5 por modalidade) + caso de exemplo
sintético pronto**. Equivale a concluir T1–T8, T10, T11 (T9 é P3/opcional para o gate).
