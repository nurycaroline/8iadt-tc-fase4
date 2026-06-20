"""Testes dos limiares clínicos (Tarefa 2.7)."""

from __future__ import annotations

from app import limiares


def test_pa_no_limite_dispara_alerta():
    assert limiares.pa_em_alerta(140, 85) is True
    assert limiares.pa_em_alerta(120, 90) is True


def test_pa_abaixo_do_limite_nao_dispara():
    assert limiares.pa_em_alerta(139, 89) is False


def test_pa_none_nao_quebra():
    assert limiares.pa_em_alerta(None, None) is False


def test_confianca_minima():
    assert limiares.confianca_suficiente(0.7) is True
    assert limiares.confianca_suficiente(0.69) is False


def test_risco_alto_por_classe_ou_pa():
    assert limiares.risco_alto_sinais_vitais("high") is True
    assert limiares.risco_alto_sinais_vitais("low", 150, 95) is True
    assert limiares.risco_alto_sinais_vitais("low", 120, 80) is False
