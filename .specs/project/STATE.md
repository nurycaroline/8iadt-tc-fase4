# STATE — Memória do Projeto

> Memória persistente entre sessões (decisões, blockers, lições, todos, ideias adiadas).
> Visão e roadmap completos vivem em [`PLANO_DE_DESENVOLVIMENTO.md`](../../PLANO_DE_DESENVOLVIMENTO.md)
> e em [`docs/`](../../docs).

## Fase atual

**Fase 2 — Desenvolvimento dos Modelos Individuais** — **implementada** (T1–T14).
Plano em [`.specs/features/fase2-modelos/`](../features/fase2-modelos/) (spec → design → tasks).
Código em `ai-service/app/` (um módulo por modalidade) + testes em `ai-service/tests/`. Cada
modalidade expõe inferência com **saída padronizada** (dict do contrato §3); limiares em
`app/limiares.py`; baseline em `ai-service/models/baseline.json`. Gate verde:
`ruff check scripts ai-service` + `pytest -q` (63 testes).
Treinos reais executados neste ambiente: **sinais vitais** (Random Forest, 451 amostras,
acurácia≈0.65/F1≈0.62) e **cicatriz** (YOLOv8n smoke, 6 imagens AZH, mAP50≈0.93, export ONNX ok).
**Texto/NLP** 5/5 vs. rótulos. **Áudio/fisioterapia**: classificadores/geometria testados; treino/
inferência completa exige dados de obtenção manual (degradam sem quebrar — DD10).
Observações do ambiente: Python **3.12** (não 3.13; dentro da faixa suportada); o detector de
cicatriz é **smoke** e precisa escalar (GPU/Colab) para detecções confiáveis acima do limiar.

**Fase 1 — Aquisição e Preparação de Dados** — **implementada**.
Plano em [`.specs/features/fase1-dados/`](../features/fase1-dados/) (spec → design → tasks).
Código em `scripts/data_prep/` (+ testes em `scripts/tests/`); estrutura em `data/`.
Gate verde: `ruff check scripts` + `pytest` (12 testes). Orquestrador `python -m scripts.data_prep`
validado: sinais vitais (UCI) e cicatriz (AZH Wound, download+conversão+preview) baixam de verdade;
texto/caso sintético gerados offline. Áudio e fisioterapia exigem obtenção manual (sem download
público simples) e aparecem como passos opcionais.

## Decisões registradas

| #   | Decisão                                                            | Origem                |
| --- | ----------------------------------------------------------------- | --------------------- |
| S1  | Scripts de dados em `scripts/data_prep/` (não em `ai-service/`)    | design.md DD1         |
| S2  | `requirements-data.txt` separado das deps do serviço de IA        | design.md DD2         |
| S3  | Caso sintético segue o objeto de requisição do contrato de API    | design.md DD4         |
| S4  | Testes unitários só em funções puras (limpeza/conversão/builder)  | design.md DD5         |
| S5  | `data/` ignorado pelo Git; só `data/README.md` versionado         | design.md DD7         |
| S6  | **Python 3.13** (não 3.14): whisper não suporta 3.14 ainda        | design.md DD8 (F1/F2) |
| S7  | Serviço de IA em `ai-service/app/`; pesos não versionados          | fase2 design.md DD1/DD4 |
| S8  | Cada modalidade expõe `inferir() -> dict` do contrato de API §3    | fase2 design.md DD3   |
| S9  | Sinais vitais = Random Forest (principal); Isolation Forest opcional | fase2 design.md DD6 |
| S10 | Áudio/Texto = regras/palavras-chave (sentimento Azure opcional)   | fase2 design.md DD7   |
| S11 | Testes do `ai-service/` integrados ao `pyproject` da raiz          | fase2 design.md DD11  |

## Blockers / dependências externas

- Acesso/licença dos datasets pode exigir login (IntelliRehabDS, Androids). Fallback: obtenção manual
  documentada em `data/README.md` (T2 da Fase 1).
- Decisão pendente do grupo: usar **Whisper local** ou **Azure Speech-to-Text** para transcrição
  (áudio) — design deixa o backend trocável por env var.
- Fase 2 depende de amostras de **áudio** e **fisioterapia** (obtenção manual na Fase 1). Os módulos
  degradam (modalidade ausente) sem quebrar o baseline/pipeline (DD10).
- **Treino do YOLO** (cicatriz/pose) é o item mais demorado — começar cedo; smoke no mini-dataset,
  escalar (Colab/GPU) só após o pipeline rodar ponta-a-ponta (DD9).
- Decisão pendente do grupo: versionar pesos via **Git LFS** vs. apenas métricas (atual: só métricas).

## Todos / próximos passos

- [x] Planejar a Fase 2 (spec → design → tasks em `.specs/features/fase2-modelos/`).
- [x] Implementar a Fase 2 seguindo `tasks.md` (T1–T14). Gate verde (ruff + 63 testes).
- [ ] **Escalar o detector de cicatriz** (mais dados/épocas em GPU/Colab) — smoke atual não detecta
      acima do limiar de confiança.
- [ ] Obter amostras de **áudio** e **fisioterapia** (manual) e rodar o baseline completo dessas modalidades.
- [ ] Iniciar o planejamento da Fase 3 (motor de fusão + API FastAPI/Node + nuvem Azure).

## Ideias adiadas

- Escalar mini-dataset (de 5 para mais amostras) só após o pipeline rodar ponta-a-ponta (Fase 3).
- Datasets sintéticos extras de pré-eclâmpsia (HF) para reforçar a modalidade de sinais vitais.

## Lições

- (a preencher durante a execução)
