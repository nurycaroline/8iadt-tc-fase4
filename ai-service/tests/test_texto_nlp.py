"""Testes do módulo de texto/NLP (T10)."""

from __future__ import annotations

from app.texto.nlp import analisar


def test_sinal_infeccao_por_febre_e_dor():
    evid = analisar("Queixa de febre (38,5°C) e dor na cicatriz, com secreção purulenta.")
    assert evid["achado"] == "sinal_infeccao"
    assert "febre" in evid["trecho"].lower()


def test_complicacao_por_proteinuria_e_cefaleia():
    evid = analisar("PA 152/98 mmHg, proteinúria, cefaleia e escotomas. Hipótese: pré-eclâmpsia.")
    assert evid["achado"] == "complicacao"


def test_complicacao_por_depressao():
    evid = analisar("Relata tristeza persistente e anedonia, compatível com depressão pós-parto.")
    assert evid["achado"] == "complicacao"


def test_texto_neutro():
    evid = analisar("Puérpera bem, amamentando. Cicatriz limpa e seca. Conduta de rotina.")
    assert evid["achado"] == "neutro"
    assert evid["trecho"] == ""


def test_infeccao_tem_precedencia_sobre_complicacao():
    texto = "Febre e dor na cicatriz; também refere cefaleia leve."
    assert analisar(texto)["achado"] == "sinal_infeccao"
