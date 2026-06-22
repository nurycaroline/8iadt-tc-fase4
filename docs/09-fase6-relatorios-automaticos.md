# Fase 6 — Relatórios Automáticos Especializados

> Objetivo: elevar o **relatório automático** atual (genérico, gerado desde a Fase 3) ao que o requisito
> [`06-relatorios-automaticos.md`](06-relatorios-automaticos.md) descreve — **conteúdo especializado por
> tipo de risco** e **anexos com links reais** —, mantendo as decisões de arquitetura já tomadas.
> Planejamento detalhado (Specify) em
> [`.specs/features/fase6-relatorios-automaticos/`](../.specs/features/fase6-relatorios-automaticos/spec.md).

> ⚠️ **Rascunho de planejamento (escopo a confirmar — `AGENTS.md`).** O relatório automático **já existe**
> (`ai-service/app/relatorio.py`, gerado pelo pipeline; com download no dashboard desde a Fase 5) e **não
> havia "Fase 6"** no plano. Esta fase foi proposta como **Relatórios Automáticos Especializados** porque é a
> lacuna restante entre o `docs/06` e o código. Se "Fase 6" significar **outro desafio (8IADT)** com enunciado
> próprio, traga o PDF e o escopo será reescrito. Pontos a confirmar com o grupo na seção
> [Decisões a confirmar](../.specs/features/fase6-relatorios-automaticos/spec.md#decisões-a-confirmar-com-o-grupo).

## Motivação (o que falta para cumprir o `docs/06`)

| # | Requisito do `docs/06` | Estado atual | Lacuna |
|---|------------------------|--------------|--------|
| 1 | **Conteúdo especializado por tipo de risco** (§1/§4) — infecção puerperal, pré-eclâmpsia, desconforto psicológico, violência | Relatório **genérico**; recomendação por **nível** (`RECOMENDACAO[risco]`) | Encaminhamento/conteúdo-chave **por gatilho** ainda não derivado |
| 2 | **Anexos com links reais** (§3/§5) — "links Blob: frame, gráfico, áudio" | `_secao_anexos` lista só o **nome** da modalidade | Falta repassar as **URLs dos artefatos** do contrato ao relatório |
| 3 | **Markdown → PDF** (§5) | PDF **best-effort**; HTML como fallback (S16/DD7) | Falta **garantir o PDF** no ambiente (libs do `weasyprint` na imagem) |
| 4 | **Exibir no dashboard** (§5) | Botão **"Ver/baixar relatório"** (Fase 5) | Falta **pré-visualização** (HTML inline) na tela de detalhe |

> **Permanece ação humana / bloqueado por ambiente** (não é desenvolvimento desta fase): gravar o **vídeo**
> demonstrando o relatório (DD-F4-5) e produzir o **frame de alerta real** da cicatriz (depende do detector
> escalado — F5-01, GPU/dataset).

## Estado da implementação

> Esta fase está em **planejamento (Specify)**. A implementação só começa **após a confirmação do escopo** e
> as fases de **Design** → **Tasks** (skill `tlc-spec-driven`). Nada de código foi alterado ainda.

| Req | Item | Estado |
|-----|------|--------|
| F6-01 | Relatório especializado por tipo de risco (§1/§4) | ⏳ **Planejado** (viável neste ambiente — lógica pura) |
| F6-02 | Anexos com links reais dos artefatos (§3/§5) | ⏳ **Planejado** (viável — usa URLs do contrato) |
| F6-03 | PDF garantido no ambiente (fallback HTML) | ⏳ **Planejado** (libs no `Dockerfile`; fallback S16/DD7) |
| F6-04 | Pré-visualização do relatório no dashboard (§5) | ⏳ **Planejado** (incremento de UX sobre o download) |
| F6-05 | Testes do template especializado + evidências | ⏳ **Planejado** (qualidade/rastreabilidade S23) |

## Resultado esperado (Definition of Done)

- [ ] **Relatório especializado**: a seção "Recomendação / encaminhamento" reflete **cada gatilho** acionado
      (infecção puerperal, pré-eclâmpsia, desconforto psicológico, violência), conforme `docs/06 §4` — F6-01.
- [ ] **Anexos com links** reais dos artefatos do caso (frame/imagem, gráfico/CSV, áudio/transcrição, texto),
      omitindo modalidades ausentes (DD10) — F6-02.
- [ ] **PDF gerado** no ambiente conteinerizado, com **fallback HTML** intacto e Content-Type correto — F6-03.
- [ ] **Pré-visualização** do relatório no dashboard, com disclaimer e acessibilidade — F6-04.
- [ ] **Testes** do template especializado/anexos verdes e **exemplo/exportação** regenerados (S23) — F6-05.
- [ ] **Gate verde** preservado (`ruff`+`pytest` / `eslint`+`jest`+`vitest`) e `docker compose up`
      reprodutível, **sem regressão** das Fases 2–5 e **sem reabrir** o contrato de API.

---

## Tarefas (visão macro)

> Quebra atômica (com dependências, "done when" e gate por tarefa) virá no `tasks.md` da feature **após** a
> confirmação do escopo e a fase de **Design**. Visão macro abaixo, em ordem sugerida.

### Tarefa 6.1 — Encaminhamento especializado por gatilho (F6-01)
- Definir o mapa **gatilho → conteúdo-chave/encaminhamento** (4 tipos do `docs/06 §4`), reusando
  `app/fusao.py:gatilhos` (sem duplicar a decisão).
- Ajustar `app/relatorio.py:gerar_markdown` para montar a **seção 4** a partir dos gatilhos, mantendo o
  fallback por nível quando não houver gatilho especializado.

### Tarefa 6.2 — Anexos com links reais (F6-02)
- Repassar o **objeto de requisição** (URLs dos artefatos) a `gerar_e_salvar`/`gerar_markdown` e montar a
  **seção 5** com links navegáveis (frame/vídeo, gráfico/CSV, áudio/transcrição, texto), omitindo ausentes.

### Tarefa 6.3 — PDF garantido no ambiente (F6-03)
- Instalar as libs de sistema do `weasyprint` no [`ai-service/Dockerfile`](../ai-service/Dockerfile);
  validar que `_tentar_pdf` produz **PDF** e que o **fallback HTML** continua intacto onde faltarem libs.

### Tarefa 6.4 — Pré-visualização no dashboard (F6-04)
- Adicionar **preview** (HTML inline/modal) na tela de detalhe
  ([`frontend/src/pages/DetalheCaso.tsx`](../frontend/src/pages/DetalheCaso.tsx)), além do download já
  existente; tratar estado vazio e manter o disclaimer/acessibilidade.

### Tarefa 6.5 — Testes e evidências (F6-05)
- Estender [`ai-service/tests/test_relatorio.py`](../ai-service/tests/test_relatorio.py) (encaminhamento por
  gatilho + anexos com links) e regenerar o exemplo em
  [`docs/relatorio/exemplo-relatorio-automatico.md`](relatorio/exemplo-relatorio-automatico.md) via
  [`scripts/gerar_evidencias.py`](../scripts/gerar_evidencias.py) (reuso, nunca edição manual — S23).

---

## Caminho crítico e paralelização

- **Caminho crítico:** 6.1 (encaminhamento especializado) → 6.5 (testes/evidências dependem do novo formato).
- **Paralelizável:** 6.2 (anexos), 6.3 (PDF/Dockerfile) e 6.4 (preview no front) podem correr em paralelo,
  pois tocam pontos independentes (relatório, imagem, UI).
- **Sem libs de PDF?** A 6.3 degrada para o **fallback HTML** (S16/DD7) sem quebrar o gate.

## Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Imagem do `ai-service` maior com as libs de PDF | Manter o fallback HTML; avaliar instalar libs só na imagem de runtime |
| Links de anexo quebrados no fallback local | Referenciar caminho/identificador quando não houver URL http(s) (decisão na spec) |
| Frame de alerta real depende do detector escalado (F5-01) | Fora de escopo: referenciar o vídeo/imagem de origem e documentar a limitação (DD10) |
| Regressão do relatório atual | Manter o fallback por nível e cobrir com testes (6.5); gate verde obrigatório |
| Escopo divergente ("outro 8IADT") | Confirmar com o grupo **antes** do Design (AGENTS.md) |
