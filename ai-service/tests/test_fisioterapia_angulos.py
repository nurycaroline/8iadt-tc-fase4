"""Testes das funções puras de geometria de movimento (T12)."""

from __future__ import annotations

import pytest

from app.fisioterapia.angulos import (
    amplitude,
    angulo,
    classificar_execucao,
    rotular_amplitude,
)
from app.fisioterapia.inferencia import avaliar_keypoints, serie_angulo_joelho


def test_angulo_reto():
    # vértice na origem; segmentos ao longo de x e de y => 90 graus.
    assert angulo((1, 0), (0, 0), (0, 1)) == pytest.approx(90.0, abs=1e-6)


def test_angulo_raso():
    # pontos colineares e opostos => 180 graus.
    assert angulo((-1, 0), (0, 0), (1, 0)) == pytest.approx(180.0, abs=1e-6)


def test_amplitude_rom():
    assert amplitude([90.0, 120.0, 60.0, 100.0]) == pytest.approx(60.0)
    assert amplitude([]) == 0.0


def test_classificar_execucao():
    assert classificar_execucao(40.0) == "correta"
    assert classificar_execucao(10.0) == "incorreta"
    assert rotular_amplitude(40.0) == "adequada"
    assert rotular_amplitude(10.0) == "reduzida"


def _kp(tornozelo_x: float):
    # 17 keypoints COCO; quadril(11), joelho(13, vértice) e tornozelo(15) definidos.
    pts = [(0.0, 0.0)] * 17
    pts[11] = (0.0, 1.0)
    pts[13] = (0.0, 0.0)
    pts[15] = (tornozelo_x, -1.0)
    return pts


def test_serie_e_avaliacao_de_keypoints():
    frames = [_kp(0.0), _kp(2.0)]  # joelho estende/dobra entre frames
    serie = serie_angulo_joelho(frames)
    assert len(serie) == 2
    evid = avaliar_keypoints(frames)
    assert evid["execucao"] in ("correta", "incorreta")


def test_avaliacao_sem_keypoints_nao_avaliado():
    assert avaliar_keypoints([])["execucao"] == "nao_avaliado"
