# STATE — Memória do Projeto

> Memória persistente entre sessões (decisões, blockers, lições, todos, ideias adiadas).
> Visão e roadmap completos vivem em [`PLANO_DE_DESENVOLVIMENTO.md`](../../PLANO_DE_DESENVOLVIMENTO.md)
> e em [`docs/`](../../docs).

## Fase atual

**Fase 8 — Áudio/Texto Unificado (depressão e violência)** — **implementada + modelos treinados**.
Spec em [`.specs/features/fase8-audio-texto-unificado/spec.md`](../features/fase8-audio-texto-unificado/spec.md)
e doc [`docs/11-fase8-audio-texto-unificado.md`](../../docs/11-fase8-audio-texto-unificado.md). Troca a
abordagem por **palavras-chave** de áudio/texto por **classificadores ML locais** em PT-BR e adiciona uma
trilha **acústica** de violência. **Tudo local/offline (sem Azure).** Entregue (F8-01..F8-10): (F8-01)
deps locais — `librosa`/`faster-whisper`/`sentence-transformers`/`argostranslate` em
`ai-service/requirements.txt`, `datasets`/`huggingface-hub` em `scripts/requirements-data.txt`; (F8-02)
pipeline de dados `scripts/data_prep/fase8_datasets.py` (download dos 3 datasets HF + tradução EN→PT
offline via `scripts/data_prep/traducao.py`, Argos padrão / X-ALMA opcional por env + geração de
**negativos** de violência), idempotente e tolerante a falha de rede; (F8-03) schema em `app/schemas.py`
(`evidencia_texto` +`depressao`/`violencia`; `evidencia_audio_unificada` com `acustico`/`transcricao`/
`texto` + **categoria legada derivada**; domínios `ROTULOS_DEPRESSAO`/`ROTULOS_VIOLENCIA`); (F8-04) treino
de texto `app/texto/treino.py` (TF-IDF+LogReg → `models/texto/<nome>.joblib` + `metrics.json`); (F8-05)
treino acústico `app/audio/treino.py` + `app/audio/features.py` (MFCC via librosa + LogReg →
`models/audio/violencia_acustico.joblib`); (F8-06) `app/audio/classificacao.py` reescrito (análise dupla
acústico + transcrição→texto unificado; fallback gracioso DD10; `classificar()` legado preservado p/
baseline); (F8-07) `app/texto/nlp.py` reescrito (depressão ML + violência ML + keywords de infecção/
complicação preservadas; depressão **saiu** de `TERMOS_COMPLICACAO`); (F8-08) fusão `app/fusao.py` +
`app/limiares.py` com novos gatilhos (violência acústica `≥0.7`, violência/depressão no texto `≥0.6`),
sem regressão; (F8-09) testes (+17 → **129** Python) — schema, classificadores (mocks/fixtures pequenas),
áudio dupla e fusão; (F8-10) docs/contrato/datasets/02-fase2/PLANO/STATE. **Carregamento de modelo
tolerante** (`app/ml_utils.py`): sem pesos, tudo degrada por keywords (gate roda sem download/treino).
**Gate verde:** `ruff` + `pytest` (**129 testes** Python). **Treino real concluído (ambiente do grupo,
2026-06-27):** depressão (texto) F1 macro **0,93**; violência (texto) F1 **1,0** (⚠️ teto de **dados** —
positivos `Spiderman01` e negativos `ShreyaR` são fontes distintas → separabilidade trivial; não generaliza,
ver docs/11 §Resultados); violência **acústica** F1 macro **0,94** — pesos `models/texto/*.joblib` e
`models/audio/violencia_acustico.joblib` **agora versionados**. **Decisão registrada:** datasets adotados +
descarte do `singhsandk/domestic-violence-dataset-prep` (14 linhas, Q&A). **Atenção:** rodar com Python
**≥3.12** — o `app.baseline`/`app.metricas_fusao` usam `zip(strict=True)` (quebra no pyenv 3.9 global).

**Fase 7 — Privacidade e Segurança (LGPD)** — **implementada** (F7-01..F7-08).
Spec em [`.specs/features/fase7-privacidade-e-seguranca/`](../features/fase7-privacidade-e-seguranca/spec.md)
e doc [`docs/10-fase7-privacidade-e-seguranca.md`](../../docs/10-fase7-privacidade-e-seguranca.md). A
**documentação de LGPD já existia** (disclaimer + §5 do relatório); a Fase 7 fechou a lacuna entre os
**controles técnicos** do componente [`docs/07`](../../docs/07-privacidade-e-seguranca.md) e o **código**:
(F7-01) **auth de serviço** — `x-api-key` no backend (`backend/src/middleware/auth.js`) e no `ai-service`
(`ai-service/app/api/seguranca.py`); opt-in (vazio = demo aberta; `AUTH_REQUIRED=true` força negar — preserva
DD10); `/health`/`/ready` públicos; (F7-02) **TLS opt-in** na borda (`frontend/nginx.tls.conf` +
`docker-compose.tls.yml` + `scripts/gerar-cert-dev.sh`, HSTS) + Node↔Python aceita `https://`, fallback HTTP;
(F7-03) **auditoria de acesso** — tabela `auditoria` (`db/index.js`/`repositorios.js`) registrada em
`rotas/casos.js` e `rotas/analisar.js` (usuário via `x-user-id`, sem conteúdo clínico); (F7-04) **retenção** —
`backend/src/servicos/retencao.js` + `scripts/retencao.js` (`npm run retencao`), TTL `RETENTION_DAYS`; (F7-05)
**pseudonimização** — `backend/src/seguranca/pseudonimizacao.js` (`case_id` UUID validado + `pacienteMinimo`
remove `primeiro_nome` do payload à IA); (F7-06) **hardening** — `helmet` + `backend/src/middleware/cors.js`
(allowlist; socket.io idem) + security headers no `nginx` + `fileFilter` de MIME no upload; (F7-07) **Key
Vault opcional** — `backend/src/seguranca/segredos.js` + `bootstrap.js` (fallback `.env`); (F7-08)
**conformidade no CI** — `scripts/check_conformidade.py` + job `conformidade`; checklist `docs/07 §6` e §5 do
relatório atualizados; disclaimer realçado no README. **Defaults da spec aplicados** (escopo confirmado pelo
pedido "implemente a fase 7"). **Gate verde:** `ruff`+`pytest` (**111 testes** Python; +4), `eslint`+`jest`
(**32 testes** Node; +14) e `eslint`+`vitest`+`build` do frontend (**7 testes**). **Já satisfeito (não
recriado):** SAS com expiração, `.env`/`data/` no `.gitignore`, dados sintéticos. **Fora de escopo:**
RBAC/Private Endpoint reais na Azure (ação humana/infra, ligado ao F5-03) e gravar o vídeo (DD-F4-5).

**Fase 6 — Relatórios Automáticos Especializados** — **implementada** (F6-01..F6-05).
Spec em [`.specs/features/fase6-relatorios-automaticos/`](../features/fase6-relatorios-automaticos/spec.md) e
doc [`docs/09-fase6-relatorios-automaticos.md`](../../docs/09-fase6-relatorios-automaticos.md). O **relatório
automático já existia** (Fase 3 — `ai-service/app/relatorio.py`; download no dashboard na Fase 5); a Fase 6
fechou a lacuna entre o requisito [`docs/06`](../../docs/06-relatorios-automaticos.md) e o código: (F6-01)
**encaminhamento especializado por gatilho** (`ENCAMINHAMENTO_GATILHO` + `_secao_recomendacao`, reusando
`app/fusao.gatilhos`) com fallback por nível; (F6-02) **anexos com links reais** dos artefatos
(`_secao_anexos`/`_artefatos_da_requisicao` — link http(s) ou identificador local; omite ausentes — DD10);
(F6-03) **PDF garantido** habilitando `weasyprint` em `requirements.txt` + libs Pango/cairo no
`ai-service/Dockerfile` (**PDF validado neste ambiente**; fallback HTML preservado — S16/DD7); (F6-04)
**pré-visualização** no dashboard (`frontend/src/components/RelatorioModal.tsx` — modal acessível com iframe +
download + "abrir em nova aba"); (F6-05) **testes** novos em `tests/test_relatorio.py` e **exemplo regerado**
por `scripts/gerar_evidencias.py` (S23). Decisões resolvidas com os defaults propostos (escopo confirmado pelo
pedido "implemente a fase 6"). **Gate verde:** `ruff`+`pytest` (**107 testes** Python; +5) e
`eslint`+`vitest`+`build` do frontend (**7 testes**). **Fora de escopo:** gerar o **frame de alerta real** da
cicatriz (depende do detector escalado — F5-01, bloqueado por ambiente; os anexos referenciam o vídeo/imagem de
origem) e gravar o **vídeo**.

**Fase 5 — Produção, Escala e Robustez** — **parcialmente implementada**.
Spec/tasks em [`.specs/features/fase5-producao-e-escala/`](../features/fase5-producao-e-escala/spec.md) e
doc [`docs/08-fase5-producao-e-escala.md`](../../docs/08-fase5-producao-e-escala.md). As Fases 1–4 já
entregam o Tech Challenge atual; a Fase 5 consolida os itens em **aberto** do
[checklist](../../docs/05-checklist-entrega.md)/STATE. **Implementado o viável neste ambiente:**
(F5-04) **dashboard React** de produção em `frontend/` (React+Vite+TS, react-query, socket.io-client),
substituindo o cliente mínimo — backend ganhou `GET /casos`, `GET /casos/:id`, `GET /casos/:id/relatorio`
e serve `frontend/dist` (SPA); (F5-05) **reforço dos sinais vitais** com pré-eclâmpsia sintética
(`scripts/data_prep/preeclampsia_sintetico.py` + `treino.comparar_com_aumento` +
`scripts/reforco_sinais_vitais.py`); (F5-06 parcial) **hardening** — `/ready`, job de CI do frontend,
`frontend/Dockerfile`+nginx (proxy REST+WS) e serviço `frontend` no compose (`:8080`).
**Bloqueado por ambiente** (código pronto/Azure-ready; degrada sem quebrar — DD10): ~~(F5-01) escalar o
detector de **cicatriz**~~ **concluído** (treino em GPU/Colab, 41 épocas, mAP50≈0.995; `best.pt`
versionado); (F5-02) **áudio/fisioterapia** exigem amostras com
licença (obtenção manual); (F5-03) **deploy real na Azure** exige conta/credenciais. **Gate verde:**
`ruff` + `pytest` (**102 testes** Python: 96 base + 6 da Fase 5); `eslint`+`jest` (**18 testes** Node:
11 base + 7) e `eslint`+`vitest`+`build` (**7 testes** frontend). Decisões de escopo (Whisper vs. Azure
Speech, LFS vs. métricas, deploy A/B, SQLite vs. Postgres) ainda na spec — defaults aplicados: Whisper
local, só métricas, SQLite. **Vídeo + integrantes** permanecem **ação humana**.

**Fase 4 — Empacotamento e Entregáveis** — **implementada** (T1–T9).
Plano em [`.specs/features/fase4-entregaveis/`](../features/fase4-entregaveis/): 14 requisitos
(F4E-01..F4E-14) e 9 tarefas (T1–T9). Fase de **documentação/empacotamento** (não cria código de produto):
auditou o **repositório** (4.1 — README reenquadrado como projeto completo, estrutura/deps/`.gitignore`/
disclaimer confirmados), consolidou **evidências reais** em `docs/relatorio/` (tabela legível de
`models/metricas_fusao.json`, **exemplo de relatório automático** gerado por `scripts/gerar_evidencias.py`
reusando `app/relatorio.py` sobre `caso_alto`, e **log E2E** real do `scripts/e2e_demo.py` com `case_id`),
escreveu o **relatório técnico** (`docs/relatorio-tecnico.md`, 6 seções do PDF, cada métrica rastreável ao
artefato de origem) com **diagrama Mermaid inline** (`docs/relatorio/diagrama-arquitetura.md`) e
**exportação** via `scripts/exportar_relatorio.py` (PDF com fallback HTML — gerou `docs/relatorio-tecnico.html`
neste ambiente, sem `weasyprint`), e o **roteiro do vídeo** (`docs/roteiro-video.md`, 8 pontos, ~14 min). O
README ganhou **créditos/integrantes** (placeholders) e **placeholder do link do vídeo**; o checklist
(`docs/05`) foi revisado item a item. Decisões DD-F4-1..DD-F4-8 aplicadas. **Gate verde** num ambiente
limpo: `ruff check scripts ai-service` + `pytest` (**96 testes** Python) e `npm run lint`/`npm test`
(**11 testes** Node). Observações do ambiente: sem pesos YOLO/ASR a cicatriz/áudio degradam (DD10) e a
fusão do `caso_alto` fecha **MEDIO** (vitais+texto); o cenário de referência com pesos treinados escala
para **ALTO** (infecção puerperal) — ambos no relatório/log. **Pendência humana:** gravar/publicar o
**vídeo** ("Não listado") e colar o link no README; preencher os integrantes.

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
Treinos reais executados: **sinais vitais** (Random Forest, 451 amostras, acurácia≈0.65/F1≈0.62) e
**cicatriz** (YOLOv8n, agora **escalado** em GPU/Colab — 41 épocas, mAP50≈0.995, precisão≈0.99,
recall≈0.99; `best.pt` versionado — supera o smoke inicial de 6 imagens).
**Texto/NLP** 5/5 vs. rótulos. **Áudio/fisioterapia**: classificadores/geometria testados; treino/
inferência completa exige dados de obtenção manual (degradam sem quebrar — DD10).
Observações do ambiente: Python **3.12** (não 3.13; dentro da faixa suportada); o detector de
cicatriz foi **escalado** (GPU/Colab, 41 épocas) e já detecta com precisão/recall ≈0.99 — **F5-01
concluído**.

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
| S7  | Serviço de IA em `ai-service/app/`. **Revisado (2026-06-27):** os pesos treinados (`best.pt`, `*.joblib`) **passaram a ser versionados** — ver "Decisão pendente" sobre Git LFS | [F2 design DD1/DD4](../features/fase2-modelos/design.md)       |
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
| S20 | Relatório em `docs/relatorio-tecnico.md` (Markdown); PDF como exportação | [F4 design DD-F4-1](../features/fase4-entregaveis/design.md) |
| S21 | Exportação de PDF com **fallback HTML/Markdown** (libs de PDF opcionais) | [F4 design DD-F4-2](../features/fase4-entregaveis/design.md) |
| S22 | Diagramas **Mermaid inline** (`mermaid-studio` não instalada)             | [F4 design DD-F4-3](../features/fase4-entregaveis/design.md) |
| S23 | **Reusar artefatos reais** (métricas/exemplo/log); nunca inventar números | [F4 design DD-F4-4](../features/fase4-entregaveis/design.md) |
| S24 | **Vídeo = roteiro + placeholder de link**; gravação/publicação é humana   | [F4 design DD-F4-5](../features/fase4-entregaveis/design.md) |
| S25 | Limitações documentadas honestamente (smoke da cicatriz; degradação)      | [F4 design DD-F4-6](../features/fase4-entregaveis/design.md) |
| S26 | Áudio = **análise dupla** (acústico + transcrição→texto); categoria legada **derivada** | [F8 spec](../features/fase8-audio-texto-unificado/spec.md) |
| S27 | Texto = **ML** (depressão/violência, PT-BR) + keywords; depressão sai de `complicacao` | [F8 spec](../features/fase8-audio-texto-unificado/spec.md) |
| S28 | Tradução EN→PT = **Argos** (padrão, CPU/MIT); X-ALMA opcional por env (sem baixar 13B) | [F8 spec](../features/fase8-audio-texto-unificado/spec.md) |
| S29 | Datasets F8: `ShreyaR`, `Spiderman01`, `Hemg` (licença **não especificada** — risco); descartado `singhsandk` (14 linhas) | [F8 spec](../features/fase8-audio-texto-unificado/spec.md) |

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
- [x] **Escalar o detector de cicatriz** (mais dados/épocas em GPU/Colab) — **concluído** (41 épocas,
      mAP50≈0.995, precisão/recall≈0.99; `best.pt` versionado).
- [ ] Obter amostras de **áudio** e **fisioterapia** (manual) e rodar o baseline completo dessas modalidades.
- [x] Planejar a Fase 3 (spec → design → tasks em `.specs/features/fase3-fusao-e-nuvem/`).
- [x] Implementar a Fase 3 seguindo `tasks.md` (T1–T18): fusão, pipeline, FastAPI, relatório, métricas,
      backend Node (CRUD + `/analisar` + alerta socket.io), storage Azure/local, Docker/compose, CI e E2E.
      Gate verde (ruff + 96 testes Python; eslint + 11 testes Node).
- [ ] Decisão pendente do grupo: **deploy real na Azure** vs. fallback local para a gravação da demo (T17).
- [x] Runtime/versões fixadas no `backend/package.json` (Node 22 LTS, última estável das libs) e nas
      deps Python adicionadas em `ai-service/requirements.txt`.
- [x] **Escalar o detector de cicatriz** (GPU/Colab) — **concluído**; com os pesos, o `caso_alto` fecha
      `ALTO` num ambiente com `ultralytics`/`torch` (regenerar o log E2E nesse ambiente — pendente).
- [x] Planejar a Fase 4 (spec → design → tasks em `.specs/features/fase4-entregaveis/`): repositório,
      relatório técnico e vídeo (14 requisitos F4E-01..F4E-14, 9 tarefas T1–T9).
- [x] Implementar a Fase 4 seguindo `tasks.md` (T1–T9): auditoria do repo, evidências, relatório técnico
      (+PDF/HTML fallback), roteiro do vídeo, README (créditos/link), checklist + gate, STATE/docs/04.
      Gate verde (ruff + 96 testes Python; eslint + 11 testes Node).
- [ ] **Ação humana (grupo):** gravar e publicar o **vídeo** (≤15 min, "Não listado") e colar o link no
      README — o agente entrega o roteiro (`docs/roteiro-video.md`) e o placeholder.
- [x] Planejar a Fase 5 (Specify, RASCUNHO em `.specs/features/fase5-producao-e-escala/` + `docs/08`):
      6 requisitos F5-01..F5-06 consolidando os itens em aberto do checklist/STATE.
- [ ] **Confirmar o escopo da Fase 5 com o grupo** (ver "Decisões a confirmar" na spec): é Produção/Escala
      ou outro desafio 8IADT? Whisper vs. Azure Speech; Git LFS vs. métricas; deploy A/B; SQLite vs. Postgres;
      profundidade do dashboard.
- [ ] Após confirmação: **Design** (decisões técnicas) → **Tasks** (quebra atômica) → Execute da Fase 5.
- [x] Planejar a Fase 6 (Specify em `.specs/features/fase6-relatorios-automaticos/` + `docs/09`):
      5 requisitos F6-01..F6-05 fechando a lacuna entre `docs/06` (relatórios especializados) e o código.
- [x] Implementar a Fase 6 (F6-01..F6-05): encaminhamento especializado por gatilho, anexos com links reais,
      PDF garantido (libs no Dockerfile + fallback HTML), pré-visualização no dashboard e testes/evidências.
      Gate verde (ruff + 107 testes Python; eslint+vitest+build do frontend). Defaults da spec aplicados.
- [ ] **Confirmar com o grupo** os defaults aplicados na Fase 6 (origem do encaminhamento, anexos no fallback
      local, libs de PDF na imagem, profundidade do preview) — revisáveis se o escopo divergir.
- [x] Planejar a Fase 7 (Specify em `.specs/features/fase7-privacidade-e-seguranca/` + `docs/10`): 8 requisitos
      F7-01..F7-08 fechando a lacuna entre os controles do `docs/07` (LGPD) e o código (auth, TLS, auditoria de
      acesso, retenção, pseudonimização, hardening, Key Vault opcional, conformidade no CI).
- [x] Implementar a Fase 7 (F7-01..F7-08): auth de serviço (backend + ai-service), TLS opt-in na borda,
      auditoria de acesso (tabela `auditoria`), retenção (`npm run retencao`), pseudonimização (`case_id` opaco
      + minimização de PII), hardening (helmet/CORS/headers/upload), Key Vault opcional e conformidade no CI +
      docs. Gate verde (ruff + 111 testes Python; eslint + 32 testes Node; vitest + 7 frontend). Defaults da
      spec aplicados.
- [ ] **Confirmar com o grupo** os defaults aplicados na Fase 7 (auth opt-in via `API_KEY`/`AUTH_REQUIRED`;
      terminação TLS no nginx; trilha em SQLite; TTL de retenção; minimização de PII removendo `primeiro_nome`
      do payload à IA; Key Vault opcional) — revisáveis se o escopo divergir.
- [ ] **Ação humana/infra:** provisionar RBAC/Private Endpoint reais na Azure (F5-03) e gravar o vídeo
      demonstrando os controles (DD-F4-5).
- [x] Implementar a Fase 8 (F8-01..F8-10): trilha acústica de violência + classificadores ML de
      depressão/violência (PT-BR, datasets EN traduzidos offline), áudio/texto unificados, fusão com
      novos gatilhos, sem Azure. Gate verde (ruff + 129 testes Python). Pesos não versionados.
- [x] **Treino da Fase 8 concluído** (2026-06-27): `app.texto.treino` + `app.audio.treino` geraram os
      pesos/métricas reais (depressão F1≈0,93; violência texto F1=1,0 ⚠️; violência acústica F1≈0,94);
      pesos versionados.
- [x] **Investigado o F1=1,0 da violência (texto)** — causa: **vazamento de fonte/domínio** (negativos de
      outro corpus). **Corrigido no código** (2026-06-27): `scripts/data_prep/fase8_datasets._negativos_violencia`
      usa negativos do **mesmo domínio** (ShreyaR neutro+depressão) e `app/texto/treino.construir_pipeline`
      foi **regularizado** (`min_df` adaptativo, `max_features=5000`, `sublinear_tf`, L2 `C=0.5`).
- [x] **Retreinado a violência (texto)** (2026-06-27) com a correção (negativos do mesmo domínio +
      regularização): **F1 permaneceu 1,0** (273+273 amostras). **Conclusão:** o teto é de **dados** —
      positivos (`Spiderman01`, 273, positivos-only) e negativos (`ShreyaR`) são **datasets distintos** →
      separáveis por fonte, não por semântica. Não generaliza. A detecção de violência se apoia em
      **acústico + keywords + transcrição** (camadas da fusão), não neste classificador isolado.
- [ ] **(Opcional, decisão do grupo)** Obter um **único dataset** com rótulos violência/não-violência da
      **mesma fonte** para um F1 de violência (texto) realista — caso contrário, manter o classificador como
      baseline limitado e documentado.
- [x] **Regenerado `models/metricas_fusao.json`** (2026-06-27, Python 3.12) — fusão precisão/recall 1,0,
      FP 0,0 vs. modalidades isoladas. **Pendente:** regenerar `models/baseline.json` (`python -m app.baseline`,
      precisa das deps de IA) e o log E2E com os pesos reais.
- [ ] **Decisão do grupo:** versionar `best.pt` (6 MB) via **Git LFS** vs. commit direto (hoje commitado
      direto); confirmar os defaults da Fase 8 (Argos vs. X-ALMA; categoria de áudio derivada).

## Ideias adiadas

- Escalar mini-dataset (de 5 para mais amostras) só após o pipeline rodar ponta-a-ponta (Fase 3).
- Datasets sintéticos extras de pré-eclâmpsia (HF) para reforçar a modalidade de sinais vitais.

## Lições

- Na Fase 4, as libs pesadas de IA (torch/ultralytics/whisper/cv2) são importadas **lazy** dentro das
  funções; o gate (`ruff`+`pytest` / `eslint`+`jest`) roda com um **conjunto enxuto** de deps
  (fastapi, pydantic, scikit-learn, pandas, markdown, pytest, ruff) — útil para validar em ambiente limpo.
- Exportação para PDF (`weasyprint`) exige **libs de sistema**; sem elas o fallback HTML mantém a entrega
  (DD-F4-2). Os diagramas Mermaid não renderizam no HTML simples — o Markdown é a fonte de verdade.
- Tarefas leves (validação, atualização de STATE, checklist) rodam bem com modelos mais rápidos/baratos.
