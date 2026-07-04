# Datasets Recomendados

> Baixe **apenas amostras** para o mini-dataset. Registre origem e licença de cada um (vai para o relatório). Não versione os dados.

> ⚠️ **Treino x uso real.** Estas bases servem **só para treinar** cada modelo — são de **pessoas diferentes**, e tudo bem. O **"mesmo paciente"** só existe no **uso real**. Para demonstrar a fusão, monte um **caso de exemplo sintético** juntando 1 amostra de cada (ver [Fase 1, Tarefa 1.6](01-fase1-dados.md)).

## 1. Vídeo — cicatriz da cesárea (visão computacional)

> Objetivo: treinar o YOLOv8 a reconhecer **sinal de infecção** na cicatriz (vermelhidão, secreção, deiscência).

| Dataset | O que é | Por que usar | Link |
|---------|---------|--------------|------|
| **AZH Wound** ⭐ | 730 imagens de feridas (diabética, pressão, **cirúrgica**, venosa), anotadas por especialistas | Melhor base pública aberta de feridas; inclui **feridas cirúrgicas** | https://github.com/uwm-bigdata/wound-classification-using-images-and-locations |
| **Imaging-based SSI (referência)** | Pipeline para triagem de imagens de ferida pós-operatória enviadas pelo paciente | Inspiração de metodologia (dados são proprietários) | https://pubmed.ncbi.nlm.nih.gov/40607706/ |

**Estratégia (sem anotação manual pesada):**
1. Definir 2 classes simples: `ferida_ok` e `ferida_alerta` (sinal de infecção).
2. Converter para o formato YOLO via script (bounding box/polígono).
3. Treinar YOLOv8n/s e avaliar mAP/precisão/recall.

> **Domínio:** o AZH Wound não é específico de cesárea, mas **feridas cirúrgicas têm aparência semelhante**. Documente a decisão e a limitação no relatório.

## 2. Sinais vitais (tabular / dados clínicos)

> Objetivo: classificar **risco materno / pré-eclâmpsia** a partir de PA, FC, glicemia e temperatura.

| Dataset | O que é | Por que usar | Link |
|---------|---------|--------------|------|
| **Maternal Health Risk (UCI)** ⭐ | 1.013 registros (PA sistólica/diastólica, glicemia, temperatura, FC) com nível de risco `low/mid/high`; **CC BY 4.0** | Base aberta e direta para Random Forest | https://archive.ics.uci.edu/dataset/863/maternal+health+risk |
| **Preeclampsia (sintético, HF)** | ~21 mil amostras focadas em pré-eclâmpsia (fatores de risco com odds ratios da literatura) | Mais volume/foco em pré-eclâmpsia | https://huggingface.co/datasets/electricsheepafrica/africa-synth-maternal-health-preeclampsia-dataset-all |
| **Maternal health pregnancy (sintético, HF)** | 30 mil registros de pré-natal (PA, hemoglobina, glicemia, proteinúria, desfecho) | Cenários variados de risco | https://huggingface.co/datasets/LinderStacy-1/maternal-health-pregnancy |

## 3. Áudio (consultas / relatos) — Fase 8 (análise dupla)

> Objetivo: **classificador acústico de violência** no som **e** transcrição reanalisada como texto
> unificado. A depressão/ansiedade deixa de ser uma categoria de áudio por keyword e passa para os
> classificadores **ML de texto** (§5). Tudo **local/offline** (sem Azure). Ver
> [Fase 8](11-fase8-audio-texto-unificado.md).

| Fonte | O que é | Idioma | Licença | Uso |
|-------|---------|--------|---------|-----|
| **`Hemg/audio-based-violence-dataset`** ⭐ | ~2.171 clipes `audio` + `label` (`violence`/`Nonvoilence` — rótulo *sic*) | áudio | **não especificada** (HF) — risco | Treinar o classificador **acústico** de violência (features MFCC + `scikit-learn`) |
| **Áudios sintéticos (TTS)** | Falas de consulta nas categorias-alvo geradas por TTS | PT | próprio | Demo/smoke sem questão de privacidade |
| **Gravações próprias (consentimento simulado)** | Falas curtas gravadas pelo grupo | PT | próprio | Demonstração realista no vídeo |

> **Transcrição (ASR):** **Whisper local** (`openai-whisper`) por padrão; `faster-whisper` como
> alternativa. **Azure deixa de ser citado** (tudo offline).
> **Limitações honestas:** licença do `Hemg` **não especificada** (registrar risco); a violência
> acústica pode se **perder na transcrição** (por isso a trilha do som é separada); sem o modelo
> treinado, a trilha acústica degrada para neutro e a violência ainda é captada pelo texto (DD10).
> **Descartado:** `Androids Corpus`/`DEPAC` (a depressão migrou para o classificador de texto em PT).

## 4. Texto clínico (NLP) — Fase 8 (depressão + violência ML)

> Objetivo: além dos sinais de risco em laudos/evolução (PA alta, proteinúria, febre/dor na
> cicatriz — por keywords), **classificar depressão e violência** com modelos **ML treinados em
> PT-BR** (datasets EN traduzidos **offline** com Argos Translate). Ver
> [Fase 8](11-fase8-audio-texto-unificado.md).

| Fonte | O que é | Idioma | Licença | Uso |
|-------|---------|--------|---------|-----|
| **`ShreyaR/DepressionDetection`** ⭐ | ~7.731 linhas `clean_text` + `is_depression` (binário) | EN → **traduzido PT** | **não especificada** (HF) — risco | Treinar o classificador de **depressão** (TF-IDF + LogReg) |
| **`Spiderman01/Domestic_violence_info_support_fromposts`** | 273 posts EN de vítimas de VD (só **positivos**; rótulo é "tipo de apoio") | EN → **traduzido PT** | **não especificada** (HF) — risco | Treinar o classificador de **violência** (texto) — exige **negativos** |
| **Negativos de violência** | Amostras neutras (`is_depression=0`) do ShreyaR (PT) + textos clínicos neutros de `data/texto_clinico/` | EN→PT / PT | misto | Completar a classe negativa do classificador de violência |
| **Laudos/evolução sintéticos** | ~5 documentos com achados normais e de risco | PT | próprio | Keywords de infecção/complicação (preservadas) |

> **Tradução EN→PT:** **Argos Translate** (`argostranslate`, CPU, MIT) é o **padrão** (offline após
> baixar o pacote de idioma uma vez); **X-ALMA** é a opção preferencial selecionável por
> `TRADUCAO_BACKEND=xalma` (apenas estruturada — não baixa o modelo de 13B no fluxo padrão).
> **Limitações honestas:** licenças **não especificadas**; domínio Reddit/Twitter ≠ pós-parto; a
> tradução adiciona ruído; o conjunto de violência é pequeno (273) → mantém-se o **fallback por
> keywords** quando o modelo ML está ausente. **Descartado:** `singhsandk/domestic-violence-dataset-prep`
> (14 linhas, formato Q&A — inadequado para treino).

## 5. Caso de exemplo sintético (gerado por você)
Script Python que monta uma **paciente fictícia** combinando 1 amostra de cada modalidade num caso coerente (ex.: cicatriz com alerta + PA alta + áudio com sinal de risco + laudo com proteinúria). É o que torna a **fusão demonstrável** — ver [Fase 1, Tarefa 1.6](01-fase1-dados.md).
