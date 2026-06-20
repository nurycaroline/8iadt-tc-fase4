"""Testes da derivação pura de tipo de sinais vitais (T6).

Nome distinto do teste da Fase 1 (scripts/tests/test_sinais_vitais.py) para evitar colisão de
basename na coleta do pytest.
"""

from __future__ import annotations

from app.sinais_vitais.inferencia import derivar_tipo


def test_pa_alta_vira_hipertensao_independe_da_classe():
    assert derivar_tipo("low", 150, 95) == "hipertensao"
    assert derivar_tipo(None, 142, 80) == "hipertensao"


def test_classe_high_sem_pa_alta_vira_risco_medio():
    assert derivar_tipo("high", 120, 80) == "risco_medio"


def test_classe_mid_vira_risco_medio():
    assert derivar_tipo("mid", 118, 76) == "risco_medio"


def test_classe_low_normal():
    assert derivar_tipo("low", 110, 70) == "normal"


def test_classe_desconhecida_normal_sem_alerta():
    assert derivar_tipo(None, 110, 70) == "normal"
