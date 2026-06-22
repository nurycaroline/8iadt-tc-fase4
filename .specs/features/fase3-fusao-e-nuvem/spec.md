# Fase 3 — Fusão Multimodal e Integração em Nuvem — Especificação

> Documento de planejamento gerado a partir de [`docs/03-fase3-fusao-e-nuvem.md`](../../../docs/03-fase3-fusao-e-nuvem.md).
> Fontes de escopo: [`docs/contrato-api.md`](../../../docs/contrato-api.md),
> [`docs/arquitetura.md`](../../../docs/arquitetura.md),
> [`docs/06-relatorios-automaticos.md`](../../../docs/06-relatorios-automaticos.md),
> [`docs/qualidade-testes-ci.md`](../../../docs/qualidade-testes-ci.md),
> [`docs/07-privacidade-e-seguranca.md`](../../../docs/07-privacidade-e-seguranca.md) e
> [`docs/frontend.md`](../../../docs/frontend.md).
> Insumos prontos: serviço de IA da [Fase 2](../fase2-modelos/) (um módulo por modalidade, cada um com
> **saída padronizada** do contrato §3) e o **caso de exemplo sintético** da [Fase 1](../fase1-dados/)
> em `data/casos/*.json`.

## Problem Statement

A [Fase 2](../fase2-modelos/) entregou **4 modalidades** funcionando isoladamente (cicatriz/vídeo,
sinais vitais, áudio, texto — e fisioterapia/pose), cada uma expondo uma função de inferência que
devolve um **dicionário de evidência** alinhado ao [contrato de API §3](../../../docs/contrato-api.md),
mais um **baseline por modalidade única** (`ai-service/models/baseline.json`). O que **ainda não existe**
é o **diferencial avaliado** do desafio: um **motor de fusão** que cruza as evidências da **mesma
paciente** e produz **um** nível de risco explicável (`BAIXO/MEDIO/ALTO`), exposto como **serviço na
nuvem**, com **alerta em tempo real** para a equipe e **relatório clínico automático** por caso.

Sem a Fase 3 não há: (1) prova de que a multimodalidade vale mais que uma modalidade só (métrica do
ganho da fusão), (2) pipeline ponta-a-ponta (upload → Blob → inferência → JSON → alerta + relatório),
nem (3) o produto rodando como serviço (FastAPI + Node + Azure). Esta fase é o **núcleo de valor** do
projeto e o **caminho crítico** (M10 → M11 → M12 do [cronograma](../../../docs/cronograma-dependencias.md)).

## Goals

- [ ] **Motor de fusão** (Python, regras clínicas) que cruza as evidências da mesma paciente e retorna o
      **JSON de risco padronizado** do [contrato §2](../../../docs/contrato-api.md), com `risco_detectado`,
      `evidencias`, `mensagem_alerta` e `relatorio_url`.
- [ ] **Métrica do ganho da fusão** vs. modalidade única (precisão, recall e **taxa de falsos
      positivos**), comparando fusão × só-vídeo × só-vitais × só-áudio/texto sobre os casos de exemplo.
- [ ] **Pipeline de inferência** (Python) que orquestra as modalidades a partir do objeto de requisição
      ([contrato §1](../../../docs/contrato-api.md)) → evidências → fusão → resposta, degradando quando
      uma modalidade está ausente.
- [ ] **Serviço de IA (FastAPI)** com `POST /inferencia` recebendo o payload do contrato e devolvendo o
      JSON de risco; `uvicorn` para servir; `/health` para readiness.
- [ ] **Backend orquestrador (Node.js/Express)**: `POST /analisar` (upload → Azure Blob → chama o
      serviço Python → grava no banco → dispara alerta) e gestão de pacientes
      (`POST /pacientes`, `GET /pacientes`, `DELETE /pacientes/{id}`).
- [ ] **Alerta em tempo real** (WebSocket/SSE) empurrando o alerta ao cliente assim que a fusão
      classificar risco `MEDIO`/`ALTO`.
- [ ] **Relatório automático** clínico por caso (Markdown → HTML/PDF), salvo no armazenamento e
      referenciado em `relatorio_url` (template de [docs/06](../../../docs/06-relatorios-automaticos.md)).
- [ ] **Infraestrutura Azure**: Blob Storage para artefatos + deploy do serviço (App Service / Functions
      / Container), com **fallback local** funcional para a demo.
- [ ] **Reprodutibilidade**: `Dockerfile` (ai-service e backend) + `docker-compose.yml` na raiz +
      `.env.example`; **CI** (GitHub Actions) rodando lint + testes dos dois serviços.
- [ ] **Teste ponta-a-ponta** com o caso de exemplo: upload → Blob → inferência → JSON → alerta no
      cliente/log, com evidências (logs/prints) para o relatório e o vídeo.
- [ ] **Observabilidade**: logging estruturado com `case_id` rastreável ponta-a-ponta nos dois serviços.

## Out of Scope

Explicitamente excluído para evitar scope creep. Cada item pertence a outra fase/feature.

| Item                                                              | Motivo / Onde entra                                   |
| ----------------------------------------------------------------- | ----------------------------------------------------- |
| Treino/ajuste dos modelos individuais                             | Fase 2 (concluída) — esta fase **consome** as inferências |
| Aquisição/preparação de dados (download/limpeza/conversão)        | Fase 1 (concluída)                                     |
| **Dashboard React completo** (todas as telas de `docs/frontend.md`) | Feature de front-end própria; aqui só um **cliente mínimo** para demonstrar o alerta em tempo real |
| Autenticação/login e permissionamento                             | Fora do escopo do projeto (ver `docs/frontend.md` §2) |
| Escalar treino do YOLO (mais dados/épocas, GPU/Colab)             | Após o pipeline rodar ponta-a-ponta (item de STATE)   |
| Relatório técnico final + vídeo de demonstração                   | Fase 4 (esta fase **gera as evidências** para eles)   |
| Dados reais de pacientes                                          | LGPD — só dados públicos/sintéticos (ver `docs/07`)   |
| Banco de dados gerenciado em produção (Postgres/CosmosDB)         | Deploy avançado opcional; o MVP usa SQLite local + fallback |

---

## User Stories

### P1: Motor de fusão clínica (regras) ⭐ MVP — o diferencial

**User Story**: Como responsável pela inteligência clínica, quero uma função Python que **cruze as
evidências** das modalidades da **mesma paciente** e classifique o risco em `BAIXO/MEDIO/ALTO` com uma
**mensagem de alerta explicável**, para que o sistema avise a equipe com base em **regras de negócio
explícitas** (a IA não decide sozinha) — Tarefa 3.1.

**Why P1**: É o núcleo de valor do desafio e o caminho crítico. Sem a fusão não há JSON de risco,
alerta nem relatório.

**Acceptance Criteria**:

1. WHEN as evidências de cicatriz e sinais vitais são combinadas THEN o motor SHALL aplicar a **matriz
   base** do [contrato §4](../../../docs/contrato-api.md): infecção+risco → `ALTO`; infecção+normal →
   `MEDIO`; ok/nenhum+risco → `MEDIO`; ok/nenhum+normal → `BAIXO`.
2. WHEN há **cicatriz com sinal de infecção E** (sinais vitais de risco **ou** febre/dor no áudio/texto)
   THEN o risco SHALL ser `ALTO` com mensagem de **infecção puerperal** (Tarefa 3.1).
3. WHEN há **sinais vitais de risco E** áudio/texto com cefaleia/proteinúria THEN o risco SHALL ser
   `ALTO` com mensagem de **pré-eclâmpsia** (Tarefa 3.1).
4. WHEN o áudio indica **violência** THEN o risco SHALL ser `ALTO` com **protocolo de proteção**;
   WHEN o áudio indica **depressão pós-parto/ansiedade** persistente THEN o risco SHALL ser ao menos
   `MEDIO` com **encaminhamento psicológico**.
5. WHEN o **texto/NLP** confirma um achado (ex.: laudo com proteinúria/febre) THEN ele SHALL entrar como
   **contexto adicional** que pode **elevar a prioridade**, sem ser a única fonte do risco máximo.
6. WHEN uma modalidade está ausente THEN o motor SHALL avaliar com as evidências disponíveis sem quebrar.
7. WHEN o motor decide THEN a saída SHALL conter **quais gatilhos foram acionados** (rastreabilidade
   para o relatório) e SHALL ser **determinística e testável**.

**Independent Test**: Chamar `avaliar_fusao` com combinações conhecidas de evidências e conferir
`risco_detectado`, `mensagem_alerta` e os gatilhos — incluindo o caso "vermelhidão leve sem febre/PA"
que **não** dispara vermelho.

---

### P1: Pipeline de inferência multimodal (contrato §1 → §2) ⭐ MVP

**User Story**: Como integrador, quero uma função/serviço que receba o **objeto de requisição** do
contrato (URLs/dados das modalidades de um caso), rode as inferências da Fase 2, monte as **evidências**
e chame o motor de fusão, devolvendo o **JSON de risco padronizado** do contrato — para que Node e
FastAPI tenham uma única porta de entrada da IA.

**Why P1**: É a cola entre as modalidades (Fase 2) e a fusão; o `POST /inferencia` é um wrapper fino sobre ela.

**Acceptance Criteria**:

1. WHEN recebe um payload do [contrato §1](../../../docs/contrato-api.md) THEN o pipeline SHALL invocar a
   inferência de cada modalidade **presente** (cicatriz, fisioterapia, sinais vitais, áudio, texto)
   reaproveitando as funções da Fase 2 (`detectar`, `avaliar`, `prever`, `audio...inferir`, `analisar`).
2. WHEN uma modalidade não está no payload ou seus pesos/dados faltam THEN o pipeline SHALL **omitir** a
   evidência (campo opcional do contrato) e registrar a omissão, sem derrubar o caso.
3. WHEN as evidências estão montadas THEN o pipeline SHALL chamar `avaliar_fusao` e devolver o objeto do
   [contrato §2](../../../docs/contrato-api.md) (`timestamp`, `case_id`, `risco_detectado`, `evidencias`,
   `mensagem_alerta`, `relatorio_url`).
4. WHEN um caso de exemplo de `data/casos/*.json` é processado THEN o pipeline SHALL produzir um risco
   coerente com o nível indicado no nome do caso (`caso_alto`/`caso_medio`/`caso_baixo`).

**Independent Test**: Rodar o pipeline sobre `data/casos/caso_alto.json` e conferir o JSON de resposta
válido (valida contra os domínios do contrato) com `risco_detectado = ALTO`.

---

### P1: Serviço de IA (FastAPI) com `POST /inferencia` ⭐ MVP

**User Story**: Como backend Node, quero um endpoint HTTP `POST /inferencia` no serviço Python que
receba o payload do contrato e devolva o JSON de risco, para chamar a IA por rede — Tarefa 3.2.

**Why P1**: Materializa o "serviço de IA na nuvem"; é a fronteira Node ↔ Python da arquitetura.

**Acceptance Criteria**:

1. WHEN o serviço sobe (`uvicorn`) THEN ele SHALL expor `POST /inferencia` e `GET /health`.
2. WHEN `POST /inferencia` recebe um corpo válido do contrato §1 THEN ele SHALL validá-lo (modelos
   Pydantic) e responder `200` com o JSON de risco do contrato §2.
3. WHEN o corpo é inválido THEN o serviço SHALL responder `422` com mensagem clara (validação Pydantic).
4. WHEN uma modalidade falha internamente THEN o serviço SHALL degradar a evidência e ainda responder o
   risco com base no que foi possível avaliar (sem `500` por modalidade ausente).

**Independent Test**: Subir o serviço, `POST /inferencia` com o payload de exemplo e conferir o status
`200` e o corpo do contrato §2; `GET /health` retorna `200`.

---

### P1: Backend orquestrador (Node.js/Express) ⭐ MVP

**User Story**: Como usuário do sistema, quero um backend que receba o **upload** de um caso, armazene
os arquivos, chame o serviço de IA, **grave o resultado** e **dispare o alerta**, além de gerir
pacientes — Tarefa 3.3.

**Why P1**: É o orquestrador da arquitetura (Node como dono do fluxo) e o ponto de entrada do front-end.

**Acceptance Criteria**:

1. WHEN `POST /analisar` recebe upload (vídeo/áudio/CSV/texto) + `paciente_id` THEN o backend SHALL
   enviar os arquivos ao **armazenamento** (Azure Blob; fallback local), montar o payload do contrato §1
   e chamar `POST /inferencia` do serviço Python (`axios`).
2. WHEN o serviço Python responde THEN o backend SHALL **persistir** o `Caso` (resultado + URLs) no banco
   e responder o JSON de risco ao chamador.
3. WHEN gerencia pacientes THEN o backend SHALL expor `POST /pacientes`, `GET /pacientes` e
   `DELETE /pacientes/{id}` conforme o modelo de dados de [arquitetura §7](../../../docs/arquitetura.md)
   (excluir paciente remove em cascata o `Caso` e os artefatos).
4. WHEN há credenciais (`.env`) THEN elas SHALL vir de variáveis de ambiente (`dotenv`), **nunca** do Git.

**Independent Test**: Com o serviço Python mockado (`jest`), enviar `POST /analisar` com um arquivo de
exemplo e conferir que o `Caso` é persistido e a resposta tem o risco; CRUD de pacientes responde.

---

### P1: Alerta em tempo real (WebSocket/SSE)

**User Story**: Como equipe de vigilância, quero **receber o alerta em tempo real** assim que a fusão
classificar um risco `MEDIO`/`ALTO`, para agir cedo — Tarefa 3.3b.

**Why P1**: Requisito explícito do PDF ("alertar a equipe em tempo real") e o "money shot" da demo.

**Acceptance Criteria**:

1. WHEN a fusão classifica `MEDIO`/`ALTO` em `POST /analisar` THEN o backend SHALL **empurrar** o alerta
   (com `case_id`, `risco_detectado`, `mensagem_alerta`, paciente) via **WebSocket** (ou SSE) aos
   clientes conectados.
2. WHEN o risco é `BAIXO` THEN nenhum alerta de risco SHALL ser empurrado (apenas atualização opcional de estado).
3. WHEN um **cliente mínimo de demonstração** conecta THEN ele SHALL exibir o alerta no momento em que a
   fusão fecha o risco (suficiente para gravar a demo).

**Independent Test**: Conectar um cliente WebSocket, disparar um `POST /analisar` de caso alto (Python
mockado) e observar o evento de alerta chegando com os campos esperados.

---

### P1: Relatório clínico automático por caso

**User Story**: Como equipe médica, quero um **relatório clínico estruturado** gerado automaticamente
para cada caso, salvo e referenciado por URL, para documentar a decisão — Tarefa 3.3c / [docs/06](../../../docs/06-relatorios-automaticos.md).

**Why P1**: Entrega técnica obrigatória do PDF ("relatórios automáticos especializados").

**Acceptance Criteria**:

1. WHEN a fusão termina THEN o serviço SHALL gerar `gerar_relatorio(json_fusao, paciente) -> markdown`
   seguindo o **template** de [docs/06](../../../docs/06-relatorios-automaticos.md) §3 (resumo, evidências
   por modalidade, gatilhos, recomendação, anexos, disclaimer).
2. WHEN o relatório é gerado THEN ele SHALL ser convertido para **HTML/PDF**, **salvo** no armazenamento
   (Blob/local) e sua URL SHALL preencher `relatorio_url` no JSON de resposta.
3. WHEN o tipo de risco varia THEN o conteúdo-chave SHALL refletir o gatilho (infecção puerperal /
   pré-eclâmpsia / desconforto psicológico / violência), conforme [docs/06](../../../docs/06-relatorios-automaticos.md) §4.
4. WHEN a conversão para PDF não está disponível no ambiente THEN o sistema SHALL manter o **Markdown/HTML**
   como saída garantida (fallback), sem quebrar o pipeline.

**Independent Test**: Gerar o relatório a partir de um JSON de fusão `ALTO` e conferir que o Markdown
contém as seções do template e os gatilhos acionados; conferir que o arquivo é salvo e a URL retorna.

---

### P1: Métrica do ganho da fusão (provar a multimodalidade) ⭐ diferencial avaliado

**User Story**: Como responsável pelas métricas, quero **comparar a fusão vs. cada modalidade isolada**
sobre os casos de exemplo, reportando precisão, recall e **taxa de falsos positivos**, para **provar que
a fusão agrega valor** — Tarefa 3.1b.

**Why P1**: O PDF e [docs/00](../../../docs/00-visao-geral-e-escopo.md) (D8) destacam isso como o
diferencial avaliado; não basta a fusão funcionar, é preciso mostrá-la melhor.

**Acceptance Criteria**:

1. WHEN a comparação roda THEN ela SHALL avaliar os cenários **só-vídeo**, **só-vitais**,
   **só-áudio/texto** e **fusão** sobre os casos de exemplo/mini-dataset, reusando
   `app.baseline.metricas_modalidade`.
2. WHEN termina THEN ela SHALL produzir uma **tabela comparativa** (precisão, recall, taxa de falsos
   positivos por cenário) salva como artefato (`models/metricas_fusao.json`).
3. WHEN comparada ao baseline THEN a conclusão esperada SHALL evidenciar **redução de falsos positivos**
   e/ou **aumento de recall** dos casos críticos (documentado no relatório técnico).

**Independent Test**: Rodar a comparação e conferir o `metricas_fusao.json` com as 4 linhas (3 modalidades
isoladas + fusão) e as três métricas em cada.

---

### P2: Infraestrutura Azure (Blob + deploy) com fallback local

**User Story**: Como time de operação, quero o serviço rodando na **Azure** (Blob Storage para artefatos
+ hospedagem do serviço Python), com **fallback local** funcional, para atender ao requisito de nuvem
sem travar a demo — Tarefa 3.4.

**Why P2**: Requisito de nuvem do desafio, mas com risco de conta/limite; o fallback local garante a demo.

**Acceptance Criteria**:

1. WHEN há credenciais Azure (`.env`/Key Vault) THEN o armazenamento SHALL usar **Azure Blob Storage**
   (container para vídeos/imagens/relatórios) com SAS/expiração.
2. WHEN não há credenciais THEN o sistema SHALL usar um **adaptador de armazenamento local** equivalente
   (mesma interface), mantendo o pipeline funcional.
3. WHEN documentado THEN o repo SHALL conter os **passos de deploy** (App Service / Functions / Container
   Instances) e as variáveis de ambiente necessárias.
4. WHEN dados sensíveis trafegam THEN os controles de [docs/07](../../../docs/07-privacidade-e-seguranca.md)
   SHALL ser respeitados (TLS, segredos fora do Git, sem dados reais).

**Independent Test**: Rodar o pipeline com o adaptador local (sem credenciais) e confirmar upload/leitura
e gravação do relatório; com credenciais de teste, confirmar a escrita no Blob.

---

### P2: Reprodutibilidade (Docker + CI) e teste ponta-a-ponta

**User Story**: Como avaliador, quero subir toda a stack com **um comando** e ver o **pipeline rodando
ponta-a-ponta** com o caso de exemplo, além de **CI verde**, para confiar na qualidade de engenharia —
Tarefa 3.5 + [docs/qualidade-testes-ci](../../../docs/qualidade-testes-ci.md).

**Why P2**: Pontua em engenharia de software e viabiliza a demo/avaliação reproduzível.

**Acceptance Criteria**:

1. WHEN `docker compose up` roda THEN ele SHALL subir **ai-service** (FastAPI) e **backend** (Node) com
   `.env`/`.env.example` e dependência (`depends_on`).
2. WHEN o **teste ponta-a-ponta** roda com o caso de exemplo THEN ele SHALL exercer upload → armazenamento
   → inferência → JSON → alerta (no log/cliente) e **capturar evidências** (logs/prints).
3. WHEN há push/PR THEN o **CI** (GitHub Actions) SHALL rodar `ruff`+`pytest` (Python) e lint+`jest` (Node).
4. WHEN um caso atravessa a stack THEN o **`case_id`** SHALL aparecer nos logs estruturados dos dois
   serviços (rastreabilidade).

**Independent Test**: `docker compose up` sobe os dois serviços; o script/teste E2E processa um caso e
mostra o alerta; o workflow de CI passa localmente (`act` ou execução manual das etapas).

---

### P3: Cliente mínimo de demonstração do alerta

**User Story**: Como apresentador, quero um **cliente mínimo** (página/script) que conecte ao WebSocket e
**mostre o alerta surgindo** quando a fusão fecha o risco, para gravar a cena principal do vídeo — sem
construir o dashboard React completo (feature própria).

**Why P3**: Suficiente para demonstrar a Tarefa 3.3b; o dashboard rico é uma feature de front-end separada.

**Acceptance Criteria**:

1. WHEN o cliente conecta THEN ele SHALL receber e exibir o alerta (paciente, risco, mensagem) em tempo real.
2. WHEN o risco é `ALTO` THEN o cliente SHALL destacar visualmente (banner/cor) o alerta.
3. WHEN o dashboard React completo for construído THEN ele SHALL reusar o **mesmo evento/contrato** deste cliente.

**Independent Test**: Abrir o cliente, disparar um caso alto e ver o alerta destacado em tempo real.

---

## Edge Cases

- WHEN o payload chega **sem nenhuma modalidade** válida THEN o pipeline SHALL retornar `BAIXO` com
  mensagem clara de "sem evidências suficientes", sem quebrar.
- WHEN os **pesos de um modelo não existem** (ex.: cicatriz não escalada) THEN a evidência SHALL degradar
  para o valor neutro (`nenhum`/`nao_avaliado`) sem derrubar a fusão (herdado da Fase 2, DD10).
- WHEN o **serviço Python está indisponível** THEN o backend Node SHALL responder erro claro (`502/504`)
  e registrar o `case_id`, sem perder o upload já armazenado.
- WHEN a **conta Azure** está indisponível/sem credencial THEN o sistema SHALL cair no **fallback local**
  automaticamente (mesma interface de storage).
- WHEN a **conversão para PDF** falha (dependência de sistema ausente) THEN o relatório SHALL ficar em
  Markdown/HTML e o `relatorio_url` SHALL apontar para esse arquivo.
- WHEN duas evidências sugerem riscos diferentes (ex.: violência no áudio **e** infecção na cicatriz)
  THEN a fusão SHALL escolher o **maior** nível de risco e **listar ambos** os gatilhos na mensagem.
- WHEN o `texto/NLP` é a **única** fonte de risco THEN ele SHALL elevar no máximo para `MEDIO` (contexto),
  pois o contrato §4 trata texto/áudio como contexto adicional.

---

## Requirement Traceability

| Requirement ID | Story                                            | Phase | Status  |
| -------------- | ------------------------------------------------ | ----- | ------- |
| F3F-01         | P1: Motor de fusão (matriz base + regras)        | Tasks | Pending |
| F3F-02         | P1: Motor de fusão (mensagem + gatilhos)         | Tasks | Pending |
| F3F-03         | P1: Pipeline de inferência (contrato §1 → §2)    | Tasks | Pending |
| F3F-04         | P1: FastAPI `POST /inferencia` + `/health`       | Tasks | Pending |
| F3F-05         | P1: Backend Node `POST /analisar` + Blob         | Tasks | Pending |
| F3F-06         | P1: Backend Node gestão de pacientes (CRUD)      | Tasks | Pending |
| F3F-07         | P1: Persistência do `Caso` + modelo de dados     | Tasks | Pending |
| F3F-08         | P1: Alerta em tempo real (WebSocket/SSE)         | Tasks | Pending |
| F3F-09         | P1: Relatório automático (Markdown→HTML/PDF)     | Tasks | Pending |
| F3F-10         | P1: Métrica do ganho da fusão (3.1b)             | Tasks | Pending |
| F3F-11         | P2: Storage Azure Blob + fallback local          | Tasks | Pending |
| F3F-12         | P2: Docker + docker-compose + .env.example       | Tasks | Pending |
| F3F-13         | P2: CI (GitHub Actions) Python + Node            | Tasks | Pending |
| F3F-14         | P2: Teste ponta-a-ponta + observabilidade        | Tasks | Pending |
| F3F-15         | P2: Deploy Azure (docs + scripts) + fallback     | Tasks | Pending |
| F3F-16         | P3: Cliente mínimo de demonstração do alerta     | Tasks | Pending |
| F3F-17         | P1: Documentação (READMEs + STATE + cross-refs)  | Tasks | Pending |

**ID format:** `F3F-[NUMBER]` (Fase 3 Fusão).
**Status values:** Pending → In Design → In Tasks → Implementing → Verified.
**Coverage:** 17 requisitos, todos mapeados para tarefas em `tasks.md`.

---

## Success Criteria

Como saberemos que a Fase 3 está pronta. O **gate de fim de fase** do
[cronograma](../../../docs/cronograma-dependencias.md) §4 exige **pipeline ponta-a-ponta + métricas da
fusão**, e o DoD de [docs/03](../../../docs/03-fase3-fusao-e-nuvem.md) lista os itens abaixo.

Itens obrigatórios para o gate:

- [ ] **Motor de fusão** retornando o **JSON de risco padronizado** (contrato §2), com regras explícitas
      e gatilhos rastreáveis — testado em unidade (núcleo do valor).
- [ ] **Métrica do ganho da fusão** vs. modalidade única salva (`metricas_fusao.json`) e documentada.
- [ ] **FastAPI** servindo `POST /inferencia` (+ `/health`) com validação Pydantic do contrato.
- [ ] **Backend Node** com `POST /analisar` (upload → Blob → Python → banco → alerta) e CRUD de pacientes.
- [ ] **Alerta em tempo real** (WebSocket/SSE) chegando a um cliente quando o risco é `MEDIO`/`ALTO`.
- [ ] **Relatório automático** gerado por caso (Markdown→HTML/PDF), salvo e referenciado em `relatorio_url`.
- [ ] **Pipeline ponta-a-ponta** rodando com o caso de exemplo (upload → IA → JSON → alerta) — local e/ou Azure.
- [ ] **Reprodutibilidade**: `docker compose up` sobe a stack; **CI verde**; logging com `case_id` nos dois serviços.
- [ ] Saídas **compatíveis com o [contrato de API](../../../docs/contrato-api.md)** (validadas).
- [ ] Gate verde: `ruff check scripts ai-service` + `pytest -q` (Python) e lint + `jest` (Node).

Itens do DoD que podem usar **fallback** (não bloqueiam o gate se o fallback funcionar):

- [ ] **Deploy real na Azure** (App Service/Functions/Container) — exige conta/credenciais; o **fallback
      local** funcional satisfaz a demonstração se a Azure estiver indisponível (ver `docs/03` §3.4).
- [ ] **Dashboard React completo** — fora do escopo; um **cliente mínimo** demonstra o alerta.
