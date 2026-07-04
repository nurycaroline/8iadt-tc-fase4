"""Caso de exemplo sintético — a "cola" da demonstração da fusão multimodal.

Monta uma paciente fictícia combinando 1 amostra de cada modalidade num pacote coerente, no formato
do objeto de **requisição** do contrato de API (docs/contrato-api.md). Gera 3 variantes:
``BAIXO`` (tudo normal), ``MEDIO`` (risco isolado) e ``ALTO`` (multi-risco).

Uso:
    python -m scripts.data_prep.caso_sintetico
"""

from __future__ import annotations

import sys

from .common import data_dir, get_logger, write_json

LOG = get_logger("caso_sintetico")

# Modalidades opcionais -> chave no JSON de requisição (contrato-api.md §1).
_CAMPOS_MODALIDADE = {
    "video_cicatriz": "video_cicatriz_url",
    "audio": "audio_url",
    "texto_clinico": "texto_clinico",
}


def montar_caso(
    case_id: str,
    paciente: dict,
    *,
    video_cicatriz: str | None = None,
    dados_vitais_csv: str | None = None,
    audio: str | None = None,
    texto_clinico: str | None = None,
) -> dict:
    """Monta o pacote de um caso (função pura), omitindo modalidades ausentes.

    O resultado segue o objeto de requisição do contrato Node -> Python.
    """
    if not case_id:
        raise ValueError("case_id é obrigatório.")
    if "id" not in paciente:
        raise ValueError("paciente.id é obrigatório.")

    caso: dict = {"case_id": case_id, "paciente": paciente}

    if video_cicatriz is not None:
        caso["video_cicatriz_url"] = video_cicatriz
    if dados_vitais_csv is not None:
        caso["dados_vitais"] = {"csv_url": dados_vitais_csv}
    if audio is not None:
        caso["audio_url"] = audio
    if texto_clinico is not None:
        caso["texto_clinico"] = texto_clinico

    return caso


def gerar_variantes() -> dict[str, dict]:
    """Gera as 3 variantes coerentes referenciando artefatos do mini-dataset em ``data/``."""
    paciente = {
        "id": "pac-demo-001",
        "primeiro_nome": "Maria",
        "idade": 31,
        "gestante": False,
        "idade_gestacional_semanas": None,
    }

    baixo = montar_caso(
        "caso-baixo",
        {**paciente, "id": "pac-demo-001"},
        video_cicatriz="data/video_cicatriz/images/ferida_ok_01.jpg",
        dados_vitais_csv="data/sinais_vitais/maternal_amostras.csv",
        audio="data/audio/consulta_neutro.wav",
        texto_clinico="data/texto_clinico/evolucao_01.txt",
    )

    medio = montar_caso(
        "caso-medio",
        {**paciente, "id": "pac-demo-002"},
        dados_vitais_csv="data/sinais_vitais/maternal_amostras.csv",
        audio="data/audio/relato_ansiedade.wav",
        texto_clinico="data/texto_clinico/evolucao_03.txt",
    )

    alto = montar_caso(
        "caso-alto",
        {**paciente, "id": "pac-demo-003"},
        video_cicatriz="data/video_cicatriz/images/ferida_alerta_01.jpg",
        dados_vitais_csv="data/sinais_vitais/maternal_amostras.csv",
        audio="data/audio/relato_depressao.wav",
        texto_clinico="data/texto_clinico/evolucao_02.txt",
    )

    return {"caso_baixo": baixo, "caso_medio": medio, "caso_alto": alto}


def main() -> int:
    pasta = data_dir("casos")
    variantes = gerar_variantes()
    for nome, caso in variantes.items():
        write_json(pasta / f"{nome}.json", caso)
    LOG.info("Gerados %d casos sintéticos em %s", len(variantes), pasta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
