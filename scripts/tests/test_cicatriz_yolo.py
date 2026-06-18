"""Testes das funções puras de conversão para YOLOv8 (T6)."""

from __future__ import annotations

import pytest

from scripts.data_prep.cicatriz_yolo import (
    CLASSES,
    bbox_para_yolo,
    caixa_imagem_inteira,
    montar_data_yaml,
)


def test_bbox_para_yolo_normaliza_centro():
    # Caixa 50..150 em x (img 200) -> centro 100/200=0.5, largura 100/200=0.5
    linha = bbox_para_yolo(50, 25, 100, 50, 200, 100, class_id=1)
    cls, cx, cy, w, h = linha.split()
    assert cls == "1"
    assert float(cx) == pytest.approx(0.5)
    assert float(cy) == pytest.approx(0.5)
    assert float(w) == pytest.approx(0.5)
    assert float(h) == pytest.approx(0.5)


def test_bbox_para_yolo_valida_limites():
    with pytest.raises(ValueError):
        bbox_para_yolo(0, 0, 300, 50, 200, 100, class_id=0)  # largura > imagem
    with pytest.raises(ValueError):
        bbox_para_yolo(0, 0, 10, 10, 0, 100, class_id=0)  # img_w inválido


def test_caixa_imagem_inteira_centralizada():
    linha = caixa_imagem_inteira(640, 480, class_id=0)
    cls, cx, cy, w, h = linha.split()
    assert cls == "0"
    assert float(cx) == pytest.approx(0.5)
    assert float(cy) == pytest.approx(0.5)
    assert float(w) == pytest.approx(1.0)


def test_montar_data_yaml_estrutura():
    y = montar_data_yaml("/tmp/data/video_cicatriz")
    assert y["nc"] == len(CLASSES)
    assert y["names"] == {0: "ferida_ok", 1: "ferida_alerta"}
    assert y["path"].endswith("video_cicatriz")
