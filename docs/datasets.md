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

## 2. Vídeo — fisioterapia / recuperação (pose)

> Objetivo: usar **YOLOv8-pose** para acompanhar os exercícios de reabilitação no pós-parto.

| Dataset | O que é | Por que usar | Link |
|---------|---------|--------------|------|
| **IntelliRehabDS** ⭐ | Movimentos de 29 sujeitos (pacientes e controles) via Kinect, com rótulo correto/incorreto | Bom para classificar execução do exercício | https://zenodo.org/records/4610859 |
| **REHAB24-6** | Vídeo RGB + esqueleto 2D/3D, repetições corretas/incorretas | Alternativa com rótulo de qualidade | (buscar "REHAB24-6 dataset") |

## 3. Sinais vitais (tabular / dados clínicos)

> Objetivo: classificar **risco materno / pré-eclâmpsia** a partir de PA, FC, glicemia e temperatura.

| Dataset | O que é | Por que usar | Link |
|---------|---------|--------------|------|
| **Maternal Health Risk (UCI)** ⭐ | 1.013 registros (PA sistólica/diastólica, glicemia, temperatura, FC) com nível de risco `low/mid/high`; **CC BY 4.0** | Base aberta e direta para Random Forest | https://archive.ics.uci.edu/dataset/863/maternal+health+risk |
| **Preeclampsia (sintético, HF)** | ~21 mil amostras focadas em pré-eclâmpsia (fatores de risco com odds ratios da literatura) | Mais volume/foco em pré-eclâmpsia | https://huggingface.co/datasets/electricsheepafrica/africa-synth-maternal-health-preeclampsia-dataset-all |
| **Maternal health pregnancy (sintético, HF)** | 30 mil registros de pré-natal (PA, hemoglobina, glicemia, proteinúria, desfecho) | Cenários variados de risco | https://huggingface.co/datasets/LinderStacy-1/maternal-health-pregnancy |

## 4. Áudio (consultas / relatos)

> Objetivo: detectar **depressão pós-parto / ansiedade / violência** na fala.

| Fonte | O que é | Uso | Link |
|-------|---------|-----|------|
| **Androids Corpus** ⭐ | 228 gravações (saudáveis vs. com depressão), leitura e fala espontânea; uso acadêmico | Treinar/validar classificação de depressão na fala | https://github.com/androidscorpus/data |
| **DEPAC** | Fala rotulada com escalas de depressão (PHQ-9) e ansiedade (GAD-7) | Mais tarefas de fala e rótulos | https://aclanthology.org/2022.clpsych-1.1.pdf |
| **Áudios sintéticos (TTS)** | Falas de consulta nas categorias-alvo geradas por TTS | Rápido e sem questão de privacidade (demo) | — |
| **Gravações próprias (consentimento simulado)** | Falas curtas gravadas pelo grupo | Demonstração realista no vídeo | — |

> **Limitação honesta:** não existe base só de depressão **pós-parto**. Usa-se base de depressão/ansiedade **geral** + áudios sintéticos. Explique isso no relatório.
> Para transcrição: **Whisper** (local) ou **Azure Speech-to-Text**. Para sentimento: **Azure Text Analytics**.

## 5. Texto clínico (NLP)

> Objetivo: achar sinais de risco em laudos/exames/evolução (ex.: PA alta, proteinúria, febre/dor na cicatriz).

| Fonte | Uso |
|-------|-----|
| **Laudos/evolução sintéticos** | Gerar ~5 documentos com achados normais e de risco (rápido e sem privacidade) |
| **Campos textuais dos datasets de pré-natal (HF)** | Reaproveitar descrições/desfechos como texto clínico |

## 6. Caso de exemplo sintético (gerado por você)
Script Python que monta uma **paciente fictícia** combinando 1 amostra de cada modalidade num caso coerente (ex.: cicatriz com alerta + PA alta + áudio com sinal de risco + laudo com proteinúria). É o que torna a **fusão demonstrável** — ver [Fase 1, Tarefa 1.6](01-fase1-dados.md).
