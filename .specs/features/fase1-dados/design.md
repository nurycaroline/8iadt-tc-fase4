# Fase 1 — Aquisição e Preparação de Dados — Design

> Como vamos construir o que o [`spec.md`](spec.md) descreve. Alinha-se à estrutura de repositório de
> [`PLANO_DE_DESENVOLVIMENTO.md`](../../../PLANO_DE_DESENVOLVIMENTO.md) (§7) e às boas práticas de
> [`docs/qualidade-testes-ci.md`](../../../docs/qualidade-testes-ci.md).

## 1. Visão geral

A Fase 1 é composta por **scripts de preparação de dados** (não há serviço/API ainda). Cada modalidade
tem um script independente que segue o mesmo contrato interno: `baixar amostra → limpar/converter →
gravar em data/<modalidade>/ → registrar metadados`. Um script final (caso sintético) consome as saídas
das modalidades e monta os pacotes de demonstração.

```
            scripts/data_prep/
                  │
  ┌───────┬───────┼─────────┬─────────┐
  ▼       ▼       ▼         ▼         ▼
vitais  cicatriz fisio    audio     texto      (independentes, paralelizáveis)
  │       │       │         │         │
  └───────┴───────┴────┬────┴─────────┘
                       ▼
              caso_sintetico.py  →  data/casos/<caso>.json  (consome 1 amostra de cada)
```

**Princípio guia (do plano):** "Se rodar com 5, roda com 500." Mini-dataset primeiro, ponta-a-ponta.

## 2. Stack e dependências

Versões devem ser fixadas pela **última estável** no momento da implementação (princípio do `AGENTS.md`);
abaixo está apenas o conjunto de pacotes, sem inventar números de versão.

| Finalidade                       | Pacote/Ferramenta            | Usado em            |
| -------------------------------- | ---------------------------- | ------------------- |
| Manipulação tabular              | `pandas`                     | sinais vitais       |
| Download de datasets             | `requests` / `ucimlrepo`     | vitais, cicatriz    |
| Conversão/leitura de imagem      | `opencv-python`, `Pillow`    | cicatriz, fisio     |
| Formato/visualização YOLO        | `ultralytics`, `pyyaml`      | cicatriz, fisio     |
| Extração de frames de vídeo      | `opencv-python` / `ffmpeg`   | cicatriz, fisio     |
| Transcrição de áudio (ASR)       | `openai-whisper` (local)     | áudio               |
| Geração de áudio sintético (TTS) | TTS local/Azure (opcional)   | áudio               |
| Testes                           | `pytest`                     | funções puras       |
| Lint                             | `ruff`                       | todos os scripts    |

> Linguagem: **Python 3.13** (última estável é 3.14, mas o `openai-whisper` só suporta até 3.13 — em
> 3.14 a instalação quebra por `numba`/`triton`; ver DD8). As dependências de preparação ficam em
> `scripts/requirements-data.txt` (separadas das do `ai-service/` da Fase 2).

## 3. Estrutura de pastas (a criar)

```
scripts/
├── requirements-data.txt          # deps da preparação de dados
├── data_prep/
│   ├── __init__.py
│   ├── common.py                  # utilidades: paths, download seguro, escrita idempotente, logging
│   ├── sinais_vitais.py           # F1D-04, F1D-05
│   ├── cicatriz_yolo.py           # F1D-06, F1D-07, F1D-08
│   ├── fisioterapia_pose.py       # F1D-14
│   ├── audio_transcrever.py       # F1D-11, F1D-12
│   ├── texto_clinico.py           # F1D-13
│   └── caso_sintetico.py          # F1D-09, F1D-10
└── tests/
    ├── test_sinais_vitais.py      # limpeza/feature/outlier
    ├── test_cicatriz_yolo.py      # normalização de bbox / data.yaml
    └── test_caso_sintetico.py     # schema do contrato + variantes

data/                              # IGNORADO pelo Git (exceto .gitkeep/metadados permitidos)
├── README.md                      # como obter os dados + origem/licença (versionado)
├── sinais_vitais/
├── video_cicatriz/
│   ├── images/
│   ├── labels/                    # .txt formato YOLO
│   └── data.yaml
├── video_fisioterapia/
├── audio/
│   └── metadados.json
├── texto_clinico/
│   └── rotulos.json
└── casos/                         # JSONs do caso sintético
```

## 4. Componentes

### 4.1 `common.py` (fundação)

Funções compartilhadas para manter os scripts pequenos e idempotentes:

- `data_dir(modalidade) -> Path` — resolve caminhos sob `data/` (cria se faltar).
- `download(url, dest, *, sample_only=True)` — download seguro: grava em arquivo temporário e renomeia
  ao final (evita arquivos parciais); falha com mensagem clara e instrução de obtenção manual.
- `write_json(path, obj)` / `write_csv(df, path)` — escrita idempotente.
- `get_logger(case_id=None)` — logging estruturado (JSON) com `case_id`, consistente com a
  observabilidade pedida na Fase de qualidade.

### 4.2 Sinais vitais (`sinais_vitais.py`)

- Baixa o **Maternal Health Risk (UCI)** (via `ucimlrepo` ou CSV direto).
- `limpar(df) -> df`: descarta outliers fisiologicamente implausíveis (faixas definidas para PA
  sistólica/diastólica, FC, glicemia, temperatura), padroniza unidades, trata faltantes.
- `selecionar_amostras(df, n=5) -> df`: pelo menos 5 amostras rotuladas `low/mid/high`.
- Saída: `data/sinais_vitais/maternal_clean.csv` + 5 amostras destacadas para o caso sintético.
- **Funções puras testáveis:** `limpar`, detecção de outlier, normalização de features.

### 4.3 Cicatriz → YOLO (`cicatriz_yolo.py`)

- Baixa **uma amostra** do **AZH Wound**.
- `converter_para_yolo(anotacao, img_size) -> labels`: gera `.txt` normalizado (bbox/polígono) com
  classes `ferida_ok` (0) e `ferida_alerta` (1). Caso a fonte traga máscara/segmentação, derivar bbox.
- Gera `data.yaml` (classes + paths) no formato Ultralytics.
- `visualizar(img, labels) -> arquivo`: salva imagem com anotações sobrepostas (OpenCV).
- **Funções puras testáveis:** normalização de coordenadas e geração do `data.yaml`.

### 4.4 Fisioterapia → pose (`fisioterapia_pose.py`) — P3

- Baixa amostras do **UCO PhyRehab** ou **IntelliRehabDS**.
- Reaproveita keypoints fornecidos quando existirem; senão extrai frames e prepara para YOLOv8-pose.
- Rotula repetições `correto`/`incorreto`.

### 4.5 Áudio (`audio_transcrever.py`)

- Coleta/gera 5 áudios (Androids/DEPAC para depressão/ansiedade + TTS/gravações para as demais categorias).
- Transcreve com **Whisper** (local) — interface trocável por Azure Speech-to-Text via env var.
- Grava `data/audio/metadados.json`: `[{arquivo, transcricao, categoria}]`
  com categorias do contrato (`neutro`/`ansiedade`/`depressao_pos_parto`/`violencia`/`fadiga`).

### 4.6 Texto clínico (`texto_clinico.py`)

- Gera/reúne ~5 documentos em texto simples (achados normais e de risco).
- `data/texto_clinico/rotulos.json`: `[{arquivo, achado, trechos}]` com `achado` em
  `complicacao`/`sinal_infeccao`/`neutro`.

### 4.7 Caso sintético (`caso_sintetico.py`) — a "cola"

- Consome 1 amostra de cada modalidade disponível e monta um **pacote de caso** no formato do objeto de
  **requisição** do [contrato de API](../../../docs/contrato-api.md): `case_id`, `paciente`,
  `video_cicatriz_url`/ref, `video_fisioterapia_url`/ref, `dados_vitais.csv_url`/ref, `audio_url`/ref,
  `texto_clinico`.
- Gera 3 variantes coerentes:
  - **BAIXO** — tudo dentro do esperado.
  - **MÉDIO** — apenas 1 modalidade alterada (risco isolado).
  - **ALTO** — múltiplas modalidades alteradas (ex.: cicatriz com alerta + PA alta).
- Modalidades ausentes → campo omitido (opcional no contrato).
- **Funções puras testáveis:** montagem do JSON e conformidade com o schema/variantes.

## 5. Decisões de design

| #  | Decisão                                                        | Justificativa                                                       |
| -- | ------------------------------------------------------------- | ------------------------------------------------------------------- |
| DD1 | Scripts em `scripts/data_prep/`, não em `ai-service/`         | Fase 1 é só dados; mantém o serviço de IA (Fase 2) limpo            |
| DD2 | `requirements-data.txt` separado                              | Evita inflar a imagem do `ai-service`; deps de prep são efêmeras    |
| DD3 | Download em arquivo temporário + rename                       | Garante idempotência e evita arquivos parciais corrompidos          |
| DD4 | Caso sintético segue o **objeto de requisição** do contrato  | A saída já alimenta a Fase 3 (fusão) sem retrabalho                 |
| DD5 | Testar apenas **funções puras** (limpeza, conversão, builder) | Download/IO dependem de rede; o valor está na lógica determinística |
| DD6 | Reuso de keypoints fornecidos (fisio) quando existirem        | Evita anotação manual pesada (política do projeto)                  |
| DD7 | `data/` ignorado; só `data/README.md` versionado             | LGPD/privacidade — nada de dados reais/sensíveis no Git             |
| DD8 | **Python 3.13** (não 3.14, a última estável)                  | `openai-whisper` (T7) não suporta 3.14 (`numba`/`triton`); 3.13 é o teto compatível com todas as deps |

## 6. Estratégia de testes (entra em cada tarefa)

Conforme `docs/qualidade-testes-ci.md` (pytest + ruff):

| Camada                              | Tipo de teste | O que cobre                                          |
| ----------------------------------- | ------------- | ---------------------------------------------------- |
| `sinais_vitais.limpar`/outliers     | unit          | entrada com outliers → linhas descartadas esperadas  |
| `cicatriz_yolo` normalização/yaml   | unit          | coords conhecidas → `.txt` normalizado; `data.yaml`  |
| `caso_sintetico` builder            | unit          | JSON conforme contrato; 3 variantes; campo opcional  |
| `common` (download/escrita)         | none          | depende de rede/IO — validado manualmente            |

- **Gate quick:** `ruff check scripts && pytest scripts/tests -q`.
- Funções de IO/rede não recebem teste unitário (DD5); são validadas pelo "Independent Test" do spec.

## 7. Riscos (herdados do escopo) e mitigação local

| Risco                                            | Mitigação na Fase 1                                                |
| ------------------------------------------------ | ----------------------------------------------------------------- |
| URL/licença do dataset muda ou exige login       | `download()` falha com instrução de obtenção manual no `data/README.md` |
| AZH Wound não é específico de cesárea            | Documentar limitação no README/relatório; usar classe `ferida_alerta`   |
| Não há base de depressão **pós-parto**           | Usar bases gerais + TTS; registrar limitação                       |
| Juntar pessoas diferentes na fusão               | Caso sintético deixa explícito que no uso real é a mesma paciente  |
| Versionar dados sensíveis                        | `.gitignore` em `data/` validado por teste manual (`git status`)   |
