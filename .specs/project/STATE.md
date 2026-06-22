# STATE — Memória do Projeto

> Memória persistente entre sessões (decisões, blockers, lições, todos, ideias adiadas).
> Visão e roadmap completos vivem em [`PLANO_DE_DESENVOLVIMENTO.md`](../../PLANO_DE_DESENVOLVIMENTO.md)
> e em [`docs/`](../../docs).

## Fase atual

**Fase 4 — Empacotamento e Entregáveis** — **planejada** (spec → design → tasks).
Plano em [`.specs/features/fase4-entregaveis/`](../features/fase4-entregaveis/): 14 requisitos
(F4E-01..F4E-14) e 9 tarefas (T1–T9). Fase de **documentação/empacotamento** (não cria código de produto):
audita o **repositório** (4.1), consolida **evidências reais** (métricas da Fase 2,
`models/metricas_fusao.json`, exemplo de relatório automático via `app/relatorio.py`, log do
`scripts/e2e_demo.py`), escreve o **relatório técnico** (`docs/relatorio-tecnico.md`, 6 seções do PDF) com
exportação para PDF (fallback HTML/Markdown), e o **roteiro do vídeo** (`docs/roteiro-video.md`, 8 pontos,
≤15 min). Decisões DD-F4-1..DD-F4-8 (relatório em Markdown+PDF fallback; diagramas Mermaid inline;
**reusar artefatos reais, nunca inventar**; **vídeo = roteiro + placeholder de link**, pois gravação/
publicação é **ação humana**; limitações documentadas honestamente; gate verde como critério de
fechamento). **A implementar** (a partir de `tasks.md`).

**Fase 3 — Fusão Multimodal e Integração em Nuvem** — **implementada** (T1–T18).
Plano em [`.specs/features/fase3-fusao-e-nuvem/`](../features/fase3-fusao-e-nuvem/) (spec → design → tasks):
17 requisitos (F3F-01..F3F-17) e 18 tarefas (T1–T18). Núcleo de valor = **motor de fusão**
(`ai-service/app/fusao.py`, regras explícitas do contrato §4 + Tarefa 3.1) + **pipeline**
(`app/pipeline.py`, contrato §1→§2), exposto por **FastAPI** (`app/api/main.py`: `POST /inferencia` +
`/health`); **backend Node/Express** (`backend/`) orquestra upload→storage→IA→banco→**alerta em tempo
real** (socket.io) e gere pacientes (CRUD); **relatório automático** (`app/relatorio.py`,
Markdown→HTML/PDF com fallback) e **métrica do ganho da fusão** (`app/metricas_fusao.py` →
`models/metricas_fusao.json`: fusão recall 1.0 / FP 0.0 vs. modalidades isoladas). Storage com adaptador
**Azure Blob | local** (`app/storage*.py`, `backend/src/storage/`; fallback p/ a demo). Cliente mínimo
em `backend/public/index.html`. Reproduz com `docker compose up`; **CI** em `.github/workflows/ci.yml`
(ruff+pytest / eslint+jest); E2E em `scripts/e2e_demo.py`. Gate verde:
`ruff check scripts ai-service` + `pytest -q` (**96 testes** Python) e `npm run lint`/`npm test`
(**11 testes** Node). Reaproveita as inferências da Fase 2 (`detectar/avaliar/prever/inferir/analisar`),
`schemas.py`, `limiares.py`, `baseline.metricas_modalidade`. Deploy real na Azure documentado em
`docs/deploy-azure.md` (pode usar fallback local — não bloqueia o gate). Dashboard React completo
permanece **fora de escopo** (cliente mínimo demonstra o alerta).
Observações do ambiente: sem pesos do YOLO (cicatriz/fisioterapia) e sem ASR de áudio, essas
modalidades **degradam** (evidência omitida/`nenhum`, DD10); a fusão ainda decide com vitais+texto. Com
os pesos treinados, o `caso_alto` escala para `ALTO` (infecção puerperal) — ver `scripts/e2e_demo.py`.

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

> Origem: links para o documento de design da fase correspondente (F1 = Fase 1, F2 = Fase 2).

| #   | Decisão                                                              | Origem                                                          |
| --- | -------------------------------------------------------------------- | -------------------------------------------------------------- |
| S1  | Scripts de dados em `scripts/data_prep/` (não em `ai-service/`)      | [F1 design DD1](../features/fase1-dados/design.md)             |
| S2  | `requirements-data.txt` separado das deps do serviço de IA          | [F1 design DD2](../features/fase1-dados/design.md)             |
| S3  | Caso sintético segue o objeto de requisição do contrato de API      | [F1 design DD4](../features/fase1-dados/design.md)             |
| S4  | Testes unitários só em funções puras (limpeza/conversão/builder)    | [F1 design DD5](../features/fase1-dados/design.md)             |
| S5  | `data/` ignorado pelo Git; só `data/README.md` versionado           | [F1 design DD7](../features/fase1-dados/design.md)             |
| S6  | **Python 3.13/3.12** (não 3.14): whisper não suporta 3.14 ainda     | [F1 design DD8](../features/fase1-dados/design.md)             |
| S7  | Serviço de IA em `ai-service/app/`; pesos não versionados           | [F2 design DD1/DD4](../features/fase2-modelos/design.md)       |
| S8  | Cada modalidade expõe `inferir() -> dict` do contrato de API §3     | [F2 design DD3](../features/fase2-modelos/design.md)           |
| S9  | Sinais vitais = Random Forest (principal); Isolation Forest opcional | [F2 design DD6](../features/fase2-modelos/design.md)           |
| S10 | Áudio/Texto = regras/palavras-chave (sentimento Azure opcional)     | [F2 design DD7](../features/fase2-modelos/design.md)           |
| S11 | Testes do `ai-service/` integrados ao `pyproject` da raiz           | [F2 design DD11](../features/fase2-modelos/design.md)          |
| S12 | Fusão = **motor de regras puro** (`app/fusao.py`), não end-to-end   | [F3 design DD1](../features/fase3-fusao-e-nuvem/design.md)     |
| S13 | **Pipeline único** (contrato §1→§2) consumido por FastAPI + testes  | [F3 design DD3](../features/fase3-fusao-e-nuvem/design.md)     |
| S14 | Backend **Node** orquestra; Python só IA (FastAPI)                  | [F3 design DD5](../features/fase3-fusao-e-nuvem/design.md)     |
| S15 | Tempo real via **socket.io** (WebSocket); SSE como alternativa      | [F3 design DD6](../features/fase3-fusao-e-nuvem/design.md)     |
| S16 | Relatório sempre **Markdown/HTML**; PDF opcional (weasyprint)       | [F3 design DD7](../features/fase3-fusao-e-nuvem/design.md)     |
| S17 | Storage com adaptador **Azure Blob \| local** (env); fallback p/ demo | [F3 design DD8](../features/fase3-fusao-e-nuvem/design.md)   |
| S18 | Persistência **SQLite** (`better-sqlite3`); Postgres/Cosmos opcional | [F3 design DD9](../features/fase3-fusao-e-nuvem/design.md)    |
| S19 | **Cliente mínimo** (HTML+socket.io); dashboard React = feature à parte | [F3 design DD10](../features/fase3-fusao-e-nuvem/design.md) |

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
- [x] Planejar a Fase 3 (spec → design → tasks em `.specs/features/fase3-fusao-e-nuvem/`).
- [x] Implementar a Fase 3 seguindo `tasks.md` (T1–T18): fusão, pipeline, FastAPI, relatório, métricas,
      backend Node (CRUD + `/analisar` + alerta socket.io), storage Azure/local, Docker/compose, CI e E2E.
      Gate verde (ruff + 96 testes Python; eslint + 11 testes Node).
- [ ] Decisão pendente do grupo: **deploy real na Azure** vs. fallback local para a gravação da demo (T17).
- [x] Runtime/versões fixadas no `backend/package.json` (Node 22 LTS, última estável das libs) e nas
      deps Python adicionadas em `ai-service/requirements.txt`.
- [ ] **Escalar o detector de cicatriz** (GPU/Colab) para o `caso_alto` fechar `ALTO` ponta-a-ponta sem
      mock (hoje degrada e a fusão decide com vitais+texto).
- [x] Planejar a Fase 4 (spec → design → tasks em `.specs/features/fase4-entregaveis/`): repositório,
      relatório técnico e vídeo (14 requisitos F4E-01..F4E-14, 9 tarefas T1–T9).
- [ ] Implementar a Fase 4 seguindo `tasks.md` (T1–T9): auditoria do repo, evidências, relatório técnico
      (+PDF), roteiro do vídeo, README (créditos/link), checklist + gate, STATE/docs/04.
- [ ] **Ação humana (grupo):** gravar e publicar o **vídeo** (≤15 min, "Não listado") e colar o link no
      README — o agente entrega o roteiro (`docs/roteiro-video.md`) e o placeholder.

## Ideias adiadas

- Escalar mini-dataset (de 5 para mais amostras) só após o pipeline rodar ponta-a-ponta (Fase 3).
- Datasets sintéticos extras de pré-eclâmpsia (HF) para reforçar a modalidade de sinais vitais.

## Lições

- (a preencher durante a execução)
