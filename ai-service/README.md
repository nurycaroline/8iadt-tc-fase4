# ai-service — Motor de IA (Fase 2)

Serviço de IA com **um módulo por modalidade**. Cada módulo treina/avalia o modelo isoladamente e
expõe uma função de inferência que devolve o **dicionário de evidência padronizado** do
[contrato de API §3](../docs/contrato-api.md), pronto para o **motor de fusão da Fase 3**.

> Planejamento: [`.specs/features/fase2-modelos/`](../.specs/features/fase2-modelos/)
> (spec → design → tasks). A API FastAPI, a fusão e o deploy na Azure são da **Fase 3**.

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
│   ├── fisioterapia/      # YOLOv8-pose + ângulos/amplitude
│   ├── audio/             # transcrição (Whisper) + classificação
│   ├── texto/             # NLP por regras/palavras-chave
│   └── baseline.py        # baseline por modalidade única (Tarefa 2.6)
├── models/                # pesos (ignorados) + métricas/baseline (versionados)
└── tests/                 # pytest (funções puras)
```

## Como treinar / inferir (rodar a partir de `ai-service/`)

| Modalidade    | Treino                                   | Inferência (saída padronizada)                        |
| ------------- | ---------------------------------------- | ----------------------------------------------------- |
| Sinais vitais | `python -m app.sinais_vitais.treino`     | `app.sinais_vitais.inferencia.prever(registro)`       |
| Cicatriz      | `python -m app.cicatriz.treino`          | `app.cicatriz.inferencia.detectar(imagem)`            |
| Cicatriz (export) | `python -m app.cicatriz.exportar`    | gera `models/cicatriz/best.onnx`                      |
| Texto/NLP     | — (regras)                               | `app.texto.nlp.analisar(texto)`                       |
| Áudio         | — (regras + ASR)                         | `app.audio.classificacao.inferir(caminho)`            |
| Fisioterapia  | — (pose)                                 | `app.fisioterapia.inferencia.avaliar(fonte)`          |
| Baseline      | `python -m app.baseline`                 | gera `models/baseline.json`                           |

## Saída padronizada por modalidade (contrato §3)

| Modalidade    | Dicionário de evidência                                                        |
| ------------- | ------------------------------------------------------------------------------ |
| Cicatriz      | `{"evento": ferida_ok\|sinal_infeccao\|nenhum, "confianca": 0..1}`            |
| Fisioterapia  | `{"execucao": correta\|incorreta\|nao_avaliado, "amplitude": ...}`            |
| Sinais vitais | `{"tipo": normal\|risco_medio\|hipertensao\|pre_eclampsia, "valor": "150/95"}`|
| Áudio         | `{"categoria": neutro\|ansiedade\|depressao_pos_parto\|violencia\|fadiga, "confianca": 0..1}` |
| Texto         | `{"achado": complicacao\|sinal_infeccao\|neutro, "trecho": "..."}`            |

## Limiares clínicos (Tarefa 2.7 — `app/limiares.py`)

| Sinal                       | Condição de alerta                       |
| --------------------------- | ---------------------------------------- |
| PA sistólica / diastólica   | `>= 140/90 mmHg`                         |
| Modelo de sinais vitais     | classe `high`                            |
| Cicatriz (`ferida_alerta`)  | confiança `>= 0.7`                       |
| Áudio (categoria de risco)  | confiança `>= 0.7`                       |
| Texto clínico               | termo/categoria de risco identificado    |

## Métricas

- Por modalidade: `models/<modalidade>/metrics.json` (+ `matriz_confusao.png` nos sinais vitais).
- Cicatriz: `mAP@0.5`, precisão, recall e `mAP_por_classe`.
- Baseline por modalidade única: `models/baseline.json` (precisão, recall, taxa de falsos positivos)
  — base de comparação para o ganho da fusão na Fase 3 (Tarefa 3.1b).

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
- **Áudio/fisioterapia:** dependem de amostras de obtenção manual (Fase 1); os módulos degradam para
  `neutro`/`nao_avaliado` quando faltam dados/pesos, sem quebrar o pipeline.
