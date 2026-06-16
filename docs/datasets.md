# Datasets Recomendados

> Baixe **apenas amostras** para o mini-dataset. Registre origem e licença de cada um (vai para o relatório). Não versione os dados.

## 1. Vídeo cirúrgico (visão computacional)

| Dataset | O que é | Por que usar | Link |
|---------|---------|--------------|------|
| **AutoLaparo** | Histerectomia laparoscópica com máscaras de segmentação pixel-a-pixel | **Melhor escolha inicial** — já traz anatomia/instrumentos anotados | https://autolaparo.github.io/ |
| **CholecT50** | Reconhecimento de ações/ferramentas cirúrgicas, bounding boxes nas pontas | Treinar YOLO em presença de ferramentas e fases | https://github.com/CAMMA-public/cholect50 |
| **SurgToolLoc** | Localização de ferramentas com bounding boxes no teste | Medir acurácia do YOLO | https://surgtoolloc.grand-challenge.org/data/ |

**Estratégia para "sangramento" (anomalia de estado, não objeto fixo):**
1. Segmentar anatomia (útero/ovário) com YOLOv8-Seg usando AutoLaparo.
2. Treinar classificador leve "presença de sangue" por frame (dataset de sangue é raro).
3. Fusão lógica com sinais vitais (não deixar a IA decidir tudo sozinha).

> Os datasets **MICCAI EndoVis** são o padrão-ouro acadêmico e já vêm com ground truth de alta qualidade, economizando anotação manual.

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
