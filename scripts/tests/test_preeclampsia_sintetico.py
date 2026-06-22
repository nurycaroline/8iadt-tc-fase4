"""Testes do gerador sintético de pré-eclâmpsia (Fase 5 — F5-05)."""

from __future__ import annotations

from scripts.data_prep.preeclampsia_sintetico import COLUNAS, gerar


def test_gera_esquema_e_rotulo_high():
    df = gerar(n=50, seed=1)
    assert list(df.columns) == COLUNAS
    assert len(df) == 50
    assert (df["RiskLevel"] == "high").all()


def test_valores_dentro_das_faixas_plausiveis_e_hipertensao():
    df = gerar(n=200, seed=7)
    # Pré-eclâmpsia: hipertensão (PAS >= 140 e PAD >= 90), dentro de faixas plausíveis.
    assert df["SystolicBP"].between(140, 200).all()
    assert df["DiastolicBP"].between(90, 125).all()
    assert df["Age"].between(15, 49).all()
    assert df["HeartRate"].between(60, 110).all()


def test_determinismo_por_seed():
    a = gerar(n=30, seed=42)
    b = gerar(n=30, seed=42)
    c = gerar(n=30, seed=43)
    assert a.equals(b)
    assert not a.equals(c)


def test_n_zero_retorna_vazio():
    df = gerar(n=0)
    assert len(df) == 0
    assert list(df.columns) == COLUNAS
