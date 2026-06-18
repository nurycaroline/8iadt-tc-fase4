# Fase 1 — Aquisição e Preparação de Dados — Especificação

> Documento de planejamento gerado a partir de [`docs/01-fase1-dados.md`](../../../docs/01-fase1-dados.md).
> Fonte de escopo: [`docs/00-visao-geral-e-escopo.md`](../../../docs/00-visao-geral-e-escopo.md),
> [`docs/datasets.md`](../../../docs/datasets.md) e [`docs/contrato-api.md`](../../../docs/contrato-api.md).

## Problem Statement

Para treinar e demonstrar a solução de IA multimodal de acompanhamento no pós-parto, precisamos de um
**mini-dataset limpo** (5 amostras por modalidade: vídeo de cicatriz, vídeo de fisioterapia, sinais
vitais, áudio e texto clínico) e de um **caso de exemplo sintético** que junte uma amostra de cada
modalidade numa "paciente" fictícia. Sem esses dados padronizados e sem o caso sintético, nenhum
modelo da Fase 2 pode ser treinado e a fusão multimodal da Fase 3 não tem como ser demonstrada.

## Goals

- [ ] Mini-dataset com **5 amostras por modalidade** (4 modalidades) limpas/rotuladas e prontas para a Fase 2.
- [ ] Amostra de cicatriz convertida para o **formato YOLOv8** via script, com visualização das anotações.
- [ ] Amostra de fisioterapia preparada para **YOLOv8-pose** (keypoints).
- [ ] Sinais vitais limpos e rotulados (`low/mid/high`) a partir do Maternal Health Risk.
- [ ] 5 áudios transcritos e rotulados (categoria de risco psicológico/violência).
- [ ] 5 documentos de texto clínico rotulados (achados normais e de risco).
- [ ] **Caso de exemplo sintético** que combina 1 amostra de cada modalidade numa paciente fictícia,
      com variantes `BAIXO / MÉDIO / ALTO`, alinhado ao [contrato de API](../../../docs/contrato-api.md).
- [ ] Estrutura `data/` criada e **ignorada pelo Git**; apenas scripts e metadados versionados.
- [ ] Origem e licença de cada dataset registradas (para o relatório técnico).

## Out of Scope

Explicitamente excluído para evitar scope creep. Cada item pertence a uma fase posterior.

| Item                                              | Motivo / Onde entra                    |
| ------------------------------------------------- | -------------------------------------- |
| Treinar qualquer modelo (YOLO, RF, classificador) | Fase 2 — esta fase só prepara os dados |
| Motor de fusão / derivação de risco real          | Fase 3 (regras)                        |
| API Node/Python, WebSocket, deploy Azure          | Fase 3                                 |
| Baixar datasets **inteiros**                      | Política do projeto: só amostras       |
| Anotação manual pesada / Roboflow                 | Preferir datasets já anotados + script |
| Relatórios automáticos e dashboard                | Fases 3/4                              |
| Dados reais de pacientes                           | LGPD — só dados públicos/sintéticos    |

---

## User Stories

### P1: Estrutura de dados e reprodutibilidade ⭐ MVP

**User Story**: Como integrante do grupo, quero uma estrutura `data/` padronizada (ignorada pelo Git)
e instruções de como obter os dados, para que qualquer pessoa reproduza o mini-dataset sem versionar
dados sensíveis.

**Why P1**: É a fundação de todas as outras tarefas; sem o layout e o `.gitignore` corretos corremos
risco de versionar dados sensíveis e de scripts gravarem em locais divergentes.

**Acceptance Criteria**:

1. WHEN o repositório é clonado THEN o sistema SHALL conter um `.gitignore` que ignora `data/`
   (exceto arquivos de exemplo/metadados explicitamente permitidos).
2. WHEN um script de preparação roda THEN ele SHALL gravar dentro de `data/<modalidade>/` seguindo o layout documentado.
3. WHEN alguém consulta o README de dados THEN o sistema SHALL informar como obter cada dataset, com origem e licença.

**Independent Test**: Clonar o repo, rodar `git status` após criar arquivos em `data/` e confirmar que
não aparecem como rastreados; abrir o README de dados e verificar a tabela de origem/licença.

---

### P1: Sinais vitais limpos e rotulados ⭐ MVP

**User Story**: Como engenheiro de dados, quero baixar e limpar o Maternal Health Risk e extrair 5
amostras rotuladas, para que a Fase 2 treine o modelo de risco materno.

**Why P1**: É a modalidade mais simples e barata (tabular, licença CC BY 4.0), serve de "hello world"
da fase e alimenta o caso sintético.

**Acceptance Criteria**:

1. WHEN o script de sinais vitais roda THEN ele SHALL baixar o CSV do Maternal Health Risk para `data/sinais_vitais/`.
2. WHEN o CSV é processado THEN o script SHALL remover outliers fisiologicamente implausíveis e padronizar unidades.
3. WHEN a limpeza termina THEN o script SHALL produzir ao menos **5 amostras rotuladas** (`low/mid/high`) num CSV limpo.
4. WHEN há valores faltantes ou fora de faixa THEN o script SHALL tratá-los de forma explícita (descartar/registrar), sem quebrar.

**Independent Test**: Rodar o script e inspecionar o CSV de saída com 5+ linhas, colunas de features
normalizadas e a coluna de rótulo `RiskLevel`.

---

### P1: Amostra de cicatriz no formato YOLOv8 ⭐ MVP

**User Story**: Como engenheiro de visão computacional, quero converter uma amostra do AZH Wound para
o formato YOLOv8 e visualizar as anotações sobrepostas, para que a Fase 2 treine o detector de infecção.

**Why P1**: É o "hello world" do vídeo e o item do caminho crítico (treino do YOLO é o mais demorado).

**Acceptance Criteria**:

1. WHEN o script de cicatriz roda THEN ele SHALL baixar **apenas uma amostra** do AZH Wound para `data/video_cicatriz/`.
2. WHEN a conversão roda THEN o script SHALL gerar rótulos no **formato YOLOv8** (`.txt` normalizado) com as classes `ferida_ok` e `ferida_alerta`.
3. WHEN a conversão termina THEN o script SHALL gerar um arquivo `data.yaml` com as classes e os caminhos.
4. WHEN a visualização roda THEN o sistema SHALL salvar/exibir ao menos 1 imagem com as bounding boxes/polígonos sobrepostos.

**Independent Test**: Rodar o script, abrir a imagem de visualização gerada e conferir as anotações
sobre a ferida; validar o `data.yaml`.

---

### P2: Caso de exemplo sintético (a "cola" da demo)

**User Story**: Como responsável pela demo, quero um script que monte uma paciente fictícia juntando 1
amostra de cada modalidade, para que a fusão multimodal seja demonstrável sem paciente real.

**Why P2**: É o gargalo subestimado (M9 no cronograma) que bloqueia a demo da fusão, mas depende de
existirem amostras das modalidades. Importante, porém não é o "hello world" inicial.

**Acceptance Criteria**:

1. WHEN o script do caso sintético roda THEN ele SHALL produzir um pacote por caso (JSON de metadados + referências aos arquivos de cada modalidade).
2. WHEN o caso é gerado THEN o JSON SHALL ser coerente com o objeto de requisição do [contrato de API](../../../docs/contrato-api.md) (`case_id`, `paciente`, URLs/refs por modalidade).
3. WHEN solicitado THEN o script SHALL gerar 3 variantes: **normal (BAIXO)**, **risco isolado (MÉDIO)** e **multi-risco (ALTO)**.
4. WHEN uma modalidade não tem amostra disponível THEN o script SHALL omitir o campo correspondente (campos são opcionais no contrato), sem quebrar.

**Independent Test**: Rodar o script e validar que cada JSON gerado referencia arquivos existentes em
`data/` e segue o schema do contrato de API, com as 3 variantes.

---

### P2: Áudios transcritos e rotulados

**User Story**: Como engenheiro de áudio, quero 5 áudios curtos transcritos e rotulados por categoria
de risco, para que a Fase 2 treine/valide a classificação de fala.

**Why P2**: Modalidade com limitação de domínio (não há base só de pós-parto); usa bases gerais + TTS.

**Acceptance Criteria**:

1. WHEN os áudios são coletados THEN o conjunto SHALL conter 5 amostras cobrindo: depressão pós-parto, ansiedade, neutro, violência, fadiga.
2. WHEN o script de transcrição roda THEN ele SHALL transcrever cada áudio (Whisper local ou Azure Speech-to-Text) para texto.
3. WHEN a transcrição termina THEN cada áudio SHALL ter um rótulo de categoria registrado em um arquivo de metadados.

**Independent Test**: Rodar a transcrição e conferir o arquivo de metadados com 5 entradas (caminho do
áudio, transcrição, categoria).

---

### P2: Texto clínico rotulado

**User Story**: Como engenheiro de NLP, quero ~5 documentos de texto clínico rotulados, para que a
Fase 2 tenha entrada para o módulo de texto.

**Why P2**: Fecha a tríade "áudio, vídeo e texto"; pode ser sintético (rápido, sem privacidade).

**Acceptance Criteria**:

1. WHEN os documentos são reunidos THEN o conjunto SHALL conter ~5 textos com achados normais e de risco (ex.: PA alta, proteinúria, febre/dor na cicatriz).
2. WHEN os documentos são rotulados THEN cada um SHALL ter trechos/achados de interesse marcados (`complicacao`/`sinal_infeccao`/`neutro`).
3. WHEN salvos THEN os textos SHALL estar em texto simples padronizado, prontos para o módulo de NLP.

**Independent Test**: Abrir o diretório de texto, conferir 5 documentos + arquivo de rótulos com os achados.

---

### P3: Amostra de fisioterapia preparada para pose

**User Story**: Como engenheiro de visão, quero amostras de exercícios de reabilitação preparadas para
YOLOv8-pose, para que a Fase 2 acompanhe a qualidade do movimento.

**Why P3**: Segundo uso do vídeo; útil, mas a detecção de cicatriz já cobre o requisito de vídeo do MVP.

**Acceptance Criteria**:

1. WHEN o script de fisioterapia roda THEN ele SHALL baixar amostras de alguns exercícios (UCO PhyRehab ou IntelliRehabDS) para `data/video_fisioterapia/`.
2. WHEN preparado THEN o material SHALL estar no formato esperado pelo YOLOv8-pose (keypoints) ou reaproveitar os keypoints fornecidos.
3. WHEN rotulado THEN as repetições SHALL ser marcadas como `correto`/`incorreto`.

**Independent Test**: Rodar o script e conferir os keypoints/rótulos das repetições para ao menos uma amostra.

---

## Edge Cases

- WHEN um download de dataset falha (rede/URL/licença) THEN o script SHALL falhar com mensagem clara e instrução de obtenção manual (sem deixar arquivos parciais corrompidos).
- WHEN o dataset inteiro seria baixado por engano THEN o script SHALL limitar a amostragem (parâmetro de N amostras) para respeitar a política "só amostras".
- WHEN um registro de sinais vitais tem valores impossíveis (ex.: PA 0 ou 400) THEN o script SHALL descartá-lo e registrar no log.
- WHEN o caso sintético referencia uma modalidade ausente THEN o JSON SHALL omitir o campo (opcional), sem erro.
- WHEN um arquivo de saída já existe THEN o script SHALL ser idempotente (sobrescrever de forma previsível ou pular), sem duplicar dados.

---

## Requirement Traceability

| Requirement ID | Story                              | Phase  | Status  |
| -------------- | ---------------------------------- | ------ | ------- |
| F1D-01         | P1: Estrutura de dados             | Tasks  | Pending |
| F1D-02         | P1: Estrutura de dados (.gitignore)| Tasks  | Pending |
| F1D-03         | P1: README/origem+licença          | Tasks  | Pending |
| F1D-04         | P1: Sinais vitais (download)       | Tasks  | Pending |
| F1D-05         | P1: Sinais vitais (limpeza+rótulo) | Tasks  | Pending |
| F1D-06         | P1: Cicatriz (download amostra)    | Tasks  | Pending |
| F1D-07         | P1: Cicatriz (conversão YOLO)      | Tasks  | Pending |
| F1D-08         | P1: Cicatriz (visualização)        | Tasks  | Pending |
| F1D-09         | P2: Caso sintético (builder)       | Tasks  | Pending |
| F1D-10         | P2: Caso sintético (variantes)     | Tasks  | Pending |
| F1D-11         | P2: Áudio (coleta)                 | Tasks  | Pending |
| F1D-12         | P2: Áudio (transcrição+rótulo)     | Tasks  | Pending |
| F1D-13         | P2: Texto clínico                  | Tasks  | Pending |
| F1D-14         | P3: Fisioterapia (pose)            | Tasks  | Pending |

**ID format:** `F1D-[NUMBER]` (Fase 1 Dados).
**Status values:** Pending → In Design → In Tasks → Implementing → Verified.
**Coverage:** 14 requisitos, todos mapeados para tarefas em `tasks.md`.

---

## Success Criteria

Como saberemos que a Fase 1 está pronta (gate de fim de fase do cronograma):

- [ ] Existem **5 amostras por modalidade** (4 modalidades) limpas/rotuladas em `data/`.
- [ ] Amostra de cicatriz visualizável no formato YOLOv8 com `data.yaml` válido.
- [ ] Caso de exemplo sintético gerado nas 3 variantes (BAIXO/MÉDIO/ALTO), coerente com o contrato de API.
- [ ] `git status` não rastreia nenhum dado dentro de `data/`.
- [ ] Tabela de origem/licença de cada dataset documentada para o relatório.
- [ ] Scripts de preparação são reexecutáveis (idempotentes) e têm testes unitários nas funções puras (parsing/features/builder).
