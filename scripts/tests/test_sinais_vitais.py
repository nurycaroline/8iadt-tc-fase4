"""Testes das funções puras de preparação de sinais vitais (T5)."""

from __future__ import annotations

import pandas as pd

from scripts.data_prep.sinais_vitais import (
    limpar,
    normalizar_risco,
    selecionar_amostras,
)


def _df_base() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Age": [25, 30, 35, 40, 45],
            "SystolicBP": [120, 140, 90, 150, 130],
            "DiastolicBP": [80, 90, 60, 95, 85],
            "BS": [7.0, 8.0, 6.0, 15.0, 9.0],
            "BodyTemp": [98.0, 98.6, 99.0, 101.0, 98.4],
            "HeartRate": [70, 80, 76, 88, 72],
            "RiskLevel": [
                "low risk",
                "mid risk",
                "low risk",
                "high risk",
                "mid risk",
            ],
        }
    )


def test_normalizar_risco_variacoes():
    assert normalizar_risco("high risk") == "high"
    assert normalizar_risco(" Mid ") == "mid"
    assert normalizar_risco("LOW") == "low"
    assert normalizar_risco("desconhecido") is None
    assert normalizar_risco(None) is None


def test_limpar_descarta_outliers_e_normaliza_rotulo():
    df = _df_base()
    # Linha com FC implausível (7) e PA sistólica impossível (400) devem ser descartadas.
    ruins = pd.DataFrame(
        {
            "Age": [28, 33],
            "SystolicBP": [400, 120],
            "DiastolicBP": [80, 70],
            "BS": [7.0, 7.0],
            "BodyTemp": [98.0, 98.0],
            "HeartRate": [70, 7],
            "RiskLevel": ["low risk", "mid risk"],
        }
    )
    entrada = pd.concat([df, ruins], ignore_index=True)
    limpo = limpar(entrada)

    assert len(limpo) == len(df)
    assert set(limpo["RiskLevel"]) <= {"low", "mid", "high"}
    assert limpo["SystolicBP"].max() <= 200
    assert limpo["HeartRate"].min() >= 40


def test_limpar_remove_faltantes_e_duplicatas():
    df = _df_base()
    com_na = df.copy()
    com_na.loc[0, "SystolicBP"] = None
    duplicada = pd.concat([df, df.iloc[[1]]], ignore_index=True)
    entrada = pd.concat([com_na, duplicada], ignore_index=True)

    limpo = limpar(entrada)
    assert limpo["SystolicBP"].notna().all()
    assert not limpo.duplicated().any()


def test_selecionar_amostras_minimo_cinco():
    df = limpar(_df_base())
    amostras = selecionar_amostras(df, n=5)
    assert len(amostras) >= min(5, len(df))
    assert set(amostras.columns) == set(df.columns)
