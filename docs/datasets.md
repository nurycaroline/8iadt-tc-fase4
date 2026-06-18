# Datasets Recomendados

> Baixe **apenas amostras** para o mini-dataset. Registre origem e licença de cada um (vai para o relatório). Não versione os dados.

## 1. Vídeo cirúrgico (visão computacional)

> **Sem Roboflow e sem anotação manual.** Todos os datasets abaixo **já vêm anotados**; basta um **script automático** para converter as máscaras de segmentação para o formato YOLO (`.txt` com polígonos normalizados).

### Já anotados (recomendados)
| Dataset | O que é | Por que usar | Link |
|---------|---------|--------------|------|
| **CholecSeg8k** ⭐ | 8.080 frames com **segmentação pixel-a-pixel** em 13 classes, incluindo **Blood (sangue)**, Grasper e L-hook (instrumentos) e anatomia | **Melhor escolha** — já traz sangramento + instrumentos + anatomia anotados; pronto no Hugging Face/Kaggle (CC BY-NC-SA 4.0) | https://huggingface.co/datasets/minwoosun/CholecSeg8k |
| **SurgBlood** | 5.330 frames de 95 vídeos com **regiões e pontos de sangramento** anotados por cirurgiões (CVPR 2026) | Específico para **hemorragia** intraoperatória | https://github.com/PJLallen/SurgBlood |
| **AutoLaparo** | Histerectomia laparoscópica com máscaras de segmentação pixel-a-pixel | Anatomia **ginecológica** (útero/instrumentos) já anotada | https://autolaparo.github.io/ |

### Complementares (também anotados)
| Dataset | O que é | Por que usar | Link |
|---------|---------|--------------|------|
| **CholecT50** | Reconhecimento de ações/ferramentas, bounding boxes nas pontas | Presença de ferramentas e fases | https://github.com/CAMMA-public/cholect50 |
| **SurgToolLoc** | Localização de ferramentas com bounding boxes no teste | Medir acurácia do YOLO | https://surgtoolloc.grand-challenge.org/data/ |

**Estratégia para "sangramento" (sem anotar à mão):**
1. **Sangue:** usar a classe **Blood** do CholecSeg8k (ou as máscaras do SurgBlood) — já anotada.
2. **Anatomia ginecológica:** usar as máscaras do AutoLaparo (útero/instrumentos).
3. **Conversão:** script automático máscara → YOLO-Seg; treinar YOLOv8-Seg com as classes combinadas.
4. **Fusão lógica** com sinais vitais (a IA não decide tudo sozinha).

> **Domínio:** CholecSeg8k/SurgBlood são de cirurgia hepatobiliar (vesícula/fígado). Como o **sangue tem aparência semelhante** entre cirurgias laparoscópicas, combiná-los com AutoLaparo (ginecológico) é uma decisão razoável — documente no relatório.
> Os datasets **MICCAI EndoVis** também são padrão-ouro e já vêm com ground truth de alta qualidade.

## 2. Sinais vitais (séries temporais)

| Dataset | O que é | Por que usar |
|---------|---------|--------------|
| **CTU-CHB Intrapartum Cardiotocography** | 552 registros de CTG no parto (FHR + UC) | Dataset definitivo de monitoramento fetal; padrões de risco classificados |
| **VitalDB** | Sinais vitais multiparâmetro de alta resolução em cirurgia (PA invasiva/não invasiva, FC, oximetria) | Simular paciente na mesa de operação; alimentar a queda de PA |
| **OB-1 Fetal ECG Database** | ECG fetal do couro cabeludo + atividade uterina, batimento a batimento | Alternativa/complemento ao CTG, foco em variabilidade de FHR |
| **Term-Preterm EHG (Tocograma)** | Eletroisterograma + tocograma | Prever contrações anômalas / trabalho de parto prematuro |

> Buscar no **PhysioNet** e no **UCI Machine Learning Repository** (ex.: *Cardiotocography Data Set*).

## 3. Áudio (consultas)

| Fonte | Uso |
|-------|-----|
| **Áudios sintéticos (TTS)** | Gerar falas de consulta nas categorias-alvo (rápido e sem questão de privacidade) |
| **RAVDESS / bases de fala emocional** | Treinar/validar classificação de emoção/sentimento |
| **Gravações próprias (consentimento simulado)** | Demonstração realista no vídeo |

> Para transcrição: **Whisper** (local) ou **Azure Speech-to-Text**. Para sentimento: **Azure Text Analytics**.

## 4. Mock de sincronização (gerado por você)
Script Python que produz uma série de **PA materna** alinhada ao vídeo, com **queda no segundo do sangramento**. É o que torna a **fusão demonstrável** — ver [Fase 1, Tarefa 1.4](01-fase1-dados.md).
