"""Texto clínico (NLP) — geração de documentos sintéticos rotulados.

Gera ~5 documentos de evolução/laudo em texto simples (achados normais e de risco) e grava
``data/texto_clinico/rotulos.json`` com os achados de interesse. Totalmente offline.

Uso:
    python -m scripts.data_prep.texto_clinico
"""

from __future__ import annotations

import sys

from .common import data_dir, get_logger, write_json

LOG = get_logger("texto_clinico")

# Achados alinhados ao contrato de API (docs/contrato-api.md): complicacao | sinal_infeccao | neutro
DOCUMENTOS: list[dict] = [
    {
        "arquivo": "evolucao_01.txt",
        "achado": "neutro",
        "texto": (
            "Puérpera no 10º dia pós-parto. Refere boa amamentação e sono preservado. "
            "PA 118/76 mmHg, afebril. Cicatriz da cesárea limpa, seca, sem sinais flogísticos. "
            "Conduta: manter cuidados habituais e retorno de rotina."
        ),
        "trechos": [],
    },
    {
        "arquivo": "evolucao_02.txt",
        "achado": "sinal_infeccao",
        "texto": (
            "Puérpera no 7º dia pós-parto. Queixa de febre (38,5°C) e dor na cicatriz. "
            "Ao exame, ferida operatória com hiperemia, calor local e saída de secreção purulenta. "
            "Conduta: avaliar antibioticoterapia e reavaliação precoce."
        ),
        "trechos": ["febre", "dor na cicatriz", "secreção purulenta", "hiperemia"],
    },
    {
        "arquivo": "evolucao_03.txt",
        "achado": "complicacao",
        "texto": (
            "Gestante de 34 semanas em acompanhamento. PA 152/98 mmHg aferida em duas ocasiões. "
            "Exame de urina com proteinúria. Refere cefaleia e escotomas visuais. "
            "Hipótese: pré-eclâmpsia. Conduta: encaminhamento para avaliação obstétrica urgente."
        ),
        "trechos": ["PA 152/98", "proteinúria", "cefaleia", "escotomas"],
    },
    {
        "arquivo": "evolucao_04.txt",
        "achado": "neutro",
        "texto": (
            "Consulta de pré-natal sem intercorrências. PA 110/70 mmHg, glicemia em jejum normal. "
            "Movimentação fetal presente. Exames laboratoriais dentro da normalidade. "
            "Conduta: seguimento de pré-natal de baixo risco."
        ),
        "trechos": [],
    },
    {
        "arquivo": "evolucao_05.txt",
        "achado": "complicacao",
        "texto": (
            "Puérpera no 20º dia. Relata tristeza persistente, anedonia e dificuldade de vínculo "
            "com o bebê. Nega ideação suicida. Sinais compatíveis com depressão pós-parto. "
            "Conduta: encaminhamento à saúde mental e suporte psicossocial."
        ),
        "trechos": ["tristeza persistente", "anedonia", "depressão pós-parto"],
    },
]


def main() -> int:
    pasta = data_dir("texto_clinico")
    rotulos = []
    for doc in DOCUMENTOS:
        (pasta / doc["arquivo"]).write_text(doc["texto"] + "\n", encoding="utf-8")
        rotulos.append(
            {"arquivo": doc["arquivo"], "achado": doc["achado"], "trechos": doc["trechos"]}
        )
    write_json(pasta / "rotulos.json", rotulos)
    LOG.info("Gerados %d documentos de texto clínico + rotulos.json", len(rotulos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
