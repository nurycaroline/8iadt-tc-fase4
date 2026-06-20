"""Testes do classificador de áudio (T11)."""

from __future__ import annotations

from app.audio.classificacao import classificar


def test_violencia():
    evid = classificar("Tenho medo dele, ontem ele me bateu de novo.")
    assert evid["categoria"] == "violencia"
    assert evid["confianca"] >= 0.7


def test_depressao_pos_parto():
    evid = classificar("Tristeza enorme, não sinto prazer em nada e só tenho vontade de chorar.")
    assert evid["categoria"] == "depressao_pos_parto"


def test_ansiedade():
    evid = classificar("Ando muito ansiosa, o coração acelerado e uma angústia constante.")
    assert evid["categoria"] == "ansiedade"


def test_fadiga():
    evid = classificar("Estou exausta, sem energia, não durmo direito desde o parto.")
    assert evid["categoria"] == "fadiga"


def test_neutro_baixa_confianca():
    evid = classificar("Tudo bem, a consulta foi tranquila e estou me sentindo ok.")
    assert evid["categoria"] == "neutro"
    assert evid["confianca"] < 0.7


def test_violencia_tem_prioridade():
    evid = classificar("Estou cansada e ansiosa, e ele me agrediu ontem.")
    assert evid["categoria"] == "violencia"
