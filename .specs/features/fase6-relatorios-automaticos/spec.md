# Fase 6 — Relatórios Automáticos Especializados — Especificação

> **Status: RASCUNHO / planejamento.** Documento gerado a partir do requisito
> [`docs/06-relatorios-automaticos.md`](../../../docs/06-relatorios-automaticos.md) (componente próprio
> citado no PDF do Tech Challenge), comparado ao que **já está implementado** em
> [`ai-service/app/relatorio.py`](../../../ai-service/app/relatorio.py), seguindo a skill
> [`tlc-spec-driven`](../../../.cursor/skills/tlc-spec-driven/SKILL.md) (fase **Specify**).
>
> ⚠️ **Decisão de escopo a confirmar (`AGENTS.md` — Princípio 1, em caso de dúvida perguntar):** o
> relatório automático **já existe** desde a Fase 3 (gerado pelo pipeline) e ganhou botão de download no
> dashboard da Fase 5. **Não existia uma "Fase 6" definida** no plano. Esta especificação propõe a Fase 6
> como **"Relatórios Automáticos Especializados"**: pegar o relatório **genérico** atual (um único template,
> recomendação só por nível de risco, anexos sem links reais) e elevá-lo ao que o `docs/06` descreve —
> **conteúdo especializado por tipo de risco** (§1/§4) e **anexos com links reais** (§2/§3/§5). **Todo
> requisito abaixo rastreia uma lacuna real entre o `docs/06` e o código — nenhum foi inventado.** Antes de
> avançar para Design/Tasks, **confirmar com o grupo** a seção [Decisões a confirmar](#decisões-a-confirmar-com-o-grupo).

## Problem Statement

O `docs/06-relatorios-automaticos.md` lista os **relatórios automáticos especializados** como entrega
técnica obrigatória do PDF, com **4 tipos de conteúdo** (desvios obstétricos, complicações do puerpério,
desconforto psicológico, violência doméstica) e um **template estruturado** (§3) cujos anexos devem trazer
**"links Blob: frame, gráfico, áudio"** (§5), salvos **"junto com os frames de alerta"** (§2).

O que **já existe** (Fases 3 e 5) atende a base, mas **fica aquém do `docs/06`** em três pontos concretos:

1. **Relatório genérico, não especializado por tipo.** [`gerar_markdown`](../../../ai-service/app/relatorio.py)
   produz **um único** template e a seção "Recomendação / encaminhamento" usa
   [`RECOMENDACAO[risco]`](../../../ai-service/app/fusao.py) — texto **por nível** (`BAIXO/MÉDIO/ALTO`),
   **não por tipo de risco**. O `docs/06 §1/§4` pede conteúdo-chave e encaminhamento **específicos** (ex.:
   violência → protocolo de proteção; depressão pós-parto → encaminhamento psicológico; infecção puerperal →
   risco de infecção da cesárea). Os gatilhos já são rastreados (`fusao.gatilhos`), mas o relatório não os
   converte em **encaminhamento especializado**.
2. **Anexos sem links reais.** [`_secao_anexos`](../../../ai-service/app/relatorio.py) apenas **lista o nome**
   das modalidades (`video_cicatriz`, `sinais_vitais`, `texto`) — não os **links Blob** dos artefatos
   (frame da cicatriz, gráfico dos sinais vitais, trecho/transcrição do áudio) que o `docs/06 §3/§5` exige.
   As URLs existem no **objeto de requisição** do contrato (`video_cicatriz_url`, `audio_url`, etc.), mas não
   são repassadas ao relatório.
3. **PDF é melhor-esforço (na prática, HTML).** A decisão S16/DD7 mantém **Markdown/HTML sempre**; o PDF
   depende do `weasyprint` + libs de sistema, que **não estão na imagem** — então o `docs/06` ("Markdown →
   PDF") fica cumprido só como HTML. Falta **garantir o PDF no ambiente conteinerizado** mantendo o fallback.

Enquanto isso, o `docs/06` continua **parcialmente** atendido: o relatório é gerado e baixável, mas não é
"especializado" nem traz os anexos navegáveis que o documento descreve. A Fase 6 **fecha essa lacuna** sem
reabrir as decisões já tomadas (S12 fusão por regras, S16 relatório MD/HTML+PDF opcional, S17 storage,
contrato estável).

## Goals

- [ ] **Especializar o relatório por tipo de risco** (`docs/06 §1/§4`): a seção de **recomendação /
      encaminhamento** e o **conteúdo-chave** SHALL ser derivados dos **gatilhos** acionados
      (`infeccao_puerperal`, `pre_eclampsia`, `violencia`, `desconforto_psicologico`), não apenas do nível de
      risco — cobrindo os 4 tipos do PDF (fonte: `docs/06 §1` e tabela `§4`).
- [ ] **Anexos com links reais** (`docs/06 §3/§5`): a seção **5. Anexos** SHALL referenciar os **artefatos
      do caso** (URL do vídeo/frame da cicatriz, do CSV/gráfico de sinais vitais, do áudio/transcrição, do
      texto) a partir do objeto de requisição do contrato, em vez de só listar nomes de modalidade.
- [ ] **Garantir a geração de PDF** no ambiente conteinerizado (libs de sistema do `weasyprint` no
      `Dockerfile` do `ai-service`), **mantendo o fallback HTML/Markdown** (S16/DD7) onde o PDF não estiver
      disponível — para que `docs/06` ("Markdown → PDF") seja cumprido de fato no deploy.
- [ ] **Visualizar o relatório no dashboard** (`docs/06 §5` "exibir no dashboard"): além do botão de
      **download** já existente, oferecer **pré-visualização** (HTML inline) do relatório na tela de detalhe
      do caso, acessível (não depender só de baixar o arquivo).
- [ ] **Cobrir com testes e atualizar evidências**: testes do template **especializado** e do mapeamento
      **gatilho → encaminhamento/anexo**; atualizar o exemplo em
      [`docs/relatorio/exemplo-relatorio-automatico.md`](../../../docs/relatorio/exemplo-relatorio-automatico.md)
      e a exportação ([`scripts/gerar_evidencias.py`](../../../scripts/gerar_evidencias.py)).
- [ ] **Manter o gate verde** (ruff+pytest / eslint+jest+vitest) e a reprodutibilidade por
      `docker compose up`, **sem regressão** das Fases 2–5 e **sem reabrir** o contrato de API.

## Out of Scope

Explicitamente excluído para evitar scope creep. Cada item é ação humana, pertence a outra fase, ou é uma
decisão de arquitetura já fechada.

| Item | Motivo / Onde entra |
| --- | --- |
| **Gravar/publicar o vídeo** demonstrando o relatório | **Ação humana** do grupo (`docs/06` nota final; roteiro já cobre — bloco 6 de [`roteiro-video.md`](../../../docs/roteiro-video.md)) |
| **Trocar o motor de fusão** ou mudar os gatilhos/regras | Decisão fechada (S12); a Fase 6 **consome** `fusao.gatilhos`, não os redefine |
| **Reescrever o contrato de API** (campos do JSON de risco) | Contrato estável ([`docs/contrato-api.md`](../../../docs/contrato-api.md)); `relatorio_url` já existe |
| **Gerar o "frame de alerta"** (recorte real da detecção da cicatriz) | Depende do **detector escalado** (F5-01, **bloqueado por ambiente**: GPU/dataset); a Fase 6 referencia a URL do artefato existente, não produz o recorte |
| **Editor/assinatura do relatório** ou fluxo de aprovação clínica | Fora do escopo do desafio (apoio à decisão, não prontuário oficial — disclaimer S16) |
| **Internacionalização** do relatório (outros idiomas) | Fora de escopo; o relatório é em pt-BR |

---

## User Stories

### P1: Relatório especializado por tipo de risco ⭐ MVP

**User Story**: Como equipe clínica, quero que o relatório traga **recomendação e conteúdo-chave
específicos do tipo de risco** detectado (infecção puerperal, pré-eclâmpsia, desconforto psicológico,
violência), para saber **qual protocolo acionar** — e não apenas uma frase genérica por nível.

**Why P1**: É o cerne do `docs/06 §1/§4` ("relatórios automáticos **especializados**") e a maior lacuna
atual; o relatório hoje recomenda só por nível (`RECOMENDACAO[risco]`).

**Acceptance Criteria**:

1. WHEN o relatório é gerado para um caso com gatilho `violencia` THEN a seção **4. Recomendação /
   encaminhamento** SHALL incluir o **protocolo de proteção** (não só "acionar a equipe").
2. WHEN o gatilho é `desconforto_psicologico` THEN o encaminhamento SHALL citar **avaliação/encaminhamento
   psicológico**; WHEN `infeccao_puerperal` THEN SHALL citar **risco de infecção da cesárea / reavaliação da
   ferida**; WHEN `pre_eclampsia` THEN SHALL citar o **risco hipertensivo / pré-eclâmpsia**, conforme a
   tabela do `docs/06 §4`.
3. WHEN **vários** gatilhos são acionados THEN o relatório SHALL listar o encaminhamento de **cada tipo**
   (sem perder nenhum), preservando o nível de risco global da fusão.
4. WHEN **nenhum** gatilho especializado é acionado THEN o relatório SHALL cair na recomendação **por nível**
   atual (compatibilidade — sem regressão).
5. WHEN o mapeamento é definido THEN ele SHALL reusar os **gatilhos** de [`app/fusao.py`](../../../ai-service/app/fusao.py)
   (rastreabilidade), sem duplicar a lógica de decisão.

**Independent Test**: Rodar `gerar_markdown` com casos sintéticos para cada gatilho e conferir que a seção 4
contém o encaminhamento especializado correspondente (teste de unidade puro, sem IO).

---

### P1: Anexos com links reais dos artefatos ⭐ MVP

**User Story**: Como profissional revisando o caso, quero que os **anexos** do relatório levem aos
**artefatos reais** (imagem da cicatriz, gráfico/CSV dos sinais vitais, áudio/transcrição, documento de
texto), para inspecionar a evidência — como o `docs/06 §3/§5` descreve ("links Blob: frame, gráfico, áudio").

**Why P1**: Sem os links, o relatório não cumpre a seção de anexos do `docs/06`; hoje só aparece o **nome**
da modalidade.

**Acceptance Criteria**:

1. WHEN o relatório é gerado THEN a seção **5. Anexos** SHALL referenciar as **URLs dos artefatos** presentes
   no objeto de requisição do contrato (`video_cicatriz_url`, `video_fisioterapia_url`,
   `dados_vitais.csv_url`, `audio_url`, `texto_clinico`/URL do documento).
2. WHEN uma modalidade **não tem** artefato (ausente/degradada — DD10) THEN ela SHALL ser **omitida** dos
   anexos sem quebrar o relatório.
3. WHEN o áudio possui **transcrição** disponível THEN o anexo de áudio SHALL referenciar o **trecho/transcrição**
   além da URL (conforme `docs/06 §3`).
4. WHEN nenhum artefato existir THEN a seção SHALL exibir **"Sem anexos."** (comportamento atual preservado).
5. WHEN o relatório é convertido para HTML/PDF THEN os anexos SHALL ser **links navegáveis** (não texto puro).

**Independent Test**: Gerar o relatório do `caso_alto` (com URLs no payload) e conferir que a seção 5 traz os
links dos artefatos; gerar um caso sem artefatos e conferir "Sem anexos."

---

### P2: PDF garantido no ambiente (com fallback HTML)

**User Story**: Como avaliador, quero que o relatório seja entregue de fato em **PDF** quando rodando o
serviço conteinerizado, cumprindo o "Markdown → PDF" do `docs/06`, sem perder o fallback HTML em ambientes
sem as libs.

**Why P2**: O `docs/06` cita PDF como saída; hoje o PDF degrada para HTML por falta de libs de sistema. É
valor de entrega, mas o HTML já é navegável — por isso não é MVP.

**Acceptance Criteria**:

1. WHEN o `Dockerfile` do `ai-service` é construído THEN ele SHALL instalar as **libs de sistema** exigidas
   pelo `weasyprint` (ex.: `libpango`, `libcairo`, `libgdk-pixbuf`), de modo que `_tentar_pdf` produza **PDF**.
2. WHEN o `weasyprint`/libs **não** estiverem disponíveis (ex.: gate enxuto, dev local) THEN o relatório
   SHALL continuar caindo no **HTML** sem quebrar o pipeline (S16/DD7 preservado).
3. WHEN o PDF é gerado THEN `relatorio_url` SHALL apontar para o **`.pdf`**; caso contrário, para o **`.html`**
   (comportamento atual mantido).
4. WHEN o backend serve o relatório THEN o **Content-Type** SHALL refletir a extensão real (rota
   [`GET /casos/:id/relatorio`](../../../backend/src/rotas/casos.js) já trata `.pdf`/`.html`).

**Independent Test**: Construir a imagem do `ai-service`, gerar um caso e confirmar `relatorio_url` `.pdf`
servido com `application/pdf`; rodar sem as libs e confirmar fallback `.html`.

---

### P2: Pré-visualização do relatório no dashboard

**User Story**: Como equipe de monitoramento, quero **ver** o relatório dentro do dashboard (não só baixar),
para ler o resumo e os encaminhamentos na própria tela de detalhe do caso.

**Why P2**: O `docs/06 §5` pede "exibir no dashboard"; o botão de download já existe (Fase 5), então a
pré-visualização é incremento de UX, não MVP.

**Acceptance Criteria**:

1. WHEN a tela de **detalhe do caso** ([`frontend/src/pages/DetalheCaso.tsx`](../../../frontend/src/pages/DetalheCaso.tsx))
   é aberta e `relatorio_url` existe THEN ela SHALL oferecer **pré-visualizar** (HTML inline/modal) além de
   **baixar**.
2. WHEN o relatório está **indisponível** THEN a UI SHALL tratar o estado vazio sem erro (degrada
   graciosamente).
3. WHEN o relatório é exibido THEN o **disclaimer** ("apoio à decisão, não diagnóstico") SHALL permanecer
   visível.
4. WHEN exibido THEN o alerta/risco SHALL manter a acessibilidade já adotada (cor + ícone + texto).

**Independent Test**: Subir backend+frontend, abrir um caso com relatório e confirmar a pré-visualização +
download; abrir um caso sem relatório e confirmar o estado vazio.

---

### P3: Testes e evidências atualizadas

**User Story**: Como mantenedor, quero **testes** do relatório especializado e dos anexos, além das
**evidências** (exemplo/exportação) atualizadas, para garantir que a Fase 6 não regrida e fique demonstrável.

**Why P3**: Qualidade/rastreabilidade; depende de P1/P2 estarem prontos.

**Acceptance Criteria**:

1. WHEN o template especializado é implementado THEN [`ai-service/tests/test_relatorio.py`](../../../ai-service/tests/test_relatorio.py)
   SHALL cobrir o encaminhamento por gatilho e a seção de anexos com links.
2. WHEN as evidências são regeneradas THEN o exemplo em `docs/relatorio/` SHALL refletir o novo formato
   (gerado por `scripts/gerar_evidencias.py`, **reusando** `app/relatorio.py` — nunca editado à mão, S23).
3. WHEN o gate roda THEN `ruff`+`pytest` e `eslint`+`jest`+`vitest` SHALL ficar **verdes** sem regressão.

**Independent Test**: Rodar `pytest -q` (novos casos verdes) e `scripts/gerar_evidencias.py`; conferir o
exemplo atualizado.

---

## Edge Cases

- WHEN o caso aciona **gatilhos conflitantes** (ex.: vários ALTO) THEN o relatório SHALL listar **todos** os
  encaminhamentos, mantendo o nível global da fusão (sem inventar prioridade não definida nas regras).
- WHEN o **objeto de requisição** não traz a URL de uma modalidade presente nas evidências THEN o anexo dessa
  modalidade SHALL ser **omitido** (não fabricar links).
- WHEN o `weasyprint`/libs **faltam** THEN o relatório SHALL **degradar para HTML** sem quebrar (S16/DD7).
- WHEN a URL do artefato for um **caminho local** (fallback `STORAGE_BACKEND=local`) THEN o anexo SHALL
  referenciar o caminho/identificador disponível sem assumir um endpoint inexistente.
- WHEN o **frame de alerta** real (recorte da cicatriz) ainda não existir (detector smoke — F5-01 bloqueado)
  THEN o anexo SHALL apontar para o **vídeo/imagem de origem**, documentando a limitação (DD10) — sem inventar
  um recorte.

---

## Requirement Traceability

| Requirement ID | Story | Fonte (lacuna real) | Phase | Status |
| --- | --- | --- | --- | --- |
| F6-01 | P1: Relatório especializado por tipo de risco | `docs/06 §1/§4` vs. `relatorio.py` (recomendação só por nível) | — | Pending |
| F6-02 | P1: Anexos com links reais dos artefatos | `docs/06 §3/§5` vs. `_secao_anexos` (só nomes) | — | Pending |
| F6-03 | P2: PDF garantido no ambiente (fallback HTML) | `docs/06 §5` vs. PDF best-effort (S16/DD7) | — | Pending |
| F6-04 | P2: Pré-visualização do relatório no dashboard | `docs/06 §5` "exibir no dashboard" vs. só download | — | Pending |
| F6-05 | P3: Testes + evidências atualizadas | qualidade/rastreabilidade (S23) | — | Pending |

**ID format:** `F6-[NUMBER]` (Fase 6).
**Status values:** Pending → In Design → In Tasks → Implementing → Verified | Bloqueado (ambiente).
**Coverage:** 5 requisitos. F6-01/02/05 são **viáveis neste ambiente** (lógica pura + UI + testes); F6-03
depende de libs de sistema na imagem (controlável no `Dockerfile`); o **frame de alerta real** permanece
ligado ao detector escalado (F5-01, bloqueado por ambiente) e está **fora de escopo** (ver tabela).

---

## Decisões a confirmar com o grupo

> Conforme `AGENTS.md` (Princípio 1 — não presumir). Estas escolhas mudam o esforço e devem ser confirmadas
> **antes** do Design.

1. **Esta é a "Fase 6" pretendida?** A proposta é **especializar e enriquecer o relatório existente**
   (conteúdo por tipo + anexos com links + PDF garantido + preview). Se "Fase 6" se referir a **outro Tech
   Challenge da pós (8IADT)** com enunciado próprio, forneça o **PDF/requisitos** para reescrever esta spec.
2. **Origem do encaminhamento especializado:** mapear **gatilho → texto** dentro do relatório
   (`app/relatorio.py`) **ou** expor o texto a partir da fusão (`app/fusao.py`)? (Proposta: mapa no relatório,
   reusando `gatilhos`, para não inflar a fusão.)
3. **Anexos no fallback local:** referenciar **caminho/identificador local** do artefato ou só exibir a
   modalidade quando não houver URL pública (Azure SAS)? (Proposta: link quando houver URL http(s); senão,
   identificador do artefato.)
4. **PDF na imagem:** instalar as libs do `weasyprint` no `Dockerfile` (aumenta a imagem) **ou** manter PDF
   só como passo opcional documentado? (Proposta: instalar no `ai-service` e manter o fallback.)
5. **Profundidade do preview:** **modal/inline** na tela de detalhe **ou** apenas abrir o relatório em nova
   aba (como hoje)? (Proposta: preview inline + manter o download.)

---

## Success Criteria

Como saberemos que a Fase 6 está pronta:

- [ ] **Relatório especializado**: a seção de encaminhamento reflete **cada gatilho** (infecção puerperal,
      pré-eclâmpsia, desconforto psicológico, violência), conforme `docs/06 §4` — F6-01.
- [ ] **Anexos com links** reais dos artefatos do caso (frame/imagem, gráfico/CSV, áudio/transcrição, texto),
      omitindo modalidades ausentes — F6-02.
- [ ] **PDF gerado** no ambiente conteinerizado, com **fallback HTML** intacto e Content-Type correto — F6-03.
- [ ] **Pré-visualização** do relatório no dashboard, com disclaimer e acessibilidade — F6-04.
- [ ] **Testes** do template especializado/anexos verdes e **exemplo/exportação** regenerados (S23) — F6-05.
- [ ] **Gate verde** preservado (ruff+pytest / eslint+jest+vitest) e `docker compose up` reprodutível, sem
      regressão das Fases 2–5 nem mudança no contrato de API.
- [ ] **STATE** e **docs** atualizados (Fase 6 registrada, decisões confirmadas).

> **Itens que permanecem ação humana / bloqueados por ambiente** (não bloqueiam a Fase 6): gravar o **vídeo**
> demonstrando o relatório (DD-F4-5) e produzir o **frame de alerta real** da cicatriz (depende do detector
> escalado — F5-01).
