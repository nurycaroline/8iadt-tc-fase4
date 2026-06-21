"""Testes da função pura de métricas do baseline (T13)."""

from __future__ import annotations

import pytest

from app.baseline import metricas_modalidade


def test_metricas_perfeitas():
    m = metricas_modalidade([True, False, True], [True, False, True])
    assert m["precisao"] == 1.0
    assert m["recall"] == 1.0
    assert m["taxa_falsos_positivos"] == 0.0


def test_falsos_positivos_e_negativos():
    # y_true: risco, risco, normal, normal
    # y_pred: risco, normal, risco, normal  -> tp=1, fn=1, fp=1, tn=1
    m = metricas_modalidade([True, True, False, False], [True, False, True, False])
    assert m["tp"] == 1 and m["fn"] == 1 and m["fp"] == 1 and m["tn"] == 1
    assert m["precisao"] == 0.5
    assert m["recall"] == 0.5
    assert m["taxa_falsos_positivos"] == 0.5


def test_tamanhos_diferentes_erro():
    with pytest.raises(ValueError):
        metricas_modalidade([True], [True, False])
