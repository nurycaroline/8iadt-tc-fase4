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


def test_texto_valido():
    evid = schemas.evidencia_texto("sinal_infeccao", "febre e dor na cicatriz")
    assert evid["achado"] == "sinal_infeccao"
    assert "febre" in evid["trecho"]
    # Fase 8: subevidências sempre presentes (neutras por padrão).
    assert evid["depressao"] == {"rotulo": "neutro", "confianca": 0.0}
    assert evid["violencia"] == {"rotulo": "neutro", "confianca": 0.0}


def test_texto_com_subevidencias():
    evid = schemas.evidencia_texto(
        "neutro",
        "",
        depressao=("depressao", 0.8),
        violencia={"rotulo": "violencia", "confianca": 0.9},
    )
    assert evid["depressao"] == {"rotulo": "depressao", "confianca": 0.8}
    assert evid["violencia"] == {"rotulo": "violencia", "confianca": 0.9}


def test_subevidencia_rotulo_invalido():
    with pytest.raises(ValueError):
        schemas.evidencia_texto("neutro", depressao=("ansiedade", 0.5))


def test_audio_unificada_deriva_categoria_legada():
    texto = schemas.evidencia_texto("neutro", "", violencia=("violencia", 0.8))
    evid = schemas.evidencia_audio_unificada(("neutro", 0.4), "ele me bateu", texto)
    assert evid["acustico"] == {"rotulo": "neutro", "confianca": 0.4}
    assert evid["transcricao"] == "ele me bateu"
    assert evid["texto"]["violencia"]["rotulo"] == "violencia"
    # Categoria legada derivada: violência (texto) → compat com a fusão/relatório.
    assert evid["categoria"] == "violencia"
    assert evid["confianca"] == 0.8


def test_audio_unificada_categoria_depressao_e_neutro():
    texto_dep = schemas.evidencia_texto("neutro", "", depressao=("depressao", 0.7))
    evid = schemas.evidencia_audio_unificada(("neutro", 0.5), "estou triste", texto_dep)
    assert evid["categoria"] == "depressao_pos_parto"
    texto_neutro = schemas.evidencia_texto("neutro", "")
    evid2 = schemas.evidencia_audio_unificada(("neutro", 0.5), "tudo bem", texto_neutro)
    assert evid2["categoria"] == "neutro"
