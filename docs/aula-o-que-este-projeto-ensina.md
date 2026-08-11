# Aula completa: tudo que este projeto ensina a um dev fullstack

> Artigo/aula baseado no projeto **IA Multimodal para Saúde da Mulher (8IADT — Tech Challenge Fase 4)**.
> Público-alvo: dev fullstack que quer entender **como IA de verdade entra em um produto** — dos modelos ao deploy, passando por dados, arquitetura, testes e LGPD.
> Tudo o que está aqui é verificável no repositório: código, métricas versionadas (`ai-service/models/**/metrics.json`) e documentação (`docs/`).

---

## Índice

1. [O problema e o produto](#1-o-problema-e-o-produto)
2. [Arquitetura: por que 3 serviços e por que essa stack](#2-arquitetura-por-que-3-serviços-e-por-que-essa-stack)
3. [Fundamentos de ML que o projeto ensina na prática](#3-fundamentos-de-ml-que-o-projeto-ensina-na-prática)
4. [Modalidade 1 — Visão computacional: YOLOv8 na cicatriz](#4-modalidade-1--visão-computacional-yolov8-na-cicatriz)
5. [Modalidade 2 — Dados tabulares: Random Forest nos sinais vitais](#5-modalidade-2--dados-tabulares-random-forest-nos-sinais-vitais)
6. [Modalidade 3 — NLP clássico: TF-IDF + Regressão Logística no texto](#6-modalidade-3--nlp-clássico-tf-idf--regressão-logística-no-texto)
7. [Modalidade 4 — Áudio: Whisper + MFCC (análise dupla)](#7-modalidade-4--áudio-whisper--mfcc-análise-dupla)
8. [Fusão multimodal: regras explicáveis em vez de ML](#8-fusão-multimodal-regras-explicáveis-em-vez-de-ml)
9. [Base de treinamento: dados públicos, sintéticos e LGPD](#9-base-de-treinamento-dados-públicos-sintéticos-e-lgpd)
10. [Engenharia fullstack em torno da IA](#10-engenharia-fullstack-em-torno-da-ia)
11. [MLOps "de bolso": reprodutibilidade, versionamento e degradação graciosa](#11-mlops-de-bolso-reprodutibilidade-versionamento-e-degradação-graciosa)
12. [Privacidade e segurança como código (LGPD)](#12-privacidade-e-segurança-como-código-lgpd)
13. [Limitações conhecidas — e o que elas ensinam](#13-limitações-conhecidas--e-o-que-elas-ensinam)
14. [Checklist do que você aprendeu + exercícios](#14-checklist-do-que-você-aprendeu--exercícios)

---

## 1. O problema e o produto

No pós-parto, a mãe volta para casa e o acompanhamento clínico enfraquece. Sinais de risco — infecção da cicatriz da cesárea, pré-eclâmpsia, depressão pós-parto, violência doméstica — aparecem aos poucos e ficam **espalhados** entre sistemas e pessoas diferentes. Quando alguém finalmente cruza os dados, a complicação já aconteceu.

A solução é um "cérebro" que **junta as modalidades da mesma paciente** e alerta cedo:

- A paciente envia, de casa: **foto/vídeo da cicatriz**, **áudio** (relato), **sinais vitais** (pressão, batimentos, glicemia, temperatura) e **texto clínico** (laudos/evoluções).
- Cada modalidade passa por um modelo de IA especializado.
- Um motor de **fusão** combina as evidências em um escore único de risco: `BAIXO` / `MEDIO` / `ALTO`.
- Risco `MEDIO`/`ALTO` dispara um **alerta em tempo real** para a equipe e gera um **relatório automático**.

**Primeira lição de produto:** o valor não está em nenhum modelo individual — está no **cruzamento**. Um relato de cansaço isolado é vago; cansaço + cicatriz alterada + pressão subindo é um quadro. É por isso que o projeto mede explicitamente o *ganho da fusão* sobre cada modalidade isolada (seção 8).

> ⚠️ É uma solução **acadêmica de apoio à decisão** — não diagnostica nem substitui avaliação médica. Esse disclaimer não é burocracia: define o escopo ético do sistema e aparece no README, no relatório técnico e nos relatórios gerados.

---

## 2. Arquitetura: por que 3 serviços e por que essa stack

```
frontend/    # Dashboard (React + Vite + TypeScript) — monitoramento e alerta ao vivo
backend/     # Orquestrador (Node.js + Express) — upload, storage, SQLite, alertas
ai-service/  # Motor de IA (Python + FastAPI) — modelos, fusão, relatório, métricas
```

Fluxo: dashboard → `POST /analisar` (Node) → storage (local ou Azure Blob) → `POST /inferencia` (FastAPI) → modelos por modalidade → fusão → relatório → Node persiste no SQLite → Socket.IO emite `alerta` se `MEDIO`/`ALTO`.

### Por que Python para IA e Node para orquestração?

Essa é a decisão de arquitetura mais instrutiva do projeto (documentada em `docs/arquitetura.md`):

| Motivo | Explicação |
|---|---|
| **Ecossistema** | YOLO (Ultralytics), PyTorch, scikit-learn, Whisper, librosa e WeasyPrint são maduros em Python e inexistentes ou imaturos em JS. Não é preferência — é disponibilidade de ferramenta. |
| **Escala independente** | Inferência é CPU/GPU-intensiva; API de upload é IO-intensiva. Separando, escala-se só o `ai-service` sem replicar a API. |
| **Substituição de modelo** | Trocar YOLOv8 por outro detector não toca uma linha do backend — o contrato HTTP (`POST /inferencia`) é a fronteira. |
| **Isolamento de falha** | Se a IA quebra, o erro fica no log Python, rastreável por `case_id`; o Node devolve 502/504 e continua vivo. |

Node ficou com o que Node faz bem: upload multipart, autenticação, SQLite, WebSocket (Socket.IO) e integração com Azure Blob. **Lição fullstack:** a fronteira entre serviços deve seguir a fronteira entre *naturezas de trabalho* (IO vs. computação), não entre "camadas" arbitrárias.

### O contrato de API como espinha dorsal

Toda a comunicação Node ↔ Python passa por **um único endpoint com contrato documentado** (`docs/contrato-api.md`):

- **Request:** `case_id`, `paciente` (mínimo, sem nome — ver seção 12), URLs dos artefatos por modalidade, `texto_clinico`. Todos os campos de modalidade são **opcionais** — o pipeline analisa o que existir.
- **Response:** `risco_detectado` (`BAIXO|MEDIO|ALTO`), `evidencias` por modalidade, `mensagem_alerta`, `relatorio_url`.

O contrato é validado dos dois lados: **Zod** no Node, **Pydantic** no FastAPI. Quando o contrato é a fonte de verdade, frontend, backend e IA evoluem em paralelo sem quebrar uns aos outros.

### Evolução incremental (não big design up front)

O frontend **não nasceu React**: a Fase 3 entregou um cliente HTML mínimo servido pelo próprio backend (que ainda existe como fallback em `backend/public/`), e só a Fase 5 trouxe o dashboard React. Entregou-se o alerta em tempo real cedo com UI feia, e a UI bonita depois. Essa ordem — **valor primeiro, polimento depois** — é visível no histórico de fases (`PLANO_DE_DESENVOLVIMENTO.md`).

---

## 3. Fundamentos de ML que o projeto ensina na prática

Antes de mergulhar nos modelos, o vocabulário mínimo — cada conceito aparece concretamente no código:

- **Aprendizado supervisionado:** todos os modelos do projeto aprendem de exemplos rotulados (imagem → `ferida_ok`/`ferida_alerta`; vitais → `low`/`mid`/`high`; texto → depressão sim/não).
- **Features:** a representação numérica da entrada. Nos vitais são as colunas do CSV; no texto é o vetor TF-IDF; no áudio são 40 números derivados de MFCC. Grande parte do trabalho de ML é decidir a representação, não o algoritmo.
- **Split treino/teste:** o modelo é avaliado em dados que **nunca viu** (holdout de 25% em todos os treinos do projeto, com `stratify` para manter a proporção das classes). Avaliar no dado de treino gera número bonito e inútil.
- **Métricas além de acurácia:**
  - **Precisão** = dos alertas que dei, quantos eram reais? (mede falso positivo)
  - **Recall** = dos casos reais, quantos eu peguei? (mede falso negativo)
  - **F1** = média harmônica das duas. **F1 macro** = média do F1 de cada classe, sem deixar a classe majoritária mascarar a minoritária.
  - Em saúde, **recall é rei**: deixar passar uma pré-eclâmpsia custa mais que um alerta a mais.
- **Classes desbalanceadas:** quase todo treino do projeto usa `class_weight="balanced"` — o modelo penaliza mais o erro na classe rara. Sem isso, um classificador que responde sempre "normal" teria acurácia alta e recall zero na classe que importa.
- **Seed (`random_state=42`):** todo split e todo modelo com aleatoriedade fixa a semente. Sem isso, cada execução dá um número diferente e nenhuma métrica é comparável.

Com esse vocabulário, cada modalidade abaixo vira um estudo de caso.

---

## 4. Modalidade 1 — Visão computacional: YOLOv8 na cicatriz

**Tarefa:** olhar a foto da cicatriz da cesárea e dizer se há sinal de infecção.

### Como o modelo funciona

**YOLO** ("You Only Look Once") é um detector de objetos: recebe uma imagem e devolve **caixas delimitadoras (bounding boxes)** com classe e confiança, em **uma única passada** da rede convolucional (por isso é rápido — diferente de abordagens antigas que rodavam um classificador em milhares de regiões candidatas). O projeto usa **YOLOv8n** ("nano"), a menor variante da família — ~6 MB de pesos, treinável em minutos numa GPU T4 gratuita do Colab.

**Por que YOLOv8n e não uma rede maior ou um classificador puro?**
- A biblioteca Ultralytics torna o **fine-tuning trivial**: um `data.yaml` apontando para as imagens + labels e uma chamada `model.train()`.
- Fine-tuning = pegar pesos pré-treinados no COCO (milhões de imagens genéricas) e **especializar** nas ~730 imagens de feridas. Treinar do zero com 730 imagens seria inviável; com transfer learning, funciona.
- Nano porque o dataset é pequeno — modelo maior só decoraria (overfitting).
- Exporta para **ONNX** (`app/cicatriz/exportar.py`), formato aberto de inferência que desacopla do PyTorch.

### O hack instrutivo: detecção como proxy de classificação

O dataset (AZH Wound, público) tem imagens de feridas classificadas em pastas `N` (sem alerta) e `S` (com alerta), **sem anotação de caixas**. O script `scripts/data_prep/cicatriz_yolo.py` resolve com um truque honesto: gera **1 bounding box cobrindo a imagem inteira** por foto, com a classe da pasta. O YOLO vira, na prática, um classificador — mas mantém a infraestrutura de detecção para quando houver anotações reais. A limitação está **documentada** (não é cicatriz de cesárea específica, é ferida genérica).

### Treinamento e resultado

- Treino local para smoke test (`python -m app.cicatriz.treino`, 20 épocas, 320px) e treino "de verdade" no Colab (`ai-service/notebooks/cicatriz_yolo_colab.ipynb`): 100 épocas configuradas, 640px, `patience=25` → **early stopping parou na época 41** (melhor época ~16). Early stopping = parar quando a métrica de validação para de melhorar, evitando overfitting e desperdício de GPU.
- Métricas (`ai-service/models/cicatriz/metrics.json`): **mAP@50 = 0,995**, precisão 0,992, recall 0,987.
- **mAP@50** = mean Average Precision com IoU ≥ 0,5; a métrica padrão de detecção. 0,995 é altíssimo — e deve gerar desconfiança saudável: com boxes cobrindo a imagem inteira e classes visualmente distintas, a tarefa é mais fácil do que o número sugere.

### Inferência em produção

`app/cicatriz/inferencia.py`: carrega `best.pt` → `predict` → pega a caixa de maior confiança → mapeia para o contrato (`ferida_alerta` → `sinal_infeccao`) **somente se confiança ≥ 0,7** (`CONFIANCA_MINIMA` em `app/limiares.py`). Abaixo disso, devolve `nenhum`. **Lição:** o threshold de decisão é uma escolha de produto (tolerância a falso positivo), separada do modelo.

---

## 5. Modalidade 2 — Dados tabulares: Random Forest nos sinais vitais

**Tarefa:** dado um CSV com pressão arterial, glicemia, temperatura e frequência cardíaca, classificar risco materno em `low`/`mid`/`high`.

### Como o modelo funciona

**Random Forest** = comitê de árvores de decisão. Cada árvore aprende regras do tipo "se PA sistólica > 132 e glicemia > 8, então high", treinada num subconjunto aleatório dos dados e das features; a predição final é o voto da maioria. Por que é a escolha padrão para tabular:

- **Robusto sem tuning**: funciona bem "out of the box", não exige normalização de features.
- **Explicável**: expõe importância de features — dá para mostrar ao médico *por que* o modelo achou risco.
- **Barato**: treina em segundos, roda em CPU.

Configuração do projeto (`app/sinais_vitais/treino.py`): `RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")`, 6 features (`Age`, `SystolicBP`, `DiastolicBP`, `BS`, `BodyTemp`, `HeartRate`).

**Lição de escolha de modelo:** para dados tabulares pequenos, deep learning perde de Random Forest / gradient boosting em quase tudo — custo, explicabilidade e frequentemente acurácia. Rede neural não é sinônimo de IA.

### O resultado mediano — e por que ele é a parte mais educativa

Dataset: **Maternal Health Risk (UCI, id 863, CC BY 4.0)** → 451 amostras após limpeza → split 338/113. Métricas (`models/sinais_vitais/metrics.json`):

| Métrica | Valor |
|---|---|
| Acurácia | **0,646** |
| F1 macro | **0,624** |
| F1 classe `high` | 0,79 |
| F1 classe `mid` | **0,38** |
| F1 classe `low` | 0,69 |

64,6% de acurácia parece ruim — e a decomposição por classe conta a história real: o modelo distingue bem extremos (`high` 0,79), mas a classe intermediária `mid` é ambígua por natureza (0,38). Três lições:

1. **Sempre olhe a métrica por classe.** A média esconde exatamente a classe que importa.
2. **Números medianos honestos > números maquiados.** O relatório técnico reporta 0,646 sem constrangimento e explica o porquê.
3. **A fusão compensa modelos fracos.** Um vitals `mid` sozinho vale pouco; `mid` + cicatriz alterada vira alerta `ALTO` (seção 8). O sistema é melhor que a soma das partes — por design.

### Dados sintéticos para reforçar a classe fraca

A Fase 5 gerou **80 amostras sintéticas de pré-eclâmpsia** (`scripts/data_prep/preeclampsia_sintetico.py`, `numpy.default_rng(42)`) e mediu o efeito **antes/depois** (`models/sinais_vitais/comparacao_preeclampsia.json`): F1 macro 0,624 → **0,675** (+0,051). A prática exemplar aqui não é o ganho — é **versionar a comparação**: augmentação de dados é hipótese, e hipótese se mede.

### Inferência em produção

`app/sinais_vitais/inferencia.py`: o pipeline escolhe a linha do CSV com **pior pressão sistólica** (o pior momento importa mais que a média), roda o modelo e aplica uma **regra clínica dura por cima**: PA ≥ **140/90** → tipo `hipertensao`, independentemente do que o modelo diga. Limiar clínico consagrado não se terceiriza a um modelo com F1 0,62. **Regras e ML convivem** — essa hibridização aparece em todas as modalidades do projeto.

---

## 6. Modalidade 3 — NLP clássico: TF-IDF + Regressão Logística no texto

**Tarefa:** ler texto clínico em português (evolução, relato transcrito) e detectar (a) achados de infecção/complicação, (b) indícios de **depressão**, (c) indícios de **violência**.

### Como o modelo funciona

Nada de LLM. O pipeline (`app/texto/treino.py`) é NLP clássico dos anos 2000, e funciona:

1. **TF-IDF** (`TfidfVectorizer(ngram_range=(1,2), max_features=5000, sublinear_tf=True)`): converte texto em vetor numérico onde cada dimensão é uma palavra ou bigrama, com peso alto para termos frequentes *neste* documento mas raros *no corpus geral*. "Tristeza" pesa muito num texto de triagem de depressão; "paciente" (que aparece em tudo) pesa quase nada. Bigramas capturam negação e contexto local ("sem dor" ≠ "dor").
2. **Regressão Logística** (`LogisticRegression(class_weight="balanced", C=0.5)`): classificador linear que aprende um peso por termo e devolve **probabilidade** — essencial, porque a fusão usa a probabilidade contra um limiar (0,6), não só a classe. `C=0.5` aumenta a regularização (encolhe pesos), reduzindo overfitting num dataset pequeno.

**Por que não um LLM?** Roda offline em CPU em milissegundos, sem custo por chamada, sem enviar dado sensível de saúde para API externa (LGPD!), e é auditável: dá para inspecionar exatamente quais termos puxaram a decisão. Para classificação binária com domínio restrito, TF-IDF+LogReg continua sendo um baseline fortíssimo. **Lição:** comece pelo modelo mais simples que resolve; complexidade se justifica com medição, não com hype.

### Resultados — incluindo o "perfeito demais"

| Modelo | Dataset | n | F1 macro |
|---|---|---|---|
| Depressão | `depressao_pt.csv` (400: 200/200) | 300 treino / 100 teste | **0,930** |
| Violência | `violencia_pt.csv` (546: 273/273) | 409 treino / 137 teste | **1,000** ⚠️ |

O F1 = 1,0 da violência é a lição mais valiosa do projeto sobre avaliação. Matriz de confusão `[[69,0],[0,68]]` — zero erros. A documentação registra o diagnóstico: **vazamento de fonte** (*source leakage*). Os positivos vieram de um dataset (posts sobre violência doméstica) e os negativos de outra fonte; o modelo provavelmente aprendeu a distinguir **as fontes** (estilo, vocabulário, tamanho), não o fenômeno. O número não generaliza — e o time **escreveu isso no relatório em vez de comemorar**.

> **Regra prática que você leva para sempre:** métrica perfeita não é motivo de festa, é gatilho de auditoria. Procure vazamento entre treino/teste, vazamento de fonte, ou feature que "entrega" o rótulo.

### Defesa em profundidade na inferência

`app/texto/nlp.py` combina três camadas:

1. **Keywords determinísticas** para achados clínicos objetivos (`febre`, `pus`, `proteinuria`, `cefaleia`...) — explicáveis, sem falso negativo por criatividade do modelo.
2. **ML** (os dois `.joblib`) para depressão/violência — generaliza além do léxico fixo.
3. **Fallback:** se o ML disser "negativo" mas as keywords dispararem, as keywords **sobem o alerta** (rede de segurança); se os pesos nem existirem no disco (checkout sem Git LFS), só keywords operam e o sistema continua funcionando.

---

## 7. Modalidade 4 — Áudio: Whisper + MFCC (análise dupla)

**Tarefa:** a partir de um áudio da paciente, detectar violência e sofrimento psicológico.

### O insight de design: violência mora em dois lugares

A Fase 8 (`docs/11-fase8-audio-texto-unificado.md`) percebeu que analisar só a **transcrição** perde informação: gritos, choro e tom alterado desaparecem quando o áudio vira texto. A solução é uma **análise dupla**:

```
áudio ─┬─► trilha ACÚSTICA: MFCC → LogReg  (violência no SOM: grito, tom)
       └─► trilha SEMÂNTICA: Whisper → transcrição → mesmo motor NLP da seção 6
                                                     (depressão + violência no CONTEÚDO)
```

### Trilha semântica: Whisper (ASR)

**Whisper** (OpenAI, open source) é um transformer encoder-decoder treinado em ~680 mil horas de áudio multilíngue — funciona bem em português sem fine-tuning. O projeto usa o modelo **`base`** (compromisso velocidade/qualidade em CPU), **rodando localmente**: nenhum áudio de paciente sai da máquina (decisão de LGPD, não só de custo — o caminho via Azure Speech existe como opção, mas o padrão é local).

A jogada arquitetural elegante: a transcrição entra **no mesmo pipeline NLP do texto digitado** (`texto/nlp.analisar`). Áudio e texto foram **unificados** — um motor a menos para manter, e métricas comparáveis entre modalidades.

### Trilha acústica: MFCC + Regressão Logística

**MFCC** (Mel-Frequency Cepstral Coefficients) é a representação clássica de áudio para ML: descreve o **envelope espectral** do som numa escala (mel) que imita a percepção humana de frequências. O projeto (`app/audio/features.py`) extrai 20 coeficientes via `librosa`, resume cada um por **média + desvio padrão** ao longo do tempo → vetor fixo de **40 números** por áudio, de qualquer duração. Sobre isso: `StandardScaler` + `LogisticRegression`.

Repare no padrão: **imagem virou detecção, texto virou TF-IDF, áudio virou 40 floats** — todo problema de ML é primeiro um problema de representação; depois disso, os classificadores são quase intercambiáveis.

- Dataset: `Hemg/audio-based-violence-dataset` (HF) → 400 WAVs versionados com `manifest.csv` (200 neutro / 200 violência).
- Métricas (300/100): **F1 macro 0,94**, matriz `[[46,4],[2,48]]`.

### Inferência e fusão dos dois canais

`app/audio/classificacao.py` devolve uma evidência unificada: `acustico` (rótulo + confiança), `transcricao`, e o resultado do NLP sobre a transcrição. Violência é sinalizada se **qualquer** trilha disparar (OR lógico) — coerente com o custo assimétrico: falso negativo de violência é inaceitável.

---

## 8. Fusão multimodal: regras explicáveis em vez de ML

A decisão mais contraintuitiva (e mais defensável) do projeto: a fusão **não é um modelo de ML**. É um **motor de regras** legível em `ai-service/app/fusao.py`, com thresholds centralizados em `app/limiares.py`.

### Por que regras?

1. **Não havia dado para aprender a fusão.** Treinar um combinador exigiria centenas de casos multimodais *da mesma paciente* rotulados — que não existem (os datasets de cada modalidade são independentes). ML sem dado é ficção.
2. **Explicabilidade clínica:** o médico precisa saber *por que* o alerta disparou. "Infecção na cicatriz + febre no relato → risco de infecção puerperal" é uma frase; um peso aprendido não é.
3. **Testável unitariamente:** cada regra tem teste (`pytest`); um modelo de fusão exigiria dataset de avaliação próprio.

O princípio documentado: **"a IA produz evidências; a regra decide."** Modelos ficam no perímetro (percepção), a lógica de negócio crítica fica determinística no centro.

### As regras (resumo)

O risco final é o **máximo** entre os níveis acionados:

| Combinação de evidências | Risco | Gatilho |
|---|---|---|
| Infecção na cicatriz **+** (vitais de risco **ou** febre/dor no texto) | **ALTO** | `infeccao_puerperal` |
| Vitais de risco **+** complicação no texto (ou tipo `pre_eclampsia`) | **ALTO** | `pre_eclampsia` |
| Violência: acústica ≥ 0,7 **ou** texto ≥ 0,6 — **mesmo isolada** | **ALTO** | `violencia` |
| Depressão no texto ≥ 0,6 | **MEDIO** | `desconforto_psicologico` |
| Infecção na cicatriz sozinha / vitais de risco sozinhos / texto isolado | **MEDIO** (teto) | contexto |
| Nada relevante | **BAIXO** | — |

Detalhes que valem estudo:

- **Evidência isolada tem teto `MEDIO`** — exceto violência, que fura o teto por decisão ética explícita. Thresholds diferentes por canal (0,7 acústico, 0,6 texto) refletem confianças diferentes nos modelos.
- **Corroboração eleva:** duas evidências `MEDIO` compatíveis viram `ALTO`. É a materialização do valor multimodal.
- Os limiares moram em **um arquivo só** (`limiares.py`) — ajustar a sensibilidade do sistema é um diff de uma linha, revisável em PR.

### Medindo o ganho da fusão

O projeto não afirma que fusão é melhor — **mede** (`ai-service/models/metricas_fusao.json`, sobre 6 casos sintéticos rotulados):

| Cenário | Precisão | Recall | Falsos positivos |
|---|---|---|---|
| Só vídeo | 0,50 | 0,33 | 0,33 |
| Só vitais | 1,00 | 0,67 | 0,00 |
| Só áudio/texto | 0,67 | 0,67 | 0,33 |
| **Fusão** | **1,00** | **1,00** | **0,00** |

n=6 é minúsculo (limitação documentada), mas a **metodologia** é o que se leva: para justificar uma feature, construa a comparação com e sem ela, sobre os mesmos casos, e versione o resultado.

---

## 9. Base de treinamento: dados públicos, sintéticos e LGPD

Dados de saúde são **sensíveis** pela LGPD (Lei 13.709/2018). A estratégia do projeto: **nenhum dado real de paciente, nunca** — só datasets públicos e sintéticos, todos **versionados no Git** para que qualquer pessoa rode e retreine sem baixar nada.

### Inventário por modalidade

| Modalidade | Dataset | Origem | Tamanho usado |
|---|---|---|---|
| Cicatriz | AZH Wound | Público/acadêmico (GitHub `uwm-bigdata`) | ~730 imagens (pastas N/S) |
| Sinais vitais | Maternal Health Risk | UCI id 863, **CC BY 4.0** | 451 linhas limpas |
| Vitais (reforço) | Pré-eclâmpsia sintética | Gerado no repo (`seed=42`) | 80 amostras |
| Texto depressão | `ShreyaR/DepressionDetection` | Hugging Face (EN) | 400 (200/200) traduzidas |
| Texto violência | `Spiderman01/Domestic_violence...` + negativos | Hugging Face (EN) | 546 (273/273) |
| Áudio violência | `Hemg/audio-based-violence-dataset` | Hugging Face | 400 WAVs (200/200) |
| Casos de fusão | `caso_baixo/medio/alto.json` | Sintéticos próprios | 3 + 6 rotulados |

### Técnicas de engenharia de dados que o projeto demonstra

- **Tradução offline como pipeline de dados:** não existia dataset de depressão em PT-BR, então os textos EN foram traduzidos com **Argos Translate** (offline, MIT, CPU) — sem enviar dados a APIs. O ruído da tradução automática é assumido como limitação documentada.
- **Composição de dataset:** o dataset de violência foi montado juntando positivos de uma fonte e negativos de outra — o que causou o vazamento de fonte da seção 6. Aprende-se dos dois lados: a técnica *e* o seu risco.
- **Manifest como contrato de dados:** os 400 áudios vêm com `manifest.csv` (arquivo → rótulo). Dataset sem manifest é pasta de arquivos; com manifest é artefato reproduzível.
- **Casos sintéticos onde a realidade não existe:** os datasets por modalidade são de *pessoas diferentes* — não há "mesma paciente" multimodal real. Os casos `caso_*.json` costuram 1 amostra de cada modalidade numa paciente fictícia, viabilizando demo e avaliação da fusão.
- **Licença é requisito de engenharia:** o projeto registra que os datasets do HF **não especificam licença** e trata isso como risco documentado — não como detalhe ignorável.
- **Conformidade automatizada:** o job `conformidade` do CI roda `scripts/check_conformidade.py`, que **quebra o build** se aparecer `.env` versionado, chave/certificado (`*.key`, `*.pem`), ou arquivo em `data/` fora de uma allowlist. Política de privacidade que não está no CI é intenção; no CI é garantia.

---

## 10. Engenharia fullstack em torno da IA

A parte que mais fala com o seu dia a dia: o modelo é ~20% do sistema. O resto é engenharia que você já conhece — aplicada com alguns detalhes finos.

### Backend (Node/Express) — `backend/src/`

- **App factory com injeção de dependências:** `app.js` recebe `db`, `storage`, `inferir` e o emissor de alertas como parâmetros. Resultado: os testes (Jest + supertest) montam o app com fakes, sem rede nem banco real. É o padrão que torna Express testável de verdade.
- **Pipeline do `POST /analisar`** (`rotas/analisar.js`): valida paciente → upload **multipart em memória** (multer, 50 MB, **MIME allowlist por campo** — vídeo/imagem, áudio, CSV) → salva no storage → monta o payload do contrato → chama a IA → persiste → audita → emite alerta.
- **Mapeamento de erro upstream:** falha HTTP da IA → **502 Bad Gateway**; timeout/rede → **504 Gateway Timeout**. Timeout de **120 s** (`AI_TIMEOUT_MS`) porque inferência multimodal é lenta — o timeout default de 30 s de um client HTTP derrubaria requisições legítimas. **Não há retry**: reprocessar o mesmo caso é caro e a operação não é idempotente por padrão; melhor falhar explícito.
- **SQLite via `better-sqlite3`** (síncrono, WAL, `foreign_keys=ON`): 3 tabelas — `pacientes`, `casos` (com `resultado_json` completo e FK `ON DELETE CASCADE`), `auditoria`. Para um sistema de um nó, SQLite elimina um container inteiro de infraestrutura. **Lição:** dimensione a persistência para o problema real, não para o problema imaginado.
- **Storage atrás de interface:** `storage/index.js` seleciona `local` (disco) ou `azure` (Blob + URLs **SAS** com expiração de 60 min) por env var, com fallback para local se a Azure falhar. O resto do código não sabe qual backend está ativo. É o padrão *ports & adapters* no menor tamanho útil.

### Tempo real (Socket.IO)

- Servidor: `realtime/alertas.js` emite `io.emit('alerta', payload)` **só** para risco `MEDIO`/`ALTO`. O payload carrega o mínimo (case_id, risco, mensagem, link do relatório, primeiro nome).
- Socket.IO em vez de WebSocket cru ou SSE: reconexão automática e fallback para polling de graça — exatamente o que um alerta clínico precisa.
- Detalhe sutil de bootstrap: o emissor é injetado **indiretamente** no app para quebrar a dependência circular app ↔ servidor HTTP ↔ io.

### Frontend (React + Vite + TS) — `frontend/src/`

- **TanStack React Query** para todo estado de servidor — cache, revalidação e estados de loading/erro sem Redux. Estado local só para forms e UI.
- **Alertas ao vivo:** `socket.ts` mantém um singleton do socket; o hook `useAlertas` escuta o evento e guarda o último alerta + histórico (50). O `AlertaBanner` fica no layout, e o Dashboard **refaz o fetch dos casos quando chega um alerta** — push notifica, pull sincroniza. Padrão simples e à prova de mensagens perdidas.
- **Chamadas relativas + proxy:** `api.ts` chama `/casos`, `/analisar` sem host; o Vite faz proxy em dev (incluindo `/socket.io` com upgrade de WebSocket) e o nginx em produção. Zero configuração de CORS no caminho feliz, mesma origem sempre.

### Testes em três stacks

| Camada | Runner | O que cobre |
|---|---|---|
| `ai-service` + `scripts` | pytest (**119 testes** na revisão final) | fusão regra a regra, pipeline, API, relatório com fallback de PDF, conformidade, e2e em processo |
| `backend` | Jest + supertest + socket.io-client (**32**) | rotas, auth, MIME, mapeamento 502/504, **emissão de alerta via socket real**, auditoria, retenção |
| `frontend` | Vitest + Testing Library (**7**) | api, AlertaBanner, RiscoBadge |

Ponto alto: os testes de backend sobem um servidor Socket.IO real e **assertam que o evento `alerta` chega no cliente**. Tempo real também se testa.

### Docker, nginx e CI

- `docker-compose.yml`: `ai-service` (8000) com **healthcheck HTTP**, `backend` (3000) com `depends_on: condition: service_healthy` — o backend só sobe quando a IA responde `/health`; `frontend` (nginx, 8080) faz proxy de API e WebSocket.
- **TLS como overlay opt-in:** `docker-compose.tls.yml` sobrepõe o compose base com nginx em 8443, redirect HTTP→HTTPS, TLS 1.2/1.3 e HSTS, com certificado dev gerado por script. A demo local continua simples; o hardening é um `-f` a mais.
- **CI (GitHub Actions)** com 4 jobs paralelos: `conformidade` (LGPD), `python` (ruff + pytest), `node` (eslint + jest), `frontend` (eslint + vitest + build). Cada stack falha independente — o diagnóstico é imediato.

---

## 11. MLOps "de bolso": reprodutibilidade, versionamento e degradação graciosa

Sem Kubeflow, sem feature store — e ainda assim as práticas essenciais de MLOps estão todas presentes, em versão mínima:

1. **Pesos no Git via LFS:** `.gitattributes` rastreia `*.pt`, `*.joblib`, `*.onnx`. O repositório clona leve (pointers de ~130 bytes) e `git lfs pull` traz os binários. Modelo é artefato versionado como código.
2. **Métricas versionadas ao lado dos pesos:** cada modelo tem seu `metrics.json` commitado (F1, matriz de confusão, tamanhos de split, tag do algoritmo tipo `"tfidf+logreg"`). O relatório técnico segue a regra: **só cita métrica que está em artefato versionado**. Nada de "deu 95% na minha máquina".
3. **Treino reproduzível por CLI:** cada modalidade retreina com um comando (`python -m app.sinais_vitais.treino`, `app.texto.treino`, ...), com seeds fixas e dados versionados. Qualquer membro do time regenera qualquer artefato.
4. **Lazy loading + cache de modelos:** `app/ml_utils.py` carrega `.joblib` sob demanda e cacheia em dict; se o arquivo for um pointer LFS não baixado ou estiver corrompido, devolve `None` e o sistema cai para keywords.
5. **Degradação graciosa como decisão de design (DD10):** sem pesos YOLO → modalidade cicatriz reporta indisponível; sem Whisper → transcrição vazia; sem `.joblib` → keywords. O pipeline **nunca quebra por artefato ausente** — degrada e segue. O CI roda a suíte inteira **sem** `git lfs pull` justamente para provar isso. O e2e documenta os dois mundos: `caso_alto` com pesos → `ALTO` (infecção puerperal); sem ultralytics → `MEDIO` (vitais+texto seguram o caso).
6. **Comparações A/B versionadas:** o reforço sintético de pré-eclâmpsia tem seu `comparacao_preeclampsia.json` com antes/depois. Toda mudança de dado ou modelo deveria deixar um rastro assim.

---

## 12. Privacidade e segurança como código (LGPD)

A Fase 7 transformou LGPD de seção de documento em **controles executáveis** — todos **opt-in por variável de ambiente**, para que a demo local continue rodando sem credenciais:

| Controle | Implementação | Princípio LGPD |
|---|---|---|
| Só dados sintéticos/públicos | Allowlist + job `conformidade` no CI | Não tratar dado real sem base legal |
| Pseudonimização | `case_id` UUID opaco; a IA recebe `pacienteMinimo` **sem o nome** (`seguranca/pseudonimizacao.js`) | Minimização: o modelo não precisa saber quem é |
| Autenticação | `API_KEY` → exige `x-api-key` (backend e ai-service); sem a env, demo aberta; `/health` e `/ready` sempre públicos | Controle de acesso |
| Auditoria | Tabela `auditoria` (quem, qual ação, qual caso, quando) — **sem conteúdo clínico** | Rastreabilidade sem criar novo dado sensível |
| Retenção | `RETENTION_DAYS` + `npm run retencao` remove casos e artefatos expirados (e audita a remoção) | Dado não vive para sempre |
| TLS na borda | Overlay compose + nginx, HSTS | Proteção em trânsito |
| Segredos fora do código | `.env` git-ignorado; Azure Key Vault opcional carregado **antes** da config | Nunca commitar credencial |
| Hardening HTTP | helmet, CORS allowlist, filtro de MIME no upload, `client_max_body_size` | Redução de superfície |
| Acesso temporário a artefatos | URLs SAS do Blob com expiração de 60 min | Link vazado expira |

Duas lições transferíveis para qualquer sistema com dados sensíveis:

- **Minimização é arquitetura:** a decisão de não enviar o nome da paciente ao serviço de IA foi tomada *no design do contrato*, não num review de compliance depois.
- **Compliance que não está no CI regride.** O job `conformidade` é o que impede o estagiário de commitar um `.env` com chave numa sexta-feira.

---

## 13. Limitações conhecidas — e o que elas ensinam

O projeto mantém uma lista explícita de limitações — e essa honestidade é, em si, uma prática a copiar:

| Limitação documentada | Lição |
|---|---|
| AZH Wound tem feridas genéricas, não cicatriz de cesárea; bbox é proxy | *Domain shift*: métrica alta em dado proxy não garante desempenho no domínio real. Nomeie seus proxies. |
| F1 = 1,0 em violência-texto por vazamento de fonte | Resultado perfeito → auditoria, não comemoração. Monte positivos e negativos da **mesma fonte**. |
| Textos de depressão vêm de Reddit/Twitter EN traduzidos, não do puerpério | O dado que você tem raramente é o dado que você quer. A distância dever ser declarada. |
| Ganho da fusão medido com n=6 | Amostra pequena prova metodologia, não eficácia. Diga o n sempre. |
| Licenças dos datasets HF não especificadas | Dados sem licença clara são passivo jurídico — registre o risco. |
| F1 0,38 na classe `mid` dos vitais | Classes intermediárias são as difíceis; a média macro esconde isso. |
| Deploy Azure real bloqueado (conta); fallback local cobre tudo | Desenhe para a nuvem, rode local: abstrações de storage/segredos pagam-se aqui. |
| PDF (weasyprint) instável no macOS → fallback HTML | Dependência nativa instável exige plano B no código, não no wiki. |

---

## 14. Checklist do que você aprendeu + exercícios

### Você agora sabe explicar

**IA/ML**
- [ ] O que é aprendizado supervisionado, features, split treino/teste, e por que `stratify` e `random_state` importam
- [ ] Precisão vs. recall vs. F1 (macro), e por que recall domina em saúde
- [ ] Como YOLO detecta objetos, o que é fine-tuning/transfer learning, early stopping e mAP@50
- [ ] Por que Random Forest é o padrão para tabular pequeno, e como ler métricas por classe
- [ ] Como TF-IDF + Regressão Logística transformam texto em decisão com probabilidade
- [ ] O que Whisper faz (ASR) e o que MFCCs representam
- [ ] O que é data/source leakage e como um F1 = 1,0 o denuncia
- [ ] Quando fusão por regras vence fusão aprendida (dados escassos + necessidade de explicação)

**Engenharia**
- [ ] Separar serviços por natureza de trabalho (IO vs. computação) com contrato HTTP validado nos dois lados (Zod/Pydantic)
- [ ] App factory + injeção de dependências para testar Express de verdade
- [ ] Timeouts dimensionados para inferência, mapeamento 502/504, e por que *não* fazer retry cego
- [ ] Storage atrás de interface com fallback (local/Azure Blob + SAS)
- [ ] Push (Socket.IO) + pull (refetch do React Query) para tempo real robusto
- [ ] Healthcheck + `depends_on: service_healthy` no compose; TLS como overlay opt-in
- [ ] Git LFS para pesos, `metrics.json` versionado, treino por CLI com seed — MLOps mínimo viável
- [ ] Degradação graciosa: o sistema funciona (pior) sem qualquer modelo individual
- [ ] LGPD como código: pseudonimização no contrato, auditoria, retenção, conformidade no CI

### Exercícios propostos (do mais fácil ao mais difícil)

1. **Rodar e observar:** `docker compose up --build`, envie os 3 casos sintéticos (`data/casos/`) e acompanhe o alerta chegar via Socket.IO no dashboard. Depois derrube o `ai-service` e observe o 502/504.
2. **Mexer num limiar:** mude `CONFIANCA_TEXTO` de 0,6 para 0,4 em `ai-service/app/limiares.py`, rode `pytest` e veja quais testes de fusão quebram — e por quê.
3. **Auditar o vazamento:** retreine o modelo de violência-texto (`python -m app.texto.treino`) com um split em que os negativos venham da mesma fonte dos positivos e compare o F1.
4. **Estender a fusão:** adicione uma regra nova (ex.: temperatura ≥ 38 °C no CSV + achado de dor no texto → gatilho próprio), com teste unitário e atualização do `contrato-api.md`.
5. **Trocar um modelo mantendo o contrato:** substitua o classificador de depressão por outro (ex.: `LinearSVC` calibrado) sem tocar no backend — prove com os testes que o contrato segurou a troca.
6. **Medir de verdade:** amplie os casos rotulados de fusão de 6 para 30 e regenere `metricas_fusao.json` (`python -m app.metricas_fusao`). O ganho da fusão sobrevive?

---

## Fechamento

O que este projeto ensina, acima de tudo, é que **um produto de IA é um sistema fullstack com alguns arquivos `.joblib` dentro**. As decisões que definem sua qualidade são as mesmas que você já toma — contratos, fronteiras de serviço, testes, CI, tratamento de erro — mais três hábitos novos:

1. **Trate dados como código:** versionados, com manifest, licença, seed e script de geração.
2. **Trate métricas como artefatos:** commitadas, comparáveis, citáveis — e audite as perfeitas.
3. **Trate o modelo como dependência não confiável:** com threshold explícito, fallback determinístico e regras de negócio que não se terceirizam.

O resto — YOLO, Whisper, TF-IDF — são ferramentas que você agora sabe quando (e quando não) usar.

---

*Referências no repositório: [`docs/arquitetura.md`](arquitetura.md) · [`docs/contrato-api.md`](contrato-api.md) · [`docs/datasets.md`](datasets.md) · [`docs/relatorio-tecnico.md`](relatorio-tecnico.md) · [`docs/11-fase8-audio-texto-unificado.md`](11-fase8-audio-texto-unificado.md) · [`docs/07-privacidade-e-seguranca.md`](07-privacidade-e-seguranca.md) · [`PLANO_DE_DESENVOLVIMENTO.md`](../PLANO_DE_DESENVOLVIMENTO.md)*
