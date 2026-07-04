# ai-service — Motor de IA (Fases 2 e 3)

Serviço de IA com **um módulo por modalidade** (Fase 2) + **motor de fusão, pipeline, API FastAPI,
relatório automático e métrica do ganho da fusão** (Fase 3). Cada modalidade expõe uma inferência que
devolve o **dicionário de evidência padronizado** do [contrato de API §3](../docs/contrato-api.md); a
fusão cruza essas evidências e produz o **JSON de risco** do [contrato §2](../docs/contrato-api.md).

> Planejamento: [`.specs/features/fase2-modelos/`](../.specs/features/fase2-modelos/) e
> [`.specs/features/fase3-fusao-e-nuvem/`](../.specs/features/fase3-fusao-e-nuvem/) (spec → design →
> tasks). O backend orquestrador (Node) fica em [`../backend`](../backend); o deploy na Azure em
> [`../docs/deploy-azure.md`](../docs/deploy-azure.md).

## Instalação

```bash
python -m venv .venv && source .venv/bin/activate   # Python 3.12+
pip install -r ai-service/requirements.txt
```

Os modelos consomem o **mini-dataset da Fase 1** (em `data/`). Gere-o antes, se necessário:

```bash
python -m scripts.data_prep              # orquestrador (ou módulos individuais)
```

## Estrutura

```
ai-service/
├── app/
│   ├── common.py          # caminhos (data/, models/), logging, IO de métricas
│   ├── schemas.py         # construtores de evidência (valores do contrato §3)
│   ├── limiares.py        # gatilhos clínicos (Tarefa 2.7)
│   ├── sinais_vitais/     # Random Forest (treino + inferência)
│   ├── cicatriz/          # YOLOv8 (treino + export ONNX + inferência)
│   ├── audio/             # transcrição (Whisper) + classificação
│   ├── texto/             # NLP por regras/palavras-chave
│   ├── baseline.py        # baseline por modalidade única (Tarefa 2.6)
│   ├── fusao.py           # motor de fusão (regras explícitas — Fase 3, Tarefa 3.1)
│   ├── pipeline.py        # contrato §1 → inferências → fusão → §2 (Fase 3)
│   ├── relatorio.py       # relatório clínico automático Markdown→HTML/PDF (Fase 3)
│   ├── metricas_fusao.py  # ganho da fusão vs modalidade única (Fase 3, Tarefa 3.1b)
│   ├── storage.py         # adaptador de storage local (fallback)
│   ├── storage_azure.py   # adaptador Azure Blob (modo nuvem, SAS)
│   └── api/               # FastAPI: POST /inferencia + GET /health (Fase 3, Tarefa 3.2)
├── models/                # pesos (ignorados) + métricas/baseline/fusão (versionados)
└── tests/                 # pytest (funções puras + API via TestClient)
```

## Como treinar / inferir (rodar a partir de `ai-service/`)

| Modalidade    | Treino                                   | Inferência (saída padronizada)                        |
| ------------- | ---------------------------------------- | ----------------------------------------------------- |
| Sinais vitais | `python -m app.sinais_vitais.treino`     | `app.sinais_vitais.inferencia.prever(registro)`       |
| Cicatriz      | `python -m app.cicatriz.treino`          | `app.cicatriz.inferencia.detectar(imagem)`            |
| Cicatriz (export) | `python -m app.cicatriz.exportar`    | gera `models/cicatriz/best.onnx`                      |
| Texto/NLP     | `python -m app.texto.treino` (Fase 8)    | `app.texto.nlp.analisar(texto)`                       |
| Áudio         | `python -m app.audio.treino` (Fase 8)    | `app.audio.classificacao.inferir(caminho)`            |
| Baseline      | `python -m app.baseline`                 | gera `models/baseline.json`                           |

> **Fase 8 (áudio/texto unificado):** o texto usa classificadores **ML** de depressão/violência
> (PT-BR) + keywords; o áudio tem **análise dupla** (acústico + transcrição→texto). Prepare os dados
> com `python -m scripts.data_prep.fase8_datasets` (na raiz). Sem os pesos, tudo degrada por
> keywords (DD10). Ver [`docs/11-fase8-audio-texto-unificado.md`](../docs/11-fase8-audio-texto-unificado.md).

## Saída padronizada por modalidade (contrato §3)

| Modalidade    | Dicionário de evidência                                                        |
| ------------- | ------------------------------------------------------------------------------ |
| Cicatriz      | `{"evento": ferida_ok\|sinal_infeccao\|nenhum, "confianca": 0..1}`            |
| Fisioterapia  | `{"execucao": correta\|incorreta\|nao_avaliado, "amplitude": ...}`            |
| Sinais vitais | `{"tipo": normal\|risco_medio\|hipertensao\|pre_eclampsia, "valor": "150/95"}`|
| Áudio         | `{"acustico": {rotulo, confianca}, "transcricao", "texto": {…}, "categoria"(legado), "confianca"(legado)}` |
| Texto         | `{"achado": complicacao\|sinal_infeccao\|neutro, "trecho", "depressao": {rotulo, confianca}, "violencia": {rotulo, confianca}}` |

## Limiares clínicos (Tarefa 2.7 — `app/limiares.py`)

| Sinal                       | Condição de alerta                       |
| --------------------------- | ---------------------------------------- |
| PA sistólica / diastólica   | `>= 140/90 mmHg`                         |
| Modelo de sinais vitais     | classe `high`                            |
| Cicatriz (`ferida_alerta`)  | confiança `>= 0.7`                       |
| Áudio (violência acústica)  | confiança `>= 0.7` (`CONFIANCA_MINIMA`)  |
| Texto (depressão/violência ML) | confiança `>= 0.6` (`CONFIANCA_TEXTO`) |
| Texto clínico (keywords)    | termo/categoria de risco identificado    |

## Métricas

- Por modalidade: `models/<modalidade>/metrics.json` (+ `matriz_confusao.png` nos sinais vitais).
- Cicatriz: `mAP@0.5`, precisão, recall e `mAP_por_classe`.
- Baseline por modalidade única: `models/baseline.json` (precisão, recall, taxa de falsos positivos)
  — base de comparação para o ganho da fusão na Fase 3 (Tarefa 3.1b).

## Fase 3 — fusão, API, relatório e métricas (rodar a partir de `ai-service/`)

| Capacidade | Como rodar | Saída |
| ---------- | ---------- | ----- |
| Motor de fusão | `app.fusao.avaliar_fusao(evidencias)` | `{risco_detectado, mensagem_alerta, gatilhos}` |
| Pipeline | `app.pipeline.processar(requisicao)` | JSON de risco (contrato §2) |
| API FastAPI | `uvicorn app.api.main:app --port 8000` | `POST /inferencia`, `GET /health` |
| Relatório | `app.relatorio.gerar_e_salvar(...)` | Markdown→HTML/PDF salvo no storage |
| Métrica da fusão | `python -m app.metricas_fusao` | `models/metricas_fusao.json` |

**Regras do motor de fusão** (contrato §4 + [docs/03](../docs/03-fase3-fusao-e-nuvem.md)): a matriz base
cruza cicatriz × sinais vitais; texto/áudio entram como **contexto** que pode elevar a prioridade
(infecção puerperal, pré-eclâmpsia, violência → `ALTO`; depressão/ansiedade → ≥ `MEDIO`). Contexto
isolado (texto/áudio fraco) tem **teto `MEDIO`**. A saída lista os **gatilhos** acionados
(rastreabilidade do relatório).

**Ganho da fusão** (`models/metricas_fusao.json`): compara `só-vídeo`, `só-vitais`, `só-áudio/texto` e
`fusão` — a fusão **reduz falsos positivos** e **aumenta o recall** dos casos críticos (Tarefa 3.1b).

**Demo ponta-a-ponta:** `python -m scripts.e2e_demo` (upload local → inferência → JSON → alerta).

## Testes e lint (gate)

```bash
ruff check scripts ai-service
pytest -q
```

Os testes cobrem as **funções puras** (schemas, limiares, derivações, NLP, classificação de áudio,
geometria de pose, métricas do baseline). Treino/IO/ASR/export são validados por execução (smoke).

## Limitações (registrar no relatório técnico)

- **Mini-dataset / smoke:** os modelos são treinados com poucas amostras (princípio "se rodar com 5,
  roda com 500"). As métricas são **ilustrativas**; o detector de cicatriz precisa ser **escalado**
  (mais dados/épocas em GPU/Colab) para gerar detecções confiáveis acima do limiar.
- **Domínio da cicatriz:** AZH Wound (feridas cirúrgicas) como proxy de cesárea; classe
  `ferida_alerta` mapeada para `sinal_infeccao`.
- **Áudio:** depende de amostras de obtenção manual (Fase 1); os módulos degradam para
  `neutro`/`nao_avaliado` quando faltam dados/pesos, sem quebrar o pipeline.
