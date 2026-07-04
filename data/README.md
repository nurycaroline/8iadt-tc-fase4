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

O orquestrador roda todas as modalidades (best-effort) e imprime um resumo. A modalidade **manual**
(áudio) aparece como `FALHOU` quando os arquivos ainda não foram adicionados — isso é esperado;
adicione as amostras e rode de novo.

Ou rode uma modalidade isolada:

| Modalidade        | Script                                          | Obtenção  | Observação                          |
| ----------------- | ----------------------------------------------- | --------- | ----------------------------------- |
| Sinais vitais     | `python -m scripts.data_prep.sinais_vitais`     | **auto**  | Baixa via `ucimlrepo` (UCI id 863)  |
| Cicatriz (YOLO)   | `python -m scripts.data_prep.cicatriz_yolo`     | **auto**  | Baixa `Test.zip` do AZH Wound (~4 MB), extrai amostras, converte e gera preview |
| Texto clínico     | `python -m scripts.data_prep.texto_clinico`     | **auto**  | Gera documentos sintéticos (offline)|
| Caso sintético    | `python -m scripts.data_prep.caso_sintetico`    | **auto**  | Junta 1 amostra de cada modalidade  |
| Áudio             | `python -m scripts.data_prep.audio_transcrever` | manual    | Coloque áudios (`.wav/.mp3/.m4a/...`) em `data/audio/` — detecta **qualquer nome**. Transcrição **local** (Whisper/`faster-whisper`) |
| **Fase 8** (áudio/texto) | `python -m scripts.data_prep.fase8_datasets`    | **auto*** | Baixa os 3 datasets HF, traduz EN→PT (Argos, offline) e gera negativos → `data/texto_clinico/fase8/*.csv` e `data/audio/fase8/violencia/manifest.csv`. *Requer rede do HF na 1ª vez; offline depois. Ver [Fase 8](../docs/11-fase8-audio-texto-unificado.md) |

Se um download automático falhar (rede, URL ou licença que exige login), os scripts emitem uma mensagem
clara com a instrução de **obtenção manual** — baixe a amostra do link na tabela de origem e coloque-a
na pasta indicada.

> **Áudio processa qualquer arquivo presente** (busca recursiva em subpastas) — não exige nomes fixos.
> A **categoria** do áudio é inferida pelo nome: por palavra-chave (`relato_ansiedade.wav` → `ansiedade`;
> pasta `HC` do Androids → `neutro`). Se não reconhecer, marca `nao_rotulado` e avisa para ajustar no
> `metadados.json`.
>
> **Transcrição (ffmpeg):** o Whisper normalmente usa **ffmpeg**. Se não tiver ffmpeg
> (`brew install ffmpeg`), instale o `soundfile` (`pip install soundfile`) — o script decodifica
> `wav/flac/ogg` sem ffmpeg. Sem o `openai-whisper`, o áudio é catalogado com `transcricao` vazia
> (apenas aviso); use `AUDIO_BACKEND=azure` para o backend de nuvem.

> **Cicatriz — mapeamento de classes:** o AZH Wound classifica por *tipo* de ferida (não por infecção).
> O script usa a pasta `N` (pele sem ferida) como `ferida_ok` e a pasta `S` (ferida cirúrgica) como
> `ferida_alerta`, gerando 1 caixa por imagem. É um *proxy* para o "hello world" do YOLO; a limitação
> está registrada abaixo.

## Origem e licença dos datasets

| Modalidade        | Dataset                       | Licença / uso          | Origem |
| ----------------- | ----------------------------- | ---------------------- | ------ |
| Sinais vitais     | Maternal Health Risk (UCI)    | **CC BY 4.0**          | https://archive.ics.uci.edu/dataset/863/maternal+health+risk |
| Cicatriz (vídeo)  | AZH Wound                     | Acadêmico (ver repo)   | https://github.com/uwm-bigdata/wound-classification-using-images-and-locations |
| Áudio (violência acústica) | `Hemg/audio-based-violence-dataset` | **não especificada** (HF) — risco | https://huggingface.co/datasets/Hemg/audio-based-violence-dataset |
| Texto (depressão) | `ShreyaR/DepressionDetection` (EN→PT) | **não especificada** (HF) — risco | https://huggingface.co/datasets/ShreyaR/DepressionDetection |
| Texto (violência) | `Spiderman01/Domestic_violence_info_support_fromposts` (EN→PT) | **não especificada** (HF) — risco | https://huggingface.co/datasets/Spiderman01/Domestic_violence_info_support_fromposts |
| Texto clínico     | Gerado sinteticamente         | N/A (próprio)          | `scripts/data_prep/texto_clinico.py` |

## Limitações conhecidas (registrar no relatório)

- **Cicatriz:** o AZH Wound não é específico de cesárea, mas feridas cirúrgicas têm aparência
  semelhante. Por ser uma base de **classificação**, geramos uma caixa por imagem cobrindo a ferida
  (decisão documentada) ao converter para o formato de detecção YOLOv8.
- **Áudio (Fase 8):** análise **dupla** — classificador **acústico** de violência (`Hemg`, licença
  não especificada) + transcrição reanalisada como texto. Não há base só de depressão **pós-parto**;
  a depressão migrou para o classificador **ML de texto** (PT). A violência acústica pode se perder na
  transcrição (por isso a trilha do som é separada).
- **Texto (Fase 8):** depressão (`ShreyaR`) e violência (`Spiderman01`) treinados em PT-BR a partir de
  datasets **EN traduzidos offline** (Argos). Licenças **não especificadas** (risco); domínio
  Reddit/Twitter ≠ pós-parto; a tradução adiciona ruído. Fallback por keywords quando o modelo falta.
- **Fusão:** os datasets são de **pessoas diferentes**; o "mesmo paciente" só existe no uso real. Por
  isso o **caso de exemplo sintético** (`casos/`) junta 1 amostra de cada modalidade para a demo.
