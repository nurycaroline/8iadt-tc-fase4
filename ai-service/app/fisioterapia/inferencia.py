"""Inferência de fisioterapia → evidência padronizada (contrato §3).

Usa YOLOv8-pose para extrair keypoints, deriva o ângulo do joelho ao longo dos frames, calcula a
amplitude de movimento (ROM) e classifica a execução. Sem amostra/keypoints → ``nao_avaliado``
(degrada sem quebrar — DD10).
"""

from __future__ import annotations

from app.common import get_logger
from app.fisioterapia.angulos import amplitude, classificar_execucao, rotular_amplitude
from app.fisioterapia.angulos import angulo as _angulo
from app.schemas import evidencia_fisioterapia

LOG = get_logger("fisioterapia")

# Índices de keypoints no formato COCO (YOLOv8-pose): quadril/joelho/tornozelo esquerdos.
QUADRIL, JOELHO, TORNOZELO = 11, 13, 15


def serie_angulo_joelho(keypoints_frames) -> list[float]:
    """Ângulo do joelho (quadril-joelho-tornozelo) por frame (função pura sobre keypoints)."""
    serie = []
    for kp in keypoints_frames:
        if len(kp) > TORNOZELO:
            serie.append(_angulo(kp[QUADRIL], kp[JOELHO], kp[TORNOZELO]))
    return serie


def avaliar_keypoints(keypoints_frames) -> dict:
    """Avalia a execução a partir de uma sequência de keypoints já extraídos (função pura)."""
    serie = serie_angulo_joelho(keypoints_frames)
    if not serie:
        return evidencia_fisioterapia("nao_avaliado")
    rom = amplitude(serie)
    return evidencia_fisioterapia(classificar_execucao(rom), rotular_amplitude(rom))


def avaliar(fonte) -> dict:
    """Extrai keypoints de ``fonte`` (imagem/frames/vídeo) e avalia a execução."""
    try:
        from app.fisioterapia.pose import estimar_keypoints

        keypoints = estimar_keypoints(fonte)
    except Exception as exc:  # pragma: no cover - depende de ultralytics/dados
        LOG.warning("Não foi possível estimar keypoints (%s); execução não avaliada.", exc)
        return evidencia_fisioterapia("nao_avaliado")
    return avaliar_keypoints(keypoints)
