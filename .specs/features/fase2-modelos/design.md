# Fase 2 — Desenvolvimento dos Modelos Individuais — Design

> Como vamos construir o que o [`spec.md`](spec.md) descreve. Alinha-se à estrutura de repositório de
> [`PLANO_DE_DESENVOLVIMENTO.md`](../../../PLANO_DE_DESENVOLVIMENTO.md) (§7), à
> [arquitetura](../../../docs/arquitetura.md) (Node + Python/FastAPI) e às boas práticas de
> [`docs/qualidade-testes-ci.md`](../../../docs/qualidade-testes-ci.md).

## 1. Visão geral

A Fase 2 cria o **serviço de IA** (`ai-service/`) e implementa **um módulo por modalidade**. Cada módulo
segue o mesmo contrato interno: `treinar/avaliar (offline) → persistir modelo + métricas em models/ →
expor inferir(...) → dicionário de evidência padronizado`. A **fusão, a API FastAPI e o deploy** ficam
para a Fase 3 — aqui paramos no **dicionário padronizado** de cada modalidade.

```
                 data/  (saídas da Fase 1, consumidas como insumo)
                   │
        ai-service/app/
                   │
  ┌────────┬───────┼─────────┬─────────┬──────────┐
  ▼        ▼       ▼         ▼         ▼          ▼
sinais   cicatriz fisio    audio     texto    (common, schemas, limiares)
vitais   (YOLO)   (pose)   (ASR+cls) (NLP)
  │        │       │         │         │
  └────────┴───────┴────┬────┴─────────┘
                        ▼
   inferir() → dict de evidência (contrato-api §3)  ──►  Fase 3 (fusão)
                        │
                        ▼
                  baseline.py  →  models/baseline.json  (Tarefa 2.6)
```

**Princípio guia (do plano):** "Se rodar com 5, roda com 500." Treinar primeiro no mini-dataset (poucas
épocas / smoke) e só depois escalar (Colab/GPU) — fora do escopo desta fase.

## 2. Stack e dependências

Versões devem ser fixadas pela **última estável** no momento da implementação (princípio do `AGENTS.md`,
confirmar via `context7`); abaixo está apenas o conjunto de pacotes, sem inventar números de versão.

| Finalidade                          | Pacote/Ferramenta              | Usado em                     |
| ----------------------------------- | ------------------------------ | ---------------------------- |
| Detecção/pose de vídeo              | `ultralytics`                  | cicatriz, fisioterapia       |
| Leitura/visualização de imagem      | `opencv-python`, `Pillow`      | cicatriz, fisioterapia       |
| Export de modelo                    | `onnx`, `onnxruntime`          | cicatriz (e fisio opcional)  |
| Modelo tabular + métricas           | `scikit-learn`                 | sinais vitais, baseline      |
| Manipulação tabular/numérica        | `pandas`, `numpy`              | sinais vitais, fisio, baseline |
| Persistência de modelo              | `joblib`                       | sinais vitais                |
| Gráficos (matriz de confusão)       | `matplotlib`                   | métricas                     |
| Transcrição de áudio (ASR)          | `openai-whisper` (local)       | áudio                        |
| Config/leitura YAML                 | `pyyaml`                       | cicatriz (`data.yaml`)       |
| Testes / Lint                       | `pytest` / `ruff`              | funções puras / todos        |

> Linguagem: **Python 3.13** (mantém a decisão DD8 da Fase 1: `openai-whisper` ainda não suporta 3.14).
> As deps do serviço ficam em `ai-service/requirements.txt`, separadas de `scripts/requirements-data.txt`.

## 3. Estrutura de pastas (a criar)

```
ai-service/
├── requirements.txt               # deps do serviço de IA (F2M-01)
├── README.md                      # como treinar/avaliar cada modelo + onde ficam pesos/métricas
├── app/
│   ├── __init__.py
│   ├── common.py                  # paths (data/, models/), logging, IO de métricas (F2M-01)
│   ├── schemas.py                 # construtores dos dicts de evidência (contrato-api §3) (F2M-02)
│   ├── limiares.py                # limiares clínicos / gatilhos (Tarefa 2.7) (F2M-03)
│   ├── sinais_vitais/
│   │   ├── __init__.py
│   │   ├── treino.py              # RandomForest + métricas + joblib (F2M-04, F2M-05)
│   │   └── inferencia.py          # carrega modelo → {tipo, valor} (F2M-06)
│   ├── cicatriz/
│   │   ├── __init__.py
│   │   ├── treino.py              # YOLOv8 fine-tune + métricas mAP/P/R (F2M-07, F2M-08)
│   │   ├── exportar.py            # export ONNX/PT (F2M-09)
│   │   └── inferencia.py          # predict → {evento, confianca} (F2M-10)
│   ├── texto/
│   │   ├── __init__.py
│   │   └── nlp.py                 # keyword/regras → {achado, trecho} (F2M-11)
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── transcricao.py         # whisper/azure (reusa lógica da Fase 1) (F2M-12)
│   │   └── classificacao.py       # keyword/sentimento → {categoria, confianca} (F2M-12)
│   ├── fisioterapia/
│   │   ├── __init__.py
│   │   ├── pose.py                # YOLOv8-pose → keypoints (F2M-13)
│   │   ├── angulos.py             # PURO: ângulos/repetições/amplitude (F2M-13)
│   │   └── inferencia.py          # → {execucao, amplitude} (F2M-13)
│   └── baseline.py                # baseline por modalidade única (F2M-14)
├── models/                        # pesos + métricas (IGNORADO pelo Git, exceto metadados)
│   ├── .gitkeep
│   ├── sinais_vitais/             # modelo.joblib + metrics.json + matriz_confusao.png
│   ├── cicatriz/                  # best.pt / best.onnx + metrics (curvas do Ultralytics)
│   └── baseline.json
└── tests/
    ├── test_schemas.py            # valores válidos/omissão de campos
    ├── test_limiares.py           # gatilhos (PA≥140/90; confiança≥0.7)
    ├── test_sinais_vitais.py      # derivação classe/PA → tipo (puro)
    ├── test_texto_nlp.py          # palavra-chave → achado/trecho
    ├── test_audio_classificacao.py# transcrição conhecida → categoria/confiança
    └── test_fisioterapia_angulos.py # keypoints sintéticos → ângulo/amplitude/execução
```

> `metrics.json`, `baseline.json` e gráficos `.png` **podem** ser versionados (pequenos, vão para o
> relatório). Pesos (`.pt`/`.onnx`/`.joblib`) **não** (tamanho + reprodutíveis pelo treino). Detalhe no
> `.gitignore` (DD4).

## 4. Componentes

### 4.1 `app/common.py` (fundação)

- `data_dir(modalidade)` / `models_dir(modalidade)` — resolvem caminhos para `data/` (insumo da Fase 1)
  e `ai-service/models/` (cria se faltar).
- `salvar_metricas(path, dict)` / `carregar_metricas(path)` — IO idempotente de `metrics.json`.
- `salvar_matriz_confusao(y_true, y_pred, labels, path)` — plota e salva o PNG (matplotlib).
- `get_logger(name, case_id=None)` — logging estruturado (JSON) com `case_id` (mesma convenção da Fase 1).

### 4.2 `app/schemas.py` (contrato de saída) — F2M-02

Construtores que **garantem valores válidos** do [contrato de API §3](../../../docs/contrato-api.md):

- `evidencia_cicatriz(evento, confianca)` — `evento ∈ {ferida_ok, sinal_infeccao, nenhum}`.
- `evidencia_fisioterapia(execucao, amplitude=None)` — `execucao ∈ {correta, incorreta, nao_avaliado}`.
- `evidencia_sinais_vitais(tipo, valor)` — `tipo ∈ {normal, risco_medio, hipertensao, pre_eclampsia}`.
- `evidencia_audio(categoria, confianca)` — `categoria ∈ {neutro, ansiedade, depressao_pos_parto, violencia, fadiga}`.
- `evidencia_texto(achado, trecho)` — `achado ∈ {complicacao, sinal_infeccao, neutro}`.

Cada construtor levanta `ValueError` para valor fora do domínio (constantes únicas reaproveitadas pelos módulos).

### 4.3 `app/limiares.py` (gatilhos clínicos) — F2M-03

Centraliza a [Tarefa 2.7](../../../docs/02-fase2-modelos.md) (e alimenta a fusão da Fase 3):

| Constante / função              | Regra                                                         |
| ------------------------------- | ------------------------------------------------------------ |
| `PA_SISTOLICA_ALERTA = 140`     | `SystolicBP ≥ 140` → hipertensão/pré-eclâmpsia               |
| `PA_DIASTOLICA_ALERTA = 90`     | `DiastolicBP ≥ 90` → hipertensão/pré-eclâmpsia               |
| `CONFIANCA_MINIMA = 0.7`        | cicatriz `ferida_alerta` e áudio de risco só contam se ≥ 0.7 |
| `pa_em_alerta(sis, dia)`        | True se PA sistólica/diastólica em faixa de alerta           |
| `risco_alto_sinais_vitais(...)` | classe `high` **ou** PA em alerta                            |

### 4.4 Sinais vitais (`sinais_vitais/`) — F2M-04..F2M-06

- `treino.py`: lê `data/sinais_vitais/maternal_clean.csv`; treina **RandomForestClassifier**
  (alvo `RiskLevel`); avalia com `train_test_split` estratificado (robusto a amostra pequena;
  `cross_val_score` quando aplicável); calcula **acurácia, F1 (macro), matriz de confusão**; salva
  `models/sinais_vitais/{modelo.joblib, metrics.json, matriz_confusao.png}`. Isolation Forest é opcional
  (anomalia não supervisionada), registrado como complemento.
- `inferencia.py`: `prever(registro) -> dict` carrega o `.joblib`, prediz a classe e **deriva o `tipo`**
  do contrato a partir da classe + limiares de PA (`derivar_tipo` é **pura/testável**):
  - PA em alerta (`limiares.pa_em_alerta`) → `hipertensao` (ou `pre_eclampsia` se houver sinal adicional na Fase 3);
  - classe `high` sem PA em alerta → `risco_medio`;
  - classe `low`/`mid` sem alerta → `normal`/`risco_medio`.
  Sem modelo treinado → erro claro / `tipo = normal` neutro documentado.
- **Funções puras testáveis:** `derivar_tipo(classe, sis, dia)` e o cálculo de métricas.

### 4.5 Cicatriz → YOLOv8 (`cicatriz/`) — F2M-07..F2M-10

- `treino.py`: `YOLO("yolov8n.pt").train(data="data/video_cicatriz/data.yaml", epochs=<poucas>, imgsz=...)`;
  o Ultralytics já gera curvas/`results.csv`; extrai **mAP@0.5, precisão, recall por classe** para
  `models/cicatriz/metrics.json` e copia `best.pt` para `models/cicatriz/`.
- `exportar.py`: `YOLO("best.pt").export(format="onnx")` → `models/cicatriz/best.onnx` (fallback `.pt`).
- `inferencia.py`: `detectar(imagem) -> dict`: roda o modelo, pega a melhor detecção, **mapeia**
  `ferida_alerta → sinal_infeccao` e `ferida_ok → ferida_ok`, aplica `limiares.CONFIANCA_MINIMA`;
  abaixo do limiar → `evento = nenhum`. O mapeamento (`mapear_evento`) é **puro/testável**.
- **Funções puras testáveis:** `mapear_evento(classe, confianca)` e a extração de métricas do `results.csv`.

> Nota de classes: a Fase 1 gera `ferida_ok`/`ferida_alerta` no `data.yaml`; o **contrato** usa
> `evento = sinal_infeccao`. O mapeamento vive em `inferencia.py` (não muda o `data.yaml`).

### 4.6 Texto/NLP (`texto/nlp.py`) — F2M-11

- `analisar(texto) -> dict`: por **palavras-chave + regras** (reaproveita os termos de risco da Fase 1:
  febre, dor na cicatriz, secreção/hiperemia → `sinal_infeccao`; proteinúria, PA alta, cefaleia,
  escotomas, depressão → `complicacao`; nada → `neutro`), devolvendo o **trecho** que disparou o achado.
- (Opcional) análise de **sentimento** via Azure Text Analytics, trocável por env var — não obrigatória.
- **Função pura testável:** `analisar(texto)` (offline, determinística).

### 4.7 Áudio (`audio/`) — F2M-12

- `transcricao.py`: reaproveita a abordagem da Fase 1 (Whisper local; `soundfile` sem ffmpeg; Azure
  trocável por `AUDIO_BACKEND`). Pode importar/reusar a lógica de `scripts/data_prep/audio_transcrever.py`.
- `classificacao.py`: `classificar(transcricao) -> dict`: palavras-chave/sentimento → `categoria` +
  `confianca`. Abaixo de `CONFIANCA_MINIMA`, a categoria de risco é contexto fraco (a fusão decide).
- **Função pura testável:** `classificar(transcricao)`.

### 4.8 Fisioterapia → pose (`fisioterapia/`) — F2M-13 (P3)

- `pose.py`: `YOLO("yolov8n-pose.pt")` extrai keypoints dos frames/sequências de `data/video_fisioterapia/`
  (ou reaproveita keypoints/esqueletos já presentes nos metadados da Fase 1).
- `angulos.py` (**puro**): `angulo(a, b, c)`, `amplitude(serie_angulos)`, `classificar_execucao(...)`
  comparando a amplitude/ângulos com faixas esperadas → `correta`/`incorreta`.
- `inferencia.py`: `avaliar(amostra) -> dict` `{execucao, amplitude}`; sem amostra → `nao_avaliado`.
- **Funções puras testáveis:** `angulo`, `amplitude`, `classificar_execucao`.

### 4.9 Baseline por modalidade única (`baseline.py`) — F2M-14

- Roda cada `inferir()` **isoladamente** sobre o mini-dataset/casos de exemplo e compara com os rótulos
  da Fase 1, calculando **precisão, recall e taxa de falsos positivos** por modalidade.
- Salva `models/baseline.json` — insumo direto da [Tarefa 3.1b](../../../docs/03-fase3-fusao-e-nuvem.md)
  (comparação fusão vs. modalidade única). Modalidade ausente → omitida.
- **Função pura testável:** a agregação de métricas (`metricas_modalidade(y_true, y_pred)`).

## 5. Decisões de design

| #   | Decisão                                                                 | Justificativa                                                                 |
| --- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| DD1 | Serviço de IA em `ai-service/app/` (pacote novo)                        | Segue `PLANO §7`/`arquitetura.md`; separa o motor de IA dos scripts de dados   |
| DD2 | **Reusar as saídas da Fase 1** em `data/` como insumo (sem re-baixar)   | Fase 1 já preparou; evita retrabalho e mantém o caminho crítico curto          |
| DD3 | Cada modalidade expõe `inferir() -> dict` do **contrato de API §3**     | A Fase 3 (fusão) consome direto, sem adaptação                                 |
| DD4 | **Pesos não versionados** (`models/` ignorado); métricas/gráficos sim   | Tamanho + reprodutibilidade; métricas pequenas vão para o relatório            |
| DD5 | Testar apenas **funções puras** (schemas, limiares, derivações, NLP)    | Treino/IO/rede são caros e não determinísticos; o valor está na lógica         |
| DD6 | Sinais vitais = **Random Forest** (principal); Isolation Forest opcional | Supervisão direta com `RiskLevel`; anomalia como complemento                   |
| DD7 | Áudio/Texto = **regras/palavras-chave** (sentimento Azure opcional)     | Determinístico, testável offline e suficiente para o desafio                   |
| DD8 | **Python 3.13** (mantém DD8 da Fase 1)                                  | `openai-whisper` ainda não suporta 3.14                                        |
| DD9 | YOLO treina como **smoke** no mini-dataset (poucas épocas)              | "Se rodar com 5, roda com 500"; escalar fica para depois do pipeline           |
| DD10| Inferência **degrada** quando faltam pesos/amostra (valor neutro)       | Mantém o pipeline da Fase 3 rodando com modalidades parciais                   |
| DD11| Integrar testes no `pyproject` da raiz (`pythonpath`+`testpaths`)       | Um único gate `ruff`+`pytest` cobre `scripts/` e `ai-service/` (ver §6)         |

## 6. Estratégia de testes (entra em cada tarefa)

Conforme `docs/qualidade-testes-ci.md` (pytest + ruff). O `pyproject.toml` da raiz passa a incluir
`ai-service` em `pythonpath` e `ai-service/tests` em `testpaths` (DD11).

| Camada                                  | Tipo  | O que cobre                                              |
| --------------------------------------- | ----- | ------------------------------------------------------- |
| `schemas` (construtores de evidência)   | unit  | valores válidos aceitos; inválidos → `ValueError`       |
| `limiares` (gatilhos)                   | unit  | PA ≥ 140/90 → alerta; confiança < 0.7 não conta          |
| `sinais_vitais.derivar_tipo`            | unit  | classe/PA conhecidas → `tipo` esperado                  |
| `cicatriz.mapear_evento`                | unit  | `ferida_alerta`+conf≥0.7 → `sinal_infeccao`; baixo → `nenhum` |
| `texto.analisar`                        | unit  | termo de risco → achado/trecho corretos                 |
| `audio.classificar`                     | unit  | transcrição conhecida → categoria/confiança             |
| `fisioterapia.angulos`                  | unit  | keypoints sintéticos → ângulo/amplitude/execução        |
| `baseline.metricas_modalidade`          | unit  | y_true/y_pred → precisão/recall/FP esperados            |
| treino YOLO/RF, export ONNX, transcrição | none  | IO/rede/treino — validados pelo "Independent Test"/smoke |

- **Gate quick:** `ruff check scripts ai-service && pytest -q`.
- Funções de treino/IO/rede não recebem teste unitário (DD5); são validadas por execução manual (smoke).

## 7. Riscos (herdados do escopo) e mitigação local

| Risco                                            | Mitigação na Fase 2                                                       |
| ------------------------------------------------ | ------------------------------------------------------------------------ |
| Treino do YOLO é o item mais demorado            | YOLOv8n + mini-dataset + poucas épocas (smoke); escalar depois (DD9)      |
| Mini-dataset pequeno → métricas instáveis        | Documentar que as métricas são ilustrativas; split robusto a poucos dados |
| AZH Wound não é de cesárea / classe alerta proxy | Mapeamento `ferida_alerta → sinal_infeccao`; limitação no relatório       |
| Áudio/fisioterapia exigem obtenção manual        | Módulos degradam (modalidade ausente) sem quebrar o baseline/pipeline     |
| Export ONNX depende de ambiente                  | Fallback para `.pt`; erro claro com instrução                             |
| Divergência da saída vs. contrato                | `schemas.py` valida o domínio; testado em unidade (F2M-02)               |
| Versionar pesos sensíveis/grandes                | `models/` no `.gitignore` (só métricas/gráficos versionados) (DD4)        |
