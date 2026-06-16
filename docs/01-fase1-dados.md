# Fase 1 — Aquisição e Preparação de Dados

> Objetivo: ter um **mini-dataset** limpo e pronto para as 3 modalidades, mais o **mock de sincronização** vídeo↔sinais vitais.

## Resultado esperado (Definition of Done)
- [ ] 5 clipes curtos de vídeo cirúrgico selecionados e anotados.
- [ ] 5 séries de sinais vitais (CTG/VitalDB) limpas e rotuladas.
- [ ] 5 áudios de consulta (ou sintéticos/abertos) transcritos.
- [ ] 5 documentos de **texto clínico** (laudos/prescrições/evolução) rotulados.
- [ ] Script de geração de **PA sintética sincronizada** com o evento de sangramento.
- [ ] Estrutura de pastas `data/` criada (e no `.gitignore`).

---

## Tarefa 1.1 — Vídeo (visão computacional)
- **Datasets:** AutoLaparo (histerectomia laparoscópica, com máscaras), CholecT50, SurgToolLoc. Ver [datasets.md](datasets.md).
- **Passos:**
  1. Baixar uma **amostra** (não o dataset inteiro).
  2. Extrair frames dos vídeos (ex.: 1 fps) com OpenCV/ffmpeg.
  3. Anotar classes-alvo no **Roboflow**: `sangramento`, `utero`, `ovario`, `instrumento`.
  4. Exportar no **formato YOLOv8** (`.txt` com coordenadas normalizadas, ou segmentação).
- **"Hello World":** converter as máscaras do AutoLaparo para o formato YOLO e visualizar 1 frame anotado.

## Tarefa 1.2 — Sinais vitais (tabular/série temporal)
- **Datasets:** CTU-CHB Intrapartum CTG (FHR + UC), VitalDB (PA, FC, oximetria em cirurgia). Ver [datasets.md](datasets.md).
- **Passos:**
  1. Baixar amostras com **Pandas/wfdb**.
  2. Limpar (remover artefatos, padronizar frequência de amostragem).
  3. Rotular janelas como `normal / suspeito / patológico` (CTG já traz classificação).
  4. Extrair features (média, desvio, mínimos de PA, FHR fora de 110–160 bpm).

## Tarefa 1.3 — Áudio (consultas)
- **Fontes:** áudios sintéticos (TTS lendo falas de consulta) ou bases públicas de fala emocional (ex.: RAVDESS para emoção; ou gravações próprias com consentimento simulado).
- **Passos:**
  1. Coletar 5 áudios curtos representando: ansiedade gestacional, depressão pós-parto, fala neutra, sinais de violência, fadiga.
  2. Transcrever com **Azure Speech-to-Text** ou **Whisper**.
  3. Rotular cada áudio com a categoria de risco psicológico.

## Tarefa 1.4 — Texto clínico (NLP)
- **Fontes:** laudos/exames sintéticos, prescrições hormonais e notas de evolução clínica (gerados ou anonimizados de bases públicas).
- **Passos:**
  1. Reunir ~5 documentos de texto representando achados normais e de risco.
  2. Rotular trechos de interesse (ex.: termos de complicação, prescrição inadequada, menção a sintomas de risco).
  3. Padronizar em texto simples para o módulo de NLP da Fase 2.

## Tarefa 1.5 — Mock de integração (sincronização)
> O segredo da fusão: os datasets reais **não** são sincronizados entre si.
- **Script Python** que gera uma série de **PA materna** ao longo do tempo do vídeo, com uma **queda brusca de PA exatamente no segundo** em que o vídeo mostra sangramento.
- Saída: CSV `tempo, PA_sistolica, PA_diastolica, FC` alinhado ao timestamp do vídeo.
- Esse CSV é o que alimenta a fusão e a demonstração no vídeo final.

---

## Boas práticas desta fase
- Não baixar datasets inteiros — só amostras.
- `data/` no `.gitignore`; documentar no README **como** obter os dados.
- Registrar a **origem e licença** de cada dataset (importante para o relatório).
- Versionar apenas os **scripts** de download/preparação, não os dados.
