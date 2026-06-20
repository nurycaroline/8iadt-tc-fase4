"""Testes dos construtores de evidência (contrato-api.md §3)."""

from __future__ import annotations

import pytest

from app import schemas


def test_cicatriz_valido():
    assert schemas.evidencia_cicatriz("sinal_infeccao", 0.86) == {
        "evento": "sinal_infeccao",
        "confianca": 0.86,
    }


def test_cicatriz_evento_invalido():
    with pytest.raises(ValueError):
        schemas.evidencia_cicatriz("ferida_alerta", 0.9)


def test_confianca_fora_de_faixa():
    with pytest.raises(ValueError):
        schemas.evidencia_audio("violencia", 1.5)


def test_sinais_vitais_valido():
    assert schemas.evidencia_sinais_vitais("hipertensao", "150/95") == {
        "tipo": "hipertensao",
        "valor": "150/95",
    }


def test_sinais_vitais_tipo_invalido():
    with pytest.raises(ValueError):
        schemas.evidencia_sinais_vitais("alto", "150/95")


def test_fisioterapia_amplitude_opcional():
    assert schemas.evidencia_fisioterapia("correta") == {"execucao": "correta"}
    assert schemas.evidencia_fisioterapia("incorreta", "reduzida") == {
        "execucao": "incorreta",
        "amplitude": "reduzida",
    }


def test_texto_valido():
    evid = schemas.evidencia_texto("sinal_infeccao", "febre e dor na cicatriz")
    assert evid["achado"] == "sinal_infeccao"
    assert "febre" in evid["trecho"]
