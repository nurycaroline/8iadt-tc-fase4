# 00 — Visão Geral e Escopo

## 1. Problema

A rede hospitalar quer **monitorar continuamente pacientes de saúde da mulher** usando **dados multimodais (áudio, vídeo, texto/sinais)** para identificar **sinais precoces de risco** e **alertar a equipe em tempo real**.

## 2. Escopo escolhido pelo grupo

**Cenário clínico central:** vigilância de **complicação/sangramento em cirurgia ginecológica-obstétrica**, com a paciente também monitorada por **sinais vitais** e tendo passado por uma **consulta** (áudio) de triagem.

Esse recorte foi escolhido porque:
- Permite uma **fusão multimodal real e demonstrável** (o que mais pontua).
- Tem **datasets públicos disponíveis** para as 3 modalidades.
- Casa com um **único evento de risco bem definido** (hemorragia + instabilidade), evitando tentar "resolver a cirurgia inteira".

## 3. Modalidades implementadas

| Modalidade | Entrada | Modelo | Saída |
|-----------|---------|--------|-------|
| **Vídeo** | Frames de vídeo cirúrgico | YOLOv8 (detecção/segmentação) | `sangramento`, anatomia, instrumentos + confiança |
| **Sinais vitais** | Série temporal (PA, FHR, UC) | Random Forest / Isolation Forest | normal / suspeito / anômalo |
| **Áudio** | Áudio de consulta | ASR (transcrição) + classificador | indicadores de ansiedade/depressão/violência |
| **Texto/NLP** | Laudos, prescrições hormonais, evolução clínica | NLP (palavras-chave / sentimento / regras) | achados de risco no texto clínico |
| **Fusão** | Saídas das 4 acima | Motor de regras | risco `BAIXO/MÉDIO/ALTO` + alerta + relatório |

> A inclusão do **texto** fecha a tríade "áudio, vídeo e texto" citada no enunciado e reforça a multimodalidade. Pode ser um módulo enxuto (regras + análise de sentimento), mas precisa existir.

## 4. Mapeamento dos requisitos do PDF

### Funcionalidades (mín. 2 — atendemos 3)
- [x] Analisar **vídeos** (cirurgias) para padrões anômalos / sangramento.
- [x] Processar **gravações de voz** (depressão pós-parto, ansiedade, violência).
- [x] Detectar **anomalias em sinais vitais** (PA em gestantes, batimentos fetais).
- [x] Integrar com **nuvem (Azure)**.

### Objetivos (mín. 3 — atendemos 5)
- [x] Detectar precocemente riscos em saúde materna e ginecológica.
- [x] Identificar sinais de violência doméstica/abuso (via áudio + texto).
- [x] Monitorar bem-estar psicológico feminino (via áudio).
- [x] Usar serviços em nuvem para ampliar capacidade de processamento.
- [x] Aplicar detecção de anomalias em tempo real.

### Entregas técnicas obrigatórias
- [x] **Análise de Vídeo** com YOLOv8 customizado → Fase 2 e 3.
- [x] **Análise de Áudio** especializada → Fase 2 (módulo de áudio).
- [x] **Relatórios automáticos especializados** → [doc dedicado](06-relatorios-automaticos.md).
- [x] **Privacidade e segurança (LGPD)** → [doc dedicado](07-privacidade-e-seguranca.md).

## 5. Decisões de projeto

| # | Decisão | Justificativa |
|---|---------|---------------|
| D1 | Incluir **módulo de áudio** mesmo que enxuto | PDF lista áudio como entrega técnica obrigatória |
| D2 | Arquitetura **Node (orquestrador) + Python (IA)** | Isolamento de responsabilidades; pontua em engenharia de software |
| D3 | **Mini-dataset primeiro** (5/5/5) | Validar pipeline ponta-a-ponta antes de escalar |
| D4 | **Mock de sincronização** vídeo↔sinais vitais | Datasets reais não vêm sincronizados; gerar dados sintéticos alinhados ao evento |
| D5 | Fusão por **motor de regras** (não end-to-end) | Explicável, demonstrável e suficiente para o desafio |
| D6 | **Azure Blob + App Service/Functions** | Requisito de nuvem do desafio |
| D7 | Incluir **módulo de texto/NLP** | Fecha a tríade "áudio, vídeo e texto" do enunciado |
| D8 | **Medir o ganho da fusão** (vs. modalidade única) | Prova o valor da multimodalidade — o diferencial avaliado |
| D9 | Alerta em **tempo real** (WebSocket/SSE) + **relatório automático** | Requisitos explícitos do PDF |

## 6. Riscos e mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Dataset de sangramento raro | Vídeo fraco | Usar segmentação de anatomia/instrumentos (AutoLaparo) + classificador "presença de sangue" |
| Sincronizar vídeo e sinais vitais | Fusão não demonstrável | Gerar **dados sintéticos** de PA alinhados ao momento do evento (D4) |
| Custo/limite da conta Azure | Deploy travado | Usar tier gratuito; ter fallback rodando localmente para o vídeo de demo |
| Dados sensíveis no Git | Violação de privacidade | `.gitignore` em `data/`, credenciais em `.env`, nada de paciente real versionado |
| Tempo de treino do YOLO | Atraso | Usar YOLOv8n/s + mini-dataset + Colab/GPU |

## 7. Definição de "pronto" do projeto

O projeto está pronto quando:
1. As 4 modalidades produzem saída individual com métricas.
2. O motor de fusão gera o JSON de risco padronizado (ver [contrato-api](contrato-api.md)) **e há métrica do ganho da fusão**.
3. O pipeline roda ponta-a-ponta (upload → IA → alerta em tempo real + relatório automático) — idealmente na Azure.
4. Privacidade/LGPD tratada (ver [doc dedicado](07-privacidade-e-seguranca.md)).
5. Relatório técnico e vídeo de até 15 min estão prontos (ver [Fase 4](04-fase4-entregaveis.md)).
