# `data/` — Mini-dataset da Fase 1

> ⚠️ **Privacidade/LGPD:** este diretório é **ignorado pelo Git** (ver `.gitignore`). Versionamos
> apenas a estrutura de pastas (`.gitkeep`), este README e pequenos metadados textuais
> (`audio/metadados.json`, `texto_clinico/rotulos.json`, `casos/*.json`, `video_cicatriz/data.yaml`).
> **Nunca** faça commit de dados brutos, imagens, áudios, vídeos ou dados reais de pacientes.

Os dados são obtidos rodando os scripts de `scripts/data_prep/`. Baixe **apenas amostras** — nunca os
datasets inteiros (política do projeto). Origem e licença de cada base estão na tabela abaixo (para o
relatório técnico).

## Layout

```
data/
├── sinais_vitais/      # CSV limpo do Maternal Health Risk
├── video_cicatriz/
│   ├── images/         # amostras de imagem (ignoradas)
│   ├── labels/         # rótulos no formato YOLOv8 (.txt)
│   └── data.yaml       # classes + paths (versionado)
├── video_fisioterapia/ # amostras de exercícios + keypoints
├── audio/
│   └── metadados.json  # {arquivo, transcricao, categoria}
├── texto_clinico/
│   └── rotulos.json    # {arquivo, achado, trechos}
└── casos/              # casos de exemplo sintéticos (JSON)
```

## Como obter os dados

Pré-requisitos: `pip install -r scripts/requirements-data.txt`.

**Baixar/gerar tudo de uma vez (recomendado):**

```bash
python -m scripts.data_prep
```

O orquestrador roda todas as modalidades (best-effort) e imprime um resumo. Modalidades **manuais**
(áudio e fisioterapia) aparecem como `FALHOU` quando os arquivos ainda não foram adicionados — isso é
esperado; adicione as amostras e rode de novo.

Ou rode uma modalidade isolada:

| Modalidade        | Script                                          | Obtenção  | Observação                          |
| ----------------- | ----------------------------------------------- | --------- | ----------------------------------- |
| Sinais vitais     | `python -m scripts.data_prep.sinais_vitais`     | **auto**  | Baixa via `ucimlrepo` (UCI id 863)  |
| Cicatriz (YOLO)   | `python -m scripts.data_prep.cicatriz_yolo`     | **auto**  | Baixa `Test.zip` do AZH Wound (~4 MB), extrai amostras, converte e gera preview |
| Texto clínico     | `python -m scripts.data_prep.texto_clinico`     | **auto**  | Gera documentos sintéticos (offline)|
| Caso sintético    | `python -m scripts.data_prep.caso_sintetico`    | **auto**  | Junta 1 amostra de cada modalidade  |
| Áudio             | `python -m scripts.data_prep.audio_transcrever` | manual    | Coloque áudios (`.wav/.mp3/.m4a/...`) em `data/audio/` — detecta **qualquer nome**. Whisper local ou Azure via env para transcrever |
| Fisioterapia      | `python -m scripts.data_prep.fisioterapia_pose` | manual    | Coloque vídeos (`.mp4/.avi/...`) **ou** esqueletos do IntelliRehabDS (`.txt/.csv`) em `data/video_fisioterapia/` — detecta qualquer nome |

Se um download automático falhar (rede, URL ou licença que exige login), os scripts emitem uma mensagem
clara com a instrução de **obtenção manual** — baixe a amostra do link na tabela de origem e coloque-a
na pasta indicada.

> **Áudio e fisioterapia processam qualquer arquivo presente** — não exigem nomes fixos. A **categoria**
> do áudio e a **execução** da fisioterapia são inferidas por palavras-chave no nome (ex.:
> `relato_ansiedade.wav` → `ansiedade`; `agachamento_incorreto.mp4` → `incorreto`). Se não reconhecer,
> marca como `nao_rotulado`/`correto` e avisa para ajustar no `metadados.json`. Sem o pacote
> `openai-whisper` instalado, o áudio é catalogado com `transcricao` vazia (apenas aviso) — instale-o
> (ou use `AUDIO_BACKEND=azure`) para gerar o texto.

> **Cicatriz — mapeamento de classes:** o AZH Wound classifica por *tipo* de ferida (não por infecção).
> O script usa a pasta `N` (pele sem ferida) como `ferida_ok` e a pasta `S` (ferida cirúrgica) como
> `ferida_alerta`, gerando 1 caixa por imagem. É um *proxy* para o "hello world" do YOLO; a limitação
> está registrada abaixo.

## Origem e licença dos datasets

| Modalidade        | Dataset                       | Licença / uso          | Origem |
| ----------------- | ----------------------------- | ---------------------- | ------ |
| Sinais vitais     | Maternal Health Risk (UCI)    | **CC BY 4.0**          | https://archive.ics.uci.edu/dataset/863/maternal+health+risk |
| Cicatriz (vídeo)  | AZH Wound                     | Acadêmico (ver repo)   | https://github.com/uwm-bigdata/wound-classification-using-images-and-locations |
| Fisioterapia      | IntelliRehabDS                | Acadêmico (Zenodo)     | https://zenodo.org/records/4610859 |
| Fisioterapia (alt)| REHAB24-6                     | Acadêmico              | (buscar "REHAB24-6 dataset") |
| Áudio             | Androids Corpus               | Acadêmico              | https://github.com/androidscorpus/data |
| Áudio (alt)       | DEPAC                         | Acadêmico              | https://aclanthology.org/2022.clpsych-1.1.pdf |
| Texto clínico     | Gerado sinteticamente         | N/A (próprio)          | `scripts/data_prep/texto_clinico.py` |

## Limitações conhecidas (registrar no relatório)

- **Cicatriz:** o AZH Wound não é específico de cesárea, mas feridas cirúrgicas têm aparência
  semelhante. Por ser uma base de **classificação**, geramos uma caixa por imagem cobrindo a ferida
  (decisão documentada) ao converter para o formato de detecção YOLOv8.
- **Áudio:** não existe base pública só de depressão **pós-parto**; usamos bases de depressão/ansiedade
  geral + áudios sintéticos (TTS) para as demais categorias.
- **Fusão:** os datasets são de **pessoas diferentes**; o "mesmo paciente" só existe no uso real. Por
  isso o **caso de exemplo sintético** (`casos/`) junta 1 amostra de cada modalidade para a demo.
