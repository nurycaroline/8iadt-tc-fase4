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

| Modalidade        | Script                                  | Observação                                  |
| ----------------- | --------------------------------------- | ------------------------------------------- |
| Sinais vitais     | `python -m scripts.data_prep.sinais_vitais`     | Baixa via `ucimlrepo` (UCI id 863)  |
| Cicatriz (YOLO)   | `python -m scripts.data_prep.cicatriz_yolo`     | Baixa 1 amostra do AZH Wound        |
| Áudio             | `python -m scripts.data_prep.audio_transcrever` | Whisper local (ou Azure via env)    |
| Texto clínico     | `python -m scripts.data_prep.texto_clinico`     | Gera documentos sintéticos (offline)|
| Fisioterapia      | `python -m scripts.data_prep.fisioterapia_pose` | Amostras de UCO PhyRehab/IntelliRehab|
| Caso sintético    | `python -m scripts.data_prep.caso_sintetico`    | Junta 1 amostra de cada modalidade  |

Se um download automático falhar (rede, URL ou licença que exige login), os scripts emitem uma mensagem
clara com a instrução de **obtenção manual** — baixe a amostra do link na tabela de origem e coloque-a
na pasta indicada.

## Origem e licença dos datasets

| Modalidade        | Dataset                       | Licença / uso          | Origem |
| ----------------- | ----------------------------- | ---------------------- | ------ |
| Sinais vitais     | Maternal Health Risk (UCI)    | **CC BY 4.0**          | https://archive.ics.uci.edu/dataset/863/maternal+health+risk |
| Cicatriz (vídeo)  | AZH Wound                     | Acadêmico (ver repo)   | https://github.com/uwm-bigdata/wound-classification-using-images-and-locations |
| Fisioterapia      | UCO Physical Rehabilitation   | Acadêmico (ver repo)   | https://github.com/AVAuco/ucophyrehab |
| Fisioterapia (alt)| IntelliRehabDS                | Acadêmico (Zenodo)     | https://zenodo.org/records/4610859 |
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
