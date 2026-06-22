"""Gerador de amostras sintéticas de pré-eclâmpsia para reforçar os sinais vitais (Fase 5 — F5-05).

Produz linhas no **mesmo esquema** do Maternal Health Risk (``Age``, ``SystolicBP``,
``DiastolicBP``, ``BS``, ``BodyTemp``, ``HeartRate``, ``RiskLevel``), refletindo o padrão clínico
de **pré-eclâmpsia** (hipertensão: PAS ≥ 140 e/ou PAD ≥ 90), todas rotuladas como ``high``.

São **dados sintéticos** (não de pacientes reais) — usados apenas para **aumentar** o conjunto de
treino da modalidade de sinais vitais e medir o efeito (LGPD: nenhum dado real é versionado).

Uso (a partir da raiz do repositório):
    python -m scripts.data_prep.preeclampsia_sintetico
"""

from __future__ import annotations

import sys

from .common import data_dir, get_logger, write_csv

LOG = get_logger("preeclampsia_sintetico")

COLUNAS = ["Age", "SystolicBP", "DiastolicBP", "BS", "BodyTemp", "HeartRate", "RiskLevel"]

# Faixas plausíveis (alinhadas a scripts/data_prep/sinais_vitais.FAIXAS_PLAUSIVEIS). A geração é
# clipada nelas para não criar valores fisiologicamente impossíveis.
_CLIP = {
    "Age": (15, 49),
    "SystolicBP": (140, 200),  # hipertensão sistólica (limiar clínico da pré-eclâmpsia)
    "DiastolicBP": (90, 125),  # hipertensão diastólica
    "BS": (4.0, 19.0),
    "BodyTemp": (97.0, 100.0),
    "HeartRate": (60, 110),
}


def gerar(n: int = 60, seed: int = 42):
    """Gera ``n`` amostras sintéticas de pré-eclâmpsia (função pura, determinística por ``seed``).

    Retorna um ``DataFrame`` com as colunas de :data:`COLUNAS` e ``RiskLevel == "high"``.
    """
    import numpy as np
    import pandas as pd

    if n <= 0:
        return pd.DataFrame(columns=COLUNAS)

    rng = np.random.default_rng(seed)

    def _amostra(coluna: str, centro: float, desvio: float):
        baixo, alto = _CLIP[coluna]
        return np.clip(rng.normal(centro, desvio, n), baixo, alto)

    df = pd.DataFrame(
        {
            "Age": _amostra("Age", 32, 7).round().astype(int),
            "SystolicBP": _amostra("SystolicBP", 158, 12).round().astype(int),
            "DiastolicBP": _amostra("DiastolicBP", 102, 8).round().astype(int),
            "BS": _amostra("BS", 8.5, 2.5).round(1),
            "BodyTemp": _amostra("BodyTemp", 98.6, 0.6).round(1),
            "HeartRate": _amostra("HeartRate", 86, 10).round().astype(int),
            "RiskLevel": "high",
        }
    )
    return df[COLUNAS]


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    df = gerar(n=n)
    destino = data_dir("sinais_vitais") / "preeclampsia_sintetico.csv"
    write_csv(df, destino)
    LOG.info("Amostras sintéticas de pré-eclâmpsia geradas: %d -> %s", len(df), destino)
    return 0


if __name__ == "__main__":
    sys.exit(main())
