# Fase 1 — Aquisição e Preparação de Dados

> Objetivo: ter um **mini-dataset** limpo e pronto para as 4 modalidades, mais o **caso de exemplo sintético** que liga as amostras a uma paciente fictícia (para demonstrar a fusão).

## Resultado esperado (Definition of Done)
- [ ] Amostra de **vídeo/imagem de cicatriz** (AZH Wound) baixada e convertida para o formato YOLO via script.
- [ ] 5 amostras de **sinais vitais** (Maternal Health Risk) limpas e rotuladas.
- [ ] 5 áudios de consulta/relato (ou sintéticos/abertos) transcritos.
- [ ] 5 documentos de **texto clínico** (laudos/exames/evolução) rotulados.
- [ ] Script que monta o **caso de exemplo sintético** (junta 1 amostra de cada modalidade em 1 "paciente").
- [ ] Estrutura de pastas `data/` criada (e no `.gitignore`).

---

## Tarefa 1.1 — Vídeo: cicatriz da cesárea (visão computacional)
> **Sem Roboflow e sem anotação manual sempre que possível.** Preferimos datasets que **já vêm anotados** e apenas **convertemos** para o formato YOLO via script.
- **Dataset recomendado:** **AZH Wound** — 730 imagens de feridas (inclui **feridas cirúrgicas**). Ver [datasets.md](datasets.md).
- **Passos (tudo automático):**
  1. Baixar uma **amostra** do dataset (não o dataset inteiro).
  2. Definir as classes alvo (ex.: `ferida_ok`, `ferida_alerta` para vermelhidão/secreção/deiscência) e rodar um **script de conversão** para o **formato YOLOv8** (`.txt` com bounding boxes/polígonos normalizados).
  3. (Se necessário) extrair frames de vídeos curtos com OpenCV/ffmpeg.
- **"Hello World":** converter 1 amostra para o formato YOLO e visualizar 1 imagem com as anotações sobrepostas.

> **Observação sobre o domínio:** o AZH Wound não é específico de cesárea, mas **feridas cirúrgicas têm aparência semelhante**. Registrar essa decisão (e a limitação) no relatório técnico.

## Tarefa 1.2 — Sinais vitais (tabular)
- **Dataset:** **Maternal Health Risk** (UCI) — 1.013 registros com PA sistólica/diastólica, glicemia, temperatura, batimentos e nível de risco (`low/mid/high`). Ver [datasets.md](datasets.md).
- **Passos:**
  1. Baixar o CSV com **Pandas**.
  2. Limpar (remover outliers fisiologicamente implausíveis, padronizar unidades).
  3. Usar o rótulo `RiskLevel` (baixo/médio/alto) como alvo.
  4. Extrair/normalizar features (PA sistólica/diastólica, glicemia, temperatura, FC).

## Tarefa 1.3 — Áudio (consultas/relatos)
- **Fontes:** bases públicas de fala com depressão/ansiedade (**Androids Corpus**, **DEPAC**) e/ou **áudios sintéticos (TTS)** lendo falas de consulta; ou gravações próprias com consentimento simulado. Ver [datasets.md](datasets.md).
- **Passos:**
  1. Coletar 5 áudios curtos representando: depressão pós-parto, ansiedade, fala neutra, sinais de violência, fadiga.
  2. Transcrever com **Azure Speech-to-Text** ou **Whisper**.
  3. Rotular cada áudio com a categoria de risco psicológico.

> **Limitação honesta:** não há base só de depressão **pós-parto**. Usamos bases de depressão/ansiedade geral e explicamos isso no relatório.

## Tarefa 1.4 — Texto clínico (NLP)
- **Fontes:** laudos/exames sintéticos, registros de pré-natal/puerpério e notas de evolução clínica (gerados ou anonimizados de bases públicas).
- **Passos:**
  1. Reunir ~5 documentos de texto representando achados normais e de risco (ex.: PA alta, proteinúria, menção a febre/dor na cicatriz).
  2. Rotular trechos de interesse (termos de complicação, sintomas de risco).
  3. Padronizar em texto simples para o módulo de NLP da Fase 2.

## Tarefa 1.5 — Caso de exemplo sintético (a "cola" da demo)
> No uso real, os dados são **da mesma paciente**. Mas os datasets públicos são de **pessoas diferentes**. Para demonstrar a fusão, montamos casos fictícios coerentes.
- **Script Python** que monta um "paciente de exemplo" juntando **1 amostra de cada modalidade** (ex.: cicatriz com alerta + PA alta + áudio com sinal de risco + laudo com proteinúria).
- Gera também variações **normais** (tudo dentro do esperado → risco BAIXO) e de **risco isolado** (só 1 modalidade alterada → risco MÉDIO).
- Saída: um pacote por caso (referências aos arquivos + metadados) que alimenta a fusão e a demonstração no vídeo final.

---

## Boas práticas desta fase
- Não baixar datasets inteiros — só amostras.
- `data/` no `.gitignore`; documentar no README **como** obter os dados.
- Registrar a **origem e licença** de cada dataset (importante para o relatório).
- Versionar apenas os **scripts** de download/preparação, não os dados.
