"""Testes do reforço por aumento sintético dos sinais vitais (Fase 5 — F5-05).

Valida a estrutura e a coerência da comparação antes/depois — sem assertar valores absolutos
de métricas (que dependem dos dados), apenas que a computação real é consistente.
"""

from __future__ import annotations

import pandas as pd

from app.sinais_vitais.treino import comparar_com_aumento

COLUNAS = ["Age", "SystolicBP", "DiastolicBP", "BS", "BodyTemp", "HeartRate", "RiskLevel"]


def _base() -> pd.DataFrame:
    linhas = [
        (25, 118, 78, 7.0, 98.0, 70, "low"),
        (29, 120, 80, 6.5, 98.2, 72, "low"),
        (31, 130, 85, 8.0, 98.6, 78, "mid"),
        (34, 135, 88, 9.0, 99.0, 80, "mid"),
        (38, 150, 95, 12.0, 100.0, 90, "high"),
        (41, 145, 92, 11.0, 99.5, 88, "high"),
    ]
    return pd.DataFrame(linhas, columns=COLUNAS)


def _sinteticas() -> pd.DataFrame:
    linhas = [
        (33, 158, 102, 8.5, 98.6, 86, "high"),
        (36, 162, 104, 9.2, 98.4, 90, "high"),
        (30, 155, 100, 7.8, 98.8, 84, "high"),
    ]
    return pd.DataFrame(linhas, columns=COLUNAS)


def test_comparacao_tem_estrutura_e_contagens_coerentes():
    comp = comparar_com_aumento(_base(), _sinteticas())

    assert comp["n_base"] == 6
    assert comp["n_sinteticas"] == 3
    assert comp["n_aumentado"] == 9
    for chave in ("acuracia", "f1_macro"):
        assert chave in comp["base"]
        assert chave in comp["aumentado"]
        assert chave in comp["delta"]


def test_delta_e_diferenca_das_metricas():
    comp = comparar_com_aumento(_base(), _sinteticas())
    esperado = round(comp["aumentado"]["f1_macro"] - comp["base"]["f1_macro"], 4)
    assert comp["delta"]["f1_macro"] == esperado
