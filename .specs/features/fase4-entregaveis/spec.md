# Fase 4 — Empacotamento e Entregáveis — Especificação

> Documento de planejamento gerado a partir de [`docs/04-fase4-entregaveis.md`](../../../docs/04-fase4-entregaveis.md).
> Fontes de escopo: [`docs/05-checklist-entrega.md`](../../../docs/05-checklist-entrega.md),
> [`docs/06-relatorios-automaticos.md`](../../../docs/06-relatorios-automaticos.md),
> [`docs/07-privacidade-e-seguranca.md`](../../../docs/07-privacidade-e-seguranca.md),
> [`docs/arquitetura.md`](../../../docs/arquitetura.md),
> [`docs/qualidade-testes-ci.md`](../../../docs/qualidade-testes-ci.md) e
> [`docs/contrato-api.md`](../../../docs/contrato-api.md).
> Insumos prontos (implementados): a stack ponta-a-ponta da [Fase 3](../fase3-fusao-e-nuvem/)
> (fusão, pipeline, FastAPI, backend Node, alerta em tempo real, relatório automático, **métrica do
> ganho da fusão** em `ai-service/models/metricas_fusao.json`, Docker/compose, CI, E2E em
> `scripts/e2e_demo.py`) e as métricas reais da [Fase 2](../fase2-modelos/)
> (`ai-service/models/cicatriz/metrics.json`, `ai-service/models/sinais_vitais/{metrics.json,matriz_confusao.png}`,
> `ai-service/models/baseline.json`).

## Problem Statement

As Fases 1–3 entregaram a solução **funcionando ponta-a-ponta** (dados → modelos → fusão → API → alerta
em tempo real → relatório automático), com **CI verde** e reprodutibilidade por Docker. O que **ainda não
existe** é o **empacotamento avaliado** do Tech Challenge: os **3 entregáveis** que valem nota — um
**repositório Git** organizado e auditado, um **relatório técnico** completo (que consolida arquitetura,
modelos, lógica de fusão, métricas e LGPD) e um **vídeo de demonstração** de até 15 min.

Sem a Fase 4, o trabalho técnico das fases anteriores **não fica legível nem submissível**: não há um
documento único que prove as escolhas e os resultados, nem um roteiro que demonstre o fluxo do alerta de
ponta a ponta. Esta fase **não constrói código novo de produto** — ela **empacota, documenta e evidencia**
o que já existe, com padrão de engenharia de software, e produz os artefatos de entrega.

## Goals

- [ ] **Repositório Git finalizado e auditado** conforme a [Tarefa 4.1](../../../docs/04-fase4-entregaveis.md):
      estrutura em pastas (`/ai-service`, `/backend`, `/docs`, `/scripts`), `requirements.txt`/`package.json`
      com versões fixadas, `README.md` com instruções de execução reproduzíveis do zero, `.gitignore`
      cobrindo `data/`/`.env`/pesos, **disclaimer ético** visível, Docker/CI/testes presentes e verdes.
- [ ] **Relatório técnico completo** (`docs/relatorio-tecnico.md`) com as **6 seções exigidas pelo PDF**:
      (1) fluxo multimodal + diagrama de arquitetura; (2) modelos por modalidade + justificativas;
      (3) lógica de fusão + **métrica do ganho da fusão** vs. modalidade única; (4) resultados e exemplos
      de anomalias (métricas, matriz de confusão, mAP); (5) privacidade/segurança (LGPD); (6) exemplo de
      relatório automático gerado.
- [ ] **Evidências consolidadas** para o relatório e o vídeo, **reaproveitando os artefatos reais** já
      gerados (métricas da Fase 2, `metricas_fusao.json`, matriz de confusão, exemplo de relatório
      automático e prints/logs do E2E), sem inventar números.
- [ ] **Exportação do relatório para PDF** (a partir do Markdown), com **fallback** para Markdown/HTML
      quando as libs de conversão não estiverem disponíveis no ambiente.
- [ ] **Roteiro de vídeo** detalhado (`docs/roteiro-video.md`) cobrindo os 8 pontos do roteiro sugerido,
      com o que mostrar na tela, comandos e mapeamento para as evidências — pronto para a gravação.
- [ ] **Vídeo publicado** (≤15 min, YouTube/Vimeo "Não listado") com o **link no `README.md`** e a
      seção de **créditos/integrantes** — a gravação/publicação é **ação humana** (ver Out of Scope).
- [ ] **Checklist de entrega** ([`docs/05-checklist-entrega.md`](../../../docs/05-checklist-entrega.md))
      revisado item a item e **gate de qualidade verde** confirmado (lint + testes dos dois serviços),
      rodando o pipeline limpo do zero seguindo só o README.

## Out of Scope

Explicitamente excluído para evitar scope creep. Cada item pertence a outra fase/feature ou é ação humana.

| Item                                                            | Motivo / Onde entra                                                  |
| --------------------------------------------------------------- | -------------------------------------------------------------------- |
| Código novo de produto (fusão, pipeline, API, backend, alerta)  | Entregue na [Fase 3](../fase3-fusao-e-nuvem/) — esta fase **documenta/empacota** |
| Treino/ajuste dos modelos individuais                           | [Fase 2](../fase2-modelos/) — o relatório **reporta** as métricas já obtidas |
| Aquisição/preparação de dados                                   | [Fase 1](../fase1-dados/)                                            |
| **Gravação e publicação do vídeo** no YouTube/Vimeo             | **Ação humana** do grupo (sem credencial/captura no agente); a fase entrega o **roteiro** e o ponto de inserir o link |
| **Escalar o detector de cicatriz** (GPU/Colab) p/ detectar acima do limiar | Item de STATE; o relatório documenta a limitação atual (smoke) honestamente |
| **Deploy real na Azure** (provisionar conta/recursos)           | Documentado em [`docs/deploy-azure.md`](../../../docs/deploy-azure.md); o relatório descreve a integração + **fallback local** |
| Dashboard React completo                                        | Feature de front-end própria; a demo usa o **cliente mínimo** da Fase 3 |
| Dados reais de pacientes                                        | LGPD — só dados públicos/sintéticos (ver [`docs/07`](../../../docs/07-privacidade-e-seguranca.md)) |

---

## User Stories

### P1: Relatório técnico completo ⭐ MVP — o entregável central

**User Story**: Como avaliador do Tech Challenge, quero um **relatório técnico** único e completo que
descreva a arquitetura, os modelos, a lógica de fusão, os resultados e o tratamento de privacidade, para
**entender e pontuar** a solução sem precisar ler o código — Tarefa 4.2.

**Why P1**: É um dos 3 entregáveis avaliados e o documento que **consolida o valor** de todas as fases.
Sem ele, o trabalho técnico não fica legível para a banca.

**Acceptance Criteria**:

1. WHEN o relatório é aberto THEN ele SHALL conter as **6 seções** do PDF/[docs/04](../../../docs/04-fase4-entregaveis.md)
   §4.2: (1) **fluxo multimodal** com diagrama de arquitetura; (2) **modelos por modalidade**
   (cicatriz/fisioterapia em vídeo, sinais vitais, áudio, texto) com **justificativa das escolhas**
   (por que YOLOv8/YOLOv8-pose, por que Random Forest/Isolation Forest); (3) **lógica de fusão** (motor de
   regras) **e a métrica do ganho da fusão**; (4) **resultados e exemplos de anomalias** (métricas, matriz
   de confusão, mAP); (5) **privacidade e segurança (LGPD)**; (6) **exemplo de relatório automático**.
2. WHEN a seção de fusão é lida THEN ela SHALL explicar as **regras explícitas** (matriz base do
   [contrato §4](../../../docs/contrato-api.md) + regras de elevação) e apresentar a **tabela comparativa**
   fusão × modalidade única (precisão, recall, **taxa de FP**) a partir de
   `ai-service/models/metricas_fusao.json` (números reais, não inventados).
3. WHEN a seção de resultados é lida THEN ela SHALL usar as **métricas reais** já geradas
   (`models/sinais_vitais/metrics.json` + `matriz_confusao.png`, `models/cicatriz/metrics.json` com mAP,
   `models/baseline.json`) e **documentar honestamente as limitações** (cicatriz em smoke;
   áudio/fisioterapia dependem de dados manuais — DD10).
4. WHEN a seção de privacidade é lida THEN ela SHALL cobrir os princípios e controles de
   [docs/07](../../../docs/07-privacidade-e-seguranca.md) (minimização, pseudonimização, TLS, segredos fora
   do Git, dados sintéticos) e incluir o **disclaimer ético**.
5. WHEN as afirmações técnicas são feitas THEN elas SHALL ser **rastreáveis** aos artefatos/docs do repo
   (links para `docs/`, `.specs/`, arquivos de métrica) — sem números fabricados (princípio do `AGENTS.md`).

**Independent Test**: Abrir `docs/relatorio-tecnico.md` e conferir que as 6 seções existem, que a tabela de
ganho da fusão bate com `metricas_fusao.json` e que cada métrica citada aponta para o artefato de origem.

---

### P1: Repositório Git finalizado e auditado ⭐ MVP

**User Story**: Como avaliador, quero **clonar o repositório e rodar a solução seguindo só o README**, com
estrutura clara, dependências fixadas e disclaimer visível, para confiar no padrão de engenharia — Tarefa 4.1.

**Why P1**: É um dos 3 entregáveis avaliados; "rodar do zero seguindo só o README" é item do
[checklist](../../../docs/05-checklist-entrega.md).

**Acceptance Criteria**:

1. WHEN o repositório é inspecionado THEN ele SHALL ter a **estrutura em pastas** (`/ai-service`, `/backend`,
   `/docs`, `/scripts`), `ai-service/requirements.txt` e `backend/package.json` com **versões fixadas**, e
   `.gitignore` cobrindo `data/`, `.env` e pesos grandes.
2. WHEN o `README.md` é seguido do zero THEN ele SHALL permitir subir a stack (`docker compose up` **ou**
   execução local) e rodar a demo E2E, sem passos faltando; o **disclaimer ético** SHALL estar visível.
3. WHEN um item do [checklist 4.1/qualidade](../../../docs/05-checklist-entrega.md) está pendente ou
   inconsistente THEN ele SHALL ser corrigido ou explicitamente justificado (ex.: pesos via métricas, não LFS).
4. WHEN o repositório é entregue THEN ele SHALL conter **créditos/integrantes** e o **espaço para o link do
   vídeo** no `README.md`.

**Independent Test**: Em um clone limpo, seguir o README do zero e chegar ao alerta da demo; rodar o
checklist 4.1 e confirmar todos os itens marcados ou justificados.

---

### P1: Evidências consolidadas (métricas, anomalias, relatório de exemplo)

**User Story**: Como autor do relatório e do vídeo, quero as **evidências reunidas em um só lugar**
(métricas, matriz de confusão, mAP, exemplo de relatório automático e prints/logs do E2E), para
referenciá-las no relatório e mostrá-las no vídeo — base das Tarefas 4.2 e 4.3.

**Why P1**: O relatório e o vídeo dependem de evidências concretas; consolidá-las evita retrabalho e
garante que os números citados são os reais.

**Acceptance Criteria**:

1. WHEN as evidências são consolidadas THEN elas SHALL **reaproveitar os artefatos existentes**
   (`models/metricas_fusao.json`, `models/sinais_vitais/*`, `models/cicatriz/metrics.json`,
   `models/baseline.json`) — sem regerar treino (Fase 2).
2. WHEN um **exemplo de relatório automático** é necessário THEN ele SHALL ser gerado a partir de um caso de
   `data/casos/*.json` via `ai-service/app/relatorio.py` e salvo como artefato versionável (Markdown/HTML)
   sob `docs/` para citação no relatório técnico.
3. WHEN o **fluxo ponta-a-ponta** precisa de evidência THEN o `scripts/e2e_demo.py` SHALL ser executado e
   seu **log com `case_id`** capturado (print/trecho) para o relatório/vídeo.

**Independent Test**: Conferir que existe um exemplo de relatório automático versionado e que a tabela de
métricas do relatório técnico cita exatamente os valores dos arquivos de origem.

---

### P1: Roteiro de vídeo de demonstração

**User Story**: Como apresentador, quero um **roteiro detalhado** que diga exatamente o que falar e mostrar
em cada minuto (e quais comandos rodar), para gravar o vídeo de ≤15 min sem improviso — Tarefa 4.3.

**Why P1**: O vídeo é um dos 3 entregáveis; um roteiro pronto é o que o agente **pode** produzir (a gravação
é humana) e o que viabiliza uma demo fluida.

**Acceptance Criteria**:

1. WHEN o roteiro é seguido THEN ele SHALL cobrir os **8 pontos** do roteiro sugerido em
   [docs/04 §4.3](../../../docs/04-fase4-entregaveis.md): problema+arquitetura, vídeo/YOLO (cicatriz+pose),
   sinais vitais, áudio+texto, **o momento da fusão** (alerta vermelho), relatório automático, integração
   Azure e o alerta chegando ao cliente.
2. WHEN cada bloco é descrito THEN ele SHALL indicar **o que mostrar na tela**, **o comando a rodar**
   (ex.: `docker compose up`, `scripts/e2e_demo.py`, `POST /analisar` do `caso_alto`) e **a evidência** a
   exibir, com uma **estimativa de duração** que some ≤15 min.
3. WHEN o ambiente não tiver pesos do YOLO/ASR THEN o roteiro SHALL indicar o **caminho de demonstração**
   válido (degradação documentada; fusão decide com vitais+texto), sem prometer o que o ambiente não faz.
4. WHEN o vídeo for publicado THEN o roteiro SHALL instruir a publicar como **"Não listado"** e **inserir o
   link no `README.md`**.

**Independent Test**: Ler o roteiro e conseguir executar a sequência de comandos descrita, obtendo na tela
o alerta da fusão e o relatório — dentro do tempo estimado.

---

### P2: Exportação do relatório técnico para PDF

**User Story**: Como responsável pela entrega, quero **exportar o relatório para PDF** a partir do Markdown,
para anexar uma versão final fechada — Tarefa 4.2.

**Why P2**: O PDF é o formato de entrega usual, mas o Markdown/HTML já satisfaz a avaliação; a conversão é
melhor-esforço (mesma política do relatório automático da Fase 3, DD7).

**Acceptance Criteria**:

1. WHEN o script/instrução de exportação roda THEN ele SHALL converter `docs/relatorio-tecnico.md` em PDF
   (reusando a abordagem de `ai-service/app/relatorio.py`: `markdown` → HTML → `weasyprint`, ou `pandoc`).
2. WHEN as libs de conversão **não** estão disponíveis THEN o processo SHALL **degradar para HTML/Markdown**
   sem quebrar, deixando claro como gerar o PDF localmente.

**Independent Test**: Rodar a exportação e obter o PDF (ou, sem libs, o HTML + instrução), a partir do mesmo
Markdown versionado.

---

### P2: Diagrama de arquitetura e fluxo multimodal

**User Story**: Como leitor do relatório e espectador do vídeo, quero um **diagrama** claro do fluxo
multimodal (upload → storage → IA → fusão → alerta/relatório), para entender a solução de relance — apoio
às Tarefas 4.2 e 4.3.

**Why P2**: A seção (1) do relatório e o ponto (1) do vídeo exigem um diagrama; reaproveita os diagramas já
existentes em [docs/arquitetura.md](../../../docs/arquitetura.md) e [docs/casos-de-uso.md](../../../docs/casos-de-uso.md).

**Acceptance Criteria**:

1. WHEN o diagrama é produzido THEN ele SHALL representar os dois serviços (Node orquestrador + Python/IA),
   o storage (Azure/local), a fusão e o alerta em tempo real, coerente com [docs/arquitetura.md](../../../docs/arquitetura.md).
2. WHEN a skill `mermaid-studio` estiver instalada THEN o diagrama SHALL ser renderizado por ela
   (SVG/PNG); caso contrário, SHALL usar **bloco Mermaid inline** e recomendar a skill uma vez.

**Independent Test**: O relatório técnico exibe o diagrama (imagem renderizada ou bloco Mermaid válido)
condizente com a arquitetura descrita.

---

### P3: Checklist final + verificação do gate de qualidade

**User Story**: Como responsável pela submissão, quero **percorrer o checklist de entrega** e confirmar o
**gate verde** (lint + testes) num clone limpo, para garantir que nada avaliado ficou de fora — antes de submeter.

**Why P3**: É a verificação final de fechamento; depende de todos os outros entregáveis estarem prontos.

**Acceptance Criteria**:

1. WHEN o checklist de [docs/05](../../../docs/05-checklist-entrega.md) é percorrido THEN cada item SHALL
   estar **marcado** ou ter justificativa registrada (ex.: deploy Azure via fallback local).
2. WHEN o gate roda THEN `ruff check scripts ai-service` + `pytest -q` (Python) e `npm run lint`/`npm test`
   (Node) SHALL passar, e o resultado SHALL ser citado no relatório/STATE.
3. WHEN a Fase 4 fecha THEN o `STATE.md` e o `docs/04-fase4-entregaveis.md` SHALL ser atualizados (itens do
   DoD marcados; decisões registradas).

**Independent Test**: Rodar o gate num clone limpo e obter verde; conferir o checklist totalmente preenchido.

---

## Edge Cases

- WHEN as libs de **conversão para PDF** (weasyprint/pandoc) faltam no ambiente THEN a exportação SHALL
  degradar para HTML/Markdown e o relatório SHALL permanecer entregável (mesmo princípio do DD7 da Fase 3).
- WHEN os **pesos do YOLO/ASR** não existem no ambiente THEN o relatório e o roteiro SHALL **documentar a
  degradação** (evidência omitida; a fusão decide com vitais+texto) em vez de afirmar detecções inexistentes.
- WHEN a skill **`mermaid-studio` não está instalada** THEN os diagramas SHALL ficar como **Mermaid inline**
  e a recomendação de instalação SHALL aparecer no máximo uma vez.
- WHEN o **vídeo ainda não foi gravado/publicado** (ação humana) THEN o `README.md` SHALL conter um
  **placeholder de link** claramente marcado, sem quebrar a entrega dos demais artefatos.
- WHEN um número/metrica **não tem artefato de origem** no repo THEN ele **NÃO** SHALL ser citado no
  relatório (princípio "nunca inventar" do `AGENTS.md`); a lacuna SHALL ser sinalizada.
- WHEN o **deploy real na Azure** não está disponível THEN o relatório SHALL descrever a integração e o
  **fallback local**, referenciando [docs/deploy-azure.md](../../../docs/deploy-azure.md).

---

## Requirement Traceability

| Requirement ID | Story                                                       | Phase | Status  |
| -------------- | ----------------------------------------------------------- | ----- | ------- |
| F4E-01         | P1: Repositório Git finalizado e auditado (4.1)             | Done  | Verified |
| F4E-02         | P1: Evidências consolidadas (métricas/anomalias/exemplo)    | Done  | Verified |
| F4E-03         | P2: Diagrama de arquitetura / fluxo multimodal              | Done  | Verified |
| F4E-04         | P1: Relatório — fluxo multimodal + diagrama                 | Done  | Verified |
| F4E-05         | P1: Relatório — modelos por modalidade + justificativas     | Done  | Verified |
| F4E-06         | P1: Relatório — lógica de fusão + métrica do ganho          | Done  | Verified |
| F4E-07         | P1: Relatório — resultados e exemplos de anomalias          | Done  | Verified |
| F4E-08         | P1: Relatório — privacidade e segurança (LGPD)              | Done  | Verified |
| F4E-09         | P1: Relatório — exemplo de relatório automático             | Done  | Verified |
| F4E-10         | P2: Exportação do relatório para PDF (com fallback)         | Done  | Verified |
| F4E-11         | P1: Roteiro de vídeo (8 pontos) + instruções de publicação  | Done  | Verified |
| F4E-12         | P1: Link do vídeo + créditos/integrantes no README          | Done  | Verified |
| F4E-13         | P3: Checklist final + gate de qualidade verde               | Done  | Verified |
| F4E-14         | P3: STATE + docs/04 atualizados (fechamento da fase)        | Done  | Verified |

**ID format:** `F4E-[NUMBER]` (Fase 4 Entregáveis).
**Status values:** Pending → In Design → In Tasks → Implementing → Verified.
**Coverage:** 14 requisitos, todos mapeados para tarefas (T1–T9) e **verificados** (implementação concluída;
vídeo entregue como roteiro + placeholder de link — ação humana).

---

## Success Criteria

Como saberemos que a Fase 4 está pronta. Espelha a **Definition of Done** de
[docs/04](../../../docs/04-fase4-entregaveis.md) e o [checklist de entrega](../../../docs/05-checklist-entrega.md).

Itens obrigatórios para o gate:

- [ ] **Repositório** organizado, com `README.md` (execução do zero), `requirements.txt`/`package.json`
      (versões fixadas), `.gitignore` adequado e **disclaimer ético** visível.
- [ ] **Relatório técnico** (`docs/relatorio-tecnico.md`) com as **6 seções** do PDF, usando **métricas
      reais** rastreáveis aos artefatos do repo (incl. a **tabela do ganho da fusão**).
- [ ] **Evidências consolidadas** (métricas, matriz de confusão, mAP, exemplo de relatório automático,
      log do E2E com `case_id`) referenciadas pelo relatório.
- [ ] **Roteiro de vídeo** (`docs/roteiro-video.md`) cobrindo os 8 pontos, com comandos e durações ≤15 min.
- [ ] **Checklist de entrega** percorrido (marcado/justificado) e **gate verde** num clone limpo
      (`ruff`+`pytest`; `eslint`+`jest`).
- [ ] **STATE** e **docs/04** atualizados (fase fechada, decisões registradas).

Itens do DoD que dependem de **ação humana** (não bloqueiam o planejamento/empacotamento do agente):

- [ ] **Vídeo gravado e publicado** (YouTube/Vimeo "Não listado") — o agente entrega o **roteiro** e o
      **placeholder de link**; a gravação/publicação é do grupo.
- [ ] **Exportação final em PDF** — entregue se as libs estiverem disponíveis; senão, Markdown/HTML +
      instrução de geração local (fallback).
