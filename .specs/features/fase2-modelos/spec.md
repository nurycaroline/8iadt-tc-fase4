# Fase 2 — Desenvolvimento dos Modelos Individuais — Especificação

> Documento de planejamento gerado a partir de [`docs/02-fase2-modelos.md`](../../../docs/02-fase2-modelos.md).
> Fonte de escopo: [`docs/00-visao-geral-e-escopo.md`](../../../docs/00-visao-geral-e-escopo.md),
> [`docs/contrato-api.md`](../../../docs/contrato-api.md), [`docs/datasets.md`](../../../docs/datasets.md)
> e [`docs/03-fase3-fusao-e-nuvem.md`](../../../docs/03-fase3-fusao-e-nuvem.md) (consumidor das saídas).
> Insumos prontos: mini-dataset da [Fase 1](../fase1-dados/) em `data/`.

## Problem Statement

A Fase 1 entregou o mini-dataset limpo das 4 modalidades (vídeo — com dois usos: cicatriz e
fisioterapia —, sinais vitais, áudio e texto clínico) e o caso de exemplo sintético. Agora é preciso **construir e
validar cada IA separadamente**, antes de uni-las. Sem modelos individuais funcionando e com **métricas
próprias** — e sem uma **saída padronizada** (um dicionário por modalidade alinhado ao
[contrato de API](../../../docs/contrato-api.md)) — o **motor de fusão da Fase 3** não tem o que cruzar e
não há **baseline por modalidade única** para provar que a fusão agrega valor.

## Goals

- [ ] Modelo de **vídeo — cicatriz** (YOLOv8) treinado e **exportado** (`.pt`/`.onnx`) com métricas
      (mAP@0.5, precisão/recall por classe).
- [ ] Modelo de **vídeo — fisioterapia** (YOLOv8-pose) funcionando, com avaliação de movimento
      (execução `correta`/`incorreta` + amplitude).
- [ ] Modelo de **sinais vitais** treinado (Random Forest; Isolation Forest opcional) com métricas
      (acurácia, F1, matriz de confusão) e modelo persistido (`joblib`).
- [ ] Módulo de **áudio** funcionando (transcrição + classificação) com exemplos.
- [ ] Módulo de **texto/NLP** funcionando com exemplos.
- [ ] **Saída padronizada** por modalidade: um dicionário Python por modalidade, **alinhado ao
      [contrato de API §3](../../../docs/contrato-api.md)**, pronto para a fusão.
- [ ] **Limiares clínicos** (gatilhos) documentados e implementados num único módulo
      ([Tarefa 2.7](../../../docs/02-fase2-modelos.md)).
- [ ] **Baseline por modalidade única** registrada (para comparar com a fusão na Fase 3).
- [ ] Métricas e gráficos salvos (matriz de confusão, curvas YOLO) para o relatório técnico.

## Out of Scope

Explicitamente excluído para evitar scope creep. Cada item pertence a outra fase.

| Item                                                        | Motivo / Onde entra                          |
| ----------------------------------------------------------- | -------------------------------------------- |
| **Motor de fusão** / derivação combinada de risco           | Fase 3 (regras que cruzam as modalidades)    |
| API Python (FastAPI `POST /inferencia`), Node, WebSocket    | Fase 3                                        |
| Deploy na Azure (Blob, App Service/Functions)               | Fase 3                                        |
| Relatórios automáticos e dashboard                          | Fases 3/4                                     |
| Aquisição/preparação de dados (download/limpeza/conversão)  | Fase 1 (já concluída) — esta fase **consome** |
| Escalar treino (mais dados/épocas, GPU/Colab em produção)   | Após o pipeline rodar ponta-a-ponta (Fase 3) |
| Dados reais de pacientes                                     | LGPD — só dados públicos/sintéticos          |
| Versionar pesos treinados grandes (`.pt`/`.onnx`)           | `models/` ignorado; só métricas versionadas  |

---

## User Stories

### P1: Fundação do serviço de IA e contrato de saída ⭐ MVP

**User Story**: Como integrante do grupo, quero a estrutura do `ai-service/` com utilidades
compartilhadas, os **schemas de saída padronizados** (dicionários de evidência) e os **limiares
clínicos** num único lugar, para que cada modelo produza uma saída coerente com o contrato de API e a
Fase 3 consuma sem retrabalho.

**Why P1**: É a fundação de todas as modalidades. Sem a saída padronizada e os limiares centralizados,
cada modelo divergiria do contrato e a fusão da Fase 3 quebraria.

**Acceptance Criteria**:

1. WHEN o `ai-service/` é criado THEN o sistema SHALL conter um pacote Python com `common.py`
   (resolução de caminhos para `data/` e `models/`, logging com `case_id`, IO de métricas).
2. WHEN um construtor de evidência é chamado (ex.: `evidencia_cicatriz`, `evidencia_sinais_vitais`)
   THEN ele SHALL retornar um dicionário com **apenas valores permitidos** pelo
   [contrato de API §3](../../../docs/contrato-api.md) e SHALL rejeitar valores fora do domínio.
3. WHEN os limiares são consultados THEN o módulo `limiares.py` SHALL expor os gatilhos da
   [Tarefa 2.7](../../../docs/02-fase2-modelos.md) (PA ≥ 140/90; classe `high risk`; cicatriz
   `ferida_alerta` com confiança ≥ 0.7; áudio risco ≥ 0.7; achado de risco no texto).
4. WHEN o gate roda THEN `ruff check` e `pytest` SHALL passar para os schemas e limiares.

**Independent Test**: Importar `schemas` e `limiares`, construir um dicionário de cada modalidade e
verificar que valores inválidos são rejeitados e que os limiares retornam os gatilhos documentados.

---

### P1: Modelo de sinais vitais com métricas e saída padronizada ⭐ MVP

**User Story**: Como engenheiro de dados, quero treinar um classificador de risco materno sobre o
`maternal_clean.csv` (Fase 1), avaliar com métricas e expor uma função de inferência que devolve o
dicionário padronizado, para que a fusão receba o risco de sinais vitais.

**Why P1**: É a modalidade mais simples/barata (tabular) e o "hello world" da fase; alimenta o baseline
e a fusão rapidamente.

**Acceptance Criteria**:

1. WHEN o script de treino roda THEN ele SHALL treinar um **Random Forest** sobre as features
   (`SystolicBP`, `DiastolicBP`, `BS`, `BodyTemp`, `HeartRate`, `Age`) com alvo `RiskLevel`
   (`low/mid/high`) a partir de `data/sinais_vitais/maternal_clean.csv`.
2. WHEN a avaliação termina THEN o script SHALL reportar **acurácia, F1 e matriz de confusão** e
   salvar as métricas (`metrics.json`) e o gráfico da matriz de confusão.
3. WHEN o treino termina THEN o modelo SHALL ser **persistido** (`joblib`) em `ai-service/models/sinais_vitais/`.
4. WHEN a inferência roda THEN ela SHALL retornar `{"tipo": ..., "valor": ...}` com `tipo` em
   `normal/risco_medio/hipertensao/pre_eclampsia` (derivado da classe + limiares de PA), conforme o contrato.
5. WHEN o CSV tem poucas amostras THEN o treino SHALL usar uma divisão treino/validação robusta a
   amostras pequenas (sem quebrar), registrando a limitação.

**Independent Test**: Rodar o treino, conferir `metrics.json` + matriz de confusão e o `.joblib`;
chamar a inferência num registro de PA alta e confirmar `tipo` = `hipertensao`/`pre_eclampsia`.

---

### P1: Detector de cicatriz (YOLOv8) treinado, exportado e com saída padronizada ⭐ MVP

**User Story**: Como engenheiro de visão computacional, quero fazer fine-tuning do YOLOv8 sobre a
amostra YOLO da Fase 1, avaliar (mAP/precisão/recall), exportar o modelo e expor a inferência que
devolve o dicionário padronizado, para detectar **sinal de infecção** na cicatriz.

**Why P1**: É o item do **caminho crítico** (treino de YOLO é o mais demorado — começar cedo) e cobre o
requisito obrigatório de **análise de vídeo** do desafio.

**Acceptance Criteria**:

1. WHEN o treino roda THEN ele SHALL fazer fine-tuning de **YOLOv8n/s** usando
   `data/video_cicatriz/data.yaml` (classes `ferida_ok`, `ferida_alerta`), com poucas épocas no mini-dataset.
2. WHEN a avaliação termina THEN o script SHALL reportar **mAP@0.5, precisão e recall por classe** e
   salvar as métricas/curvas geradas pelo Ultralytics.
3. WHEN o export roda THEN o modelo SHALL ser exportado em **ONNX** (e/ou `.pt`) para `ai-service/models/cicatriz/`.
4. WHEN a inferência roda THEN ela SHALL retornar `{"evento": ..., "confianca": ...}` com `evento` em
   `ferida_ok/sinal_infeccao/nenhum`, **mapeando** a classe `ferida_alerta` → `sinal_infeccao` e
   aplicando o limiar de confiança (≥ 0.7).
5. WHEN não há detecção acima do limiar THEN a inferência SHALL retornar `evento = nenhum` sem quebrar.

**Independent Test**: Rodar o treino (mini-dataset), conferir as métricas/curvas e o arquivo exportado;
rodar a inferência numa imagem `ferida_alerta` e confirmar `evento` = `sinal_infeccao` com confiança.

---

### P1: Módulo de texto/NLP com saída padronizada ⭐ MVP

**User Story**: Como engenheiro de NLP, quero um módulo que leia os documentos de
`data/texto_clinico/` e classifique o achado de risco, para fechar a tríade "áudio, vídeo e texto" e
alimentar a fusão com contexto textual.

**Why P1**: É barato e determinístico (regras/palavras-chave), fecha o requisito de texto e dá retorno
rápido para o baseline.

**Acceptance Criteria**:

1. WHEN um texto clínico é analisado THEN o módulo SHALL retornar `{"achado": ..., "trecho": ...}` com
   `achado` em `complicacao/sinal_infeccao/neutro`, conforme o contrato.
2. WHEN o texto contém termos de risco (ex.: febre, dor na cicatriz, proteinúria, PA alta, secreção)
   THEN o módulo SHALL identificar o achado correspondente e devolver o trecho que o disparou.
3. WHEN executado sobre os 5 documentos da Fase 1 THEN o módulo SHALL produzir exemplos coerentes com
   os rótulos de `data/texto_clinico/rotulos.json`.

**Independent Test**: Rodar o módulo nos 5 documentos e comparar os achados com `rotulos.json`.

---

### P2: Módulo de áudio (transcrição + classificação) com saída padronizada

**User Story**: Como engenheiro de áudio, quero transcrever os áudios de `data/audio/` e classificar a
categoria de risco psicológico/violência, para alimentar a fusão com o sinal de fala.

**Why P2**: Depende de amostras de áudio (obtenção manual na Fase 1) e tem limitação de domínio; usa a
transcrição já prototipada na Fase 1.

**Acceptance Criteria**:

1. WHEN um áudio é processado THEN o módulo SHALL transcrevê-lo (Whisper local; backend Azure trocável
   por env var, reaproveitando a lógica da Fase 1) e classificá-lo.
2. WHEN a classificação roda THEN ela SHALL retornar `{"categoria": ..., "confianca": ...}` com
   `categoria` em `neutro/ansiedade/depressao_pos_parto/violencia/fadiga`, conforme o contrato.
3. WHEN a confiança de risco fica abaixo do limiar (0.7) THEN a categoria de risco SHALL ser tratada
   como contexto fraco (a fusão decide), sem quebrar.
4. WHEN não há áudio disponível THEN o módulo SHALL degradar com mensagem clara (modalidade ausente).

**Independent Test**: Rodar o módulo sobre os áudios disponíveis e conferir a categoria/confiança no
metadados gerado; validar a classificação por palavras-chave em transcrições conhecidas.

---

### P2: Baseline por modalidade única

**User Story**: Como responsável pelas métricas, quero registrar a performance de **cada modalidade
isolada** detectando o evento de risco, para servir de comparação e provar, na Fase 3, que a fusão
reduz falsos positivos / melhora a detecção.

**Why P2**: Depende de todas as modalidades terem inferência pronta; é a base da [Tarefa 3.1b](../../../docs/03-fase3-fusao-e-nuvem.md).

**Acceptance Criteria**:

1. WHEN o baseline roda THEN ele SHALL calcular, por modalidade isolada (vídeo, sinais vitais,
   áudio/texto), as métricas de detecção do evento de risco sobre o mini-dataset / casos de exemplo.
2. WHEN o baseline termina THEN ele SHALL salvar um `baseline.json` com precisão, recall e **taxa de
   falsos positivos** por modalidade.
3. WHEN uma modalidade não tem amostra/modelo THEN o baseline SHALL omiti-la sem quebrar e registrar a omissão.

**Independent Test**: Rodar o baseline e conferir `baseline.json` com as métricas por modalidade.

---

### P3: Análise de fisioterapia (YOLOv8-pose)

**User Story**: Como engenheiro de visão, quero estimar keypoints nos dados de fisioterapia, derivar
ângulos/repetições e classificar a execução, para acompanhar a recuperação física e alimentar a fusão.

**Why P3**: Segundo uso do vídeo; útil, mas a detecção de cicatriz já cobre o requisito de vídeo do MVP,
e depende de amostras de obtenção manual (IntelliRehabDS).

**Acceptance Criteria**:

1. WHEN o módulo roda THEN ele SHALL estimar keypoints com **YOLOv8-pose** (ou reaproveitar keypoints
   fornecidos) a partir de `data/video_fisioterapia/`.
2. WHEN os keypoints são processados THEN o módulo SHALL derivar ângulos/repetições/amplitude (funções
   puras) e classificar a execução como `correta`/`incorreta`.
3. WHEN a inferência roda THEN ela SHALL retornar `{"execucao": ..., "amplitude": ...}` com `execucao`
   em `correta/incorreta/nao_avaliado`, conforme o contrato.
4. WHEN não há amostra de fisioterapia THEN o módulo SHALL retornar `execucao = nao_avaliado` sem quebrar.

**Independent Test**: Rodar o módulo sobre uma amostra e conferir o ângulo/amplitude calculado e a
execução; validar a derivação de ângulo em keypoints sintéticos conhecidos.

---

## Edge Cases

- WHEN os pesos de um modelo não existem (ainda não treinado) THEN a inferência SHALL retornar o valor
  neutro da modalidade (`nenhum`/`nao_avaliado`) com mensagem clara, sem derrubar o pipeline da Fase 3.
- WHEN o mini-dataset é muito pequeno (1–2 imagens / poucos registros) THEN o treino SHALL rodar como
  **smoke** (poucas épocas / split robusto) e documentar que as métricas são ilustrativas.
- WHEN o export ONNX falha por dependência ausente THEN o script SHALL falhar com instrução clara e
  manter o `.pt` como fallback.
- WHEN o áudio não tem `ffmpeg` THEN a transcrição SHALL usar o caminho via `soundfile` (como na Fase 1).
- WHEN uma classe não aparece no conjunto de validação THEN o cálculo de métricas SHALL lidar com
  classes ausentes (sem dividir por zero) e registrar a limitação.
- WHEN a inferência recebe entrada de modalidade ausente THEN ela SHALL omitir/neutralizar a evidência,
  pois os campos são opcionais no contrato.

---

## Requirement Traceability

| Requirement ID | Story                                       | Phase | Status  |
| -------------- | ------------------------------------------- | ----- | ------- |
| F2M-01         | P1: Fundação (estrutura + common)           | Tasks | Pending |
| F2M-02         | P1: Fundação (schemas de saída)             | Tasks | Pending |
| F2M-03         | P1: Fundação (limiares clínicos)            | Tasks | Pending |
| F2M-04         | P1: Sinais vitais (treino RF)               | Tasks | Pending |
| F2M-05         | P1: Sinais vitais (métricas + persistência) | Tasks | Pending |
| F2M-06         | P1: Sinais vitais (inferência → dict)       | Tasks | Pending |
| F2M-07         | P1: Cicatriz (treino YOLOv8)                | Tasks | Pending |
| F2M-08         | P1: Cicatriz (métricas mAP/P/R)             | Tasks | Pending |
| F2M-09         | P1: Cicatriz (export ONNX/PT)               | Tasks | Pending |
| F2M-10         | P1: Cicatriz (inferência → dict)            | Tasks | Pending |
| F2M-11         | P1: Texto/NLP (inferência → dict)           | Tasks | Pending |
| F2M-12         | P2: Áudio (transcrição + classificação)     | Tasks | Pending |
| F2M-13         | P3: Fisioterapia (pose + execução)          | Tasks | Pending |
| F2M-14         | P2: Baseline por modalidade única           | Tasks | Pending |
| F2M-15         | P1: Documentação de limiares + métricas     | Tasks | Pending |

**ID format:** `F2M-[NUMBER]` (Fase 2 Modelos).
**Status values:** Pending → In Design → In Tasks → Implementing → Verified.
**Coverage:** 15 requisitos, todos mapeados para tarefas em `tasks.md`.

---

## Success Criteria

Como saberemos que a Fase 2 está pronta. O **gate de fim de fase** do
[cronograma](../../../docs/cronograma-dependencias.md) §4 exige **4 modelos com métricas individuais**.
Os 4 modelos que contam para o gate são: **cicatriz** (vídeo/detecção), **sinais vitais**, **áudio** e
**texto**. A **fisioterapia** (segundo uso do vídeo, P3) é exigida pelo DoD de
[`docs/02-fase2-modelos.md`](../../../docs/02-fase2-modelos.md), mas é **opcional para o gate**.

Itens obrigatórios para o gate:

- [ ] **Cicatriz** (vídeo): YOLOv8 treinado + **exportado** (`.pt`/`.onnx`) + mAP/precisão/recall registrados.
- [ ] **Sinais vitais**: modelo persistido + acurácia/F1/matriz de confusão.
- [ ] **Áudio**: transcrição + classificação funcionando com exemplos coerentes com os rótulos da Fase 1.
- [ ] **Texto**: módulo funcionando com exemplos coerentes com `data/texto_clinico/rotulos.json`.
- [ ] Cada um dos 4 modelos produz **saída individual** (dicionário padronizado) com **métricas próprias**.
- [ ] **Limiares clínicos** centralizados em `limiares.py` e documentados.
- [ ] **Baseline por modalidade única** salvo (`baseline.json`) para comparação na Fase 3.
- [ ] Cada saída é **compatível com o [contrato de API §3](../../../docs/contrato-api.md)** (valores válidos).
- [ ] Gate verde: `ruff check` + `pytest` (funções puras: schemas, limiares, derivações, classificadores).

Item do DoD (não bloqueia o gate):

- [ ] **Fisioterapia** (P3): YOLOv8-pose avaliando execução (`correta`/`incorreta` + amplitude).
