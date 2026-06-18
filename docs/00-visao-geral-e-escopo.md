# 00 — Visão Geral e Escopo

## 1. Problema

A rede hospitalar quer **monitorar continuamente pacientes de saúde da mulher** usando **dados multimodais (áudio, vídeo, texto/sinais)** para identificar **sinais precoces de risco** e **alertar a equipe em tempo real**.

**A dor concreta:** no pós-parto a mãe vai para casa e o acompanhamento enfraquece. Sinais de risco (infecção da cicatriz, pré-eclâmpsia, depressão pós-parto, violência) surgem aos poucos e ficam **espalhados** em sistemas e pessoas diferentes. Quando alguém cruza tudo, a complicação já aconteceu.

## 2. Escopo escolhido pelo grupo

**Cenário clínico central:** **acompanhamento contínuo da mulher no pós-parto** (e gestação avançada). A paciente, em casa, **envia periodicamente** seus dados (relato em áudio, foto/vídeo da cicatriz e dos exercícios, sinais vitais e laudos), e o sistema **cruza tudo** e alerta a equipe diante de **sinais precoces de risco**.

Esse recorte foi escolhido porque:
- Casa com o **"monitorar continuamente"** e **"sinal precoce"** do enunciado (a paciente manda dados ao longo do tempo).
- Permite uma **fusão multimodal real e demonstrável** (o que mais pontua).
- Tem **datasets públicos disponíveis** para as 4 modalidades.
- Cobre **riscos-alvo bem definidos** do puerpério: infecção, pré-eclâmpsia, saúde mental e violência.

## 3. Modalidades implementadas

| Modalidade | Entrada | Modelo | Saída |
|-----------|---------|--------|-------|
| **Vídeo (cicatriz)** | Foto/vídeo da cicatriz da cesárea | YOLOv8 (detecção) | sinal de **infecção** (vermelhidão, secreção, deiscência) + confiança |
| **Vídeo (fisioterapia)** | Vídeo do exercício de reabilitação | YOLOv8-pose | qualidade/evolução do movimento (recuperação física) |
| **Sinais vitais** | Dados clínicos tabulares (PA, FC, glicemia, temperatura) | Random Forest / Isolation Forest | normal / risco materno / pré-eclâmpsia |
| **Áudio** | Áudio de consulta/relato | ASR (transcrição) + classificador | indicadores de depressão pós-parto/ansiedade/violência |
| **Texto/NLP** | Laudos, exames, evolução clínica | NLP (palavras-chave / sentimento / regras) | achados de risco no texto clínico |
| **Fusão** | Saídas das modalidades acima | Motor de regras | risco `BAIXO/MÉDIO/ALTO` + alerta + relatório |

> A inclusão do **texto** fecha a tríade "áudio, vídeo e texto" citada no enunciado e reforça a multimodalidade. Pode ser um módulo enxuto (regras + análise de sentimento), mas precisa existir.

> **Sobre o vídeo:** as duas aplicações (cicatriz e fisioterapia) usam a mesma família YOLOv8 — a primeira por **detecção** (sinal de infecção), a segunda por **estimativa de pose** (movimento). Ambas são coisas que a mãe grava **em casa**, reforçando o "monitoramento contínuo".

## 4. Mapeamento dos requisitos do PDF

### Funcionalidades (mín. 2 — atendemos 3)
- [x] Analisar **vídeos** (cicatriz / fisioterapia) para padrões anômalos / sinal de infecção.
- [x] Processar **gravações de voz** (depressão pós-parto, ansiedade, violência).
- [x] Detectar **anomalias em sinais vitais** (pressão/risco materno, pré-eclâmpsia).
- [x] Integrar com **nuvem (Azure)**.

### Objetivos (mín. 3 — atendemos 5)
- [x] Detectar precocemente riscos em saúde materna e no puerpério.
- [x] Identificar sinais de violência doméstica/abuso (via áudio + texto).
- [x] Monitorar bem-estar psicológico feminino (via áudio).
- [x] Usar serviços em nuvem para ampliar capacidade de processamento.
- [x] Aplicar detecção de anomalias em tempo real.

### Entregas técnicas obrigatórias
- [x] **Análise de Vídeo** com YOLOv8 customizado → Fase 2 e 3.
- [x] **Análise de Áudio** especializada → Fase 2 (módulo de áudio).
- [x] **Relatórios automáticos especializados** → [doc dedicado](06-relatorios-automaticos.md).
- [x] **Privacidade e segurança (LGPD)** → [doc dedicado](07-privacidade-e-seguranca.md).

## 5. O que liga os dados (coerência)

| Cola | O que é |
|------|---------|
| **Paciente + caso** | Cada paciente cadastrada recebe **um conjunto de dados**; tudo é da **mesma pessoa, no mesmo episódio**. |
| **Linha do tempo do pós-parto** | Cada modalidade observa um ângulo do **mesmo acompanhamento**: relato (áudio/texto), corpo (cicatriz/fisioterapia), números (sinais vitais). |
| **Motor de fusão** | Cruza as evidências e gera **um** nível de risco. |

> **Treino x uso real.** Os **datasets públicos** servem **só para treinar** cada modelo (são de pessoas diferentes — tudo bem). O **"mesmo paciente"** só existe no **uso real**. Para **demonstrar** a fusão sem paciente real, montamos um **"caso de exemplo" sintético** juntando amostras (ver [Fase 1](01-fase1-dados.md)).

## 6. Decisões de projeto

| # | Decisão | Justificativa |
|---|---------|---------------|
| D1 | Cenário central = **acompanhamento no pós-parto** (não cirurgia) | "Monitorar continuamente" + "sinal precoce" do enunciado |
| D2 | Arquitetura **Node (orquestrador) + Python (IA)** | Isolamento de responsabilidades; pontua em engenharia de software |
| D3 | **Mini-dataset primeiro** (5 por modalidade) | Validar pipeline ponta-a-ponta antes de escalar |
| D4 | **Caso de exemplo sintético** para a demo | Datasets reais são de pessoas diferentes; montar 1 paciente fictícia juntando amostras |
| D5 | Fusão por **motor de regras** (não end-to-end) | Explicável, demonstrável e suficiente para o desafio |
| D6 | **Azure Blob + App Service/Functions** | Requisito de nuvem do desafio |
| D7 | Incluir **módulo de texto/NLP** | Fecha a tríade "áudio, vídeo e texto" do enunciado |
| D8 | **Medir o ganho da fusão** (vs. modalidade única) | Prova o valor da multimodalidade — o diferencial avaliado |
| D9 | Alerta em **tempo real** (WebSocket/SSE) + **relatório automático** | Requisitos explícitos do PDF |
| D10 | **Vídeo com dois usos** (cicatriz por detecção + fisioterapia por pose) | Aproveita YOLOv8 em dois sinais relevantes do puerpério |

## 7. Riscos e mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Dataset de cicatriz infectada é limitado | Vídeo fraco | Usar AZH Wound (feridas cirúrgicas) + classe "ferida com sinal de alerta"; documentar limitação |
| Áudio específico de depressão **pós-parto** não existe | Áudio menos fiel | Usar bases de depressão/ansiedade geral (Androids, DEPAC) + áudios sintéticos; explicar no relatório |
| Juntar dados de pessoas diferentes na fusão | Fusão "artificial" na demo | Montar **caso de exemplo sintético** por paciente (D4); deixar claro que no uso real é da mesma pessoa |
| Custo/limite da conta Azure | Deploy travado | Usar tier gratuito; ter fallback rodando localmente para o vídeo de demo |
| Dados sensíveis no Git | Violação de privacidade | `.gitignore` em `data/`, credenciais em `.env`, nada de paciente real versionado |
| Tempo de treino do YOLO | Atraso | Usar YOLOv8n/s + mini-dataset + Colab/GPU |

## 8. Definição de "pronto" do projeto

O projeto está pronto quando:
1. As 4 modalidades produzem saída individual com métricas.
2. O motor de fusão gera o JSON de risco padronizado (ver [contrato-api](contrato-api.md)) **e há métrica do ganho da fusão**.
3. O pipeline roda ponta-a-ponta (upload → IA → alerta em tempo real + relatório automático) — idealmente na Azure.
4. Privacidade/LGPD tratada (ver [doc dedicado](07-privacidade-e-seguranca.md)).
5. Relatório técnico e vídeo de até 15 min estão prontos (ver [Fase 4](04-fase4-entregaveis.md)).
