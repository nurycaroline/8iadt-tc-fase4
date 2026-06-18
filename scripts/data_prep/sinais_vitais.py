"""Sinais vitais — Maternal Health Risk (UCI id 863).

Baixa o dataset, remove outliers fisiologicamente implausíveis, padroniza o rótulo de risco
(``low``/``mid``/``high``) e exporta um CSV limpo com pelo menos 5 amostras rotuladas.

Uso:
    python -m scripts.data_prep.sinais_vitais
"""

from __future__ import annotations

import sys

from .common import data_dir, get_logger, write_csv

LOG = get_logger("sinais_vitais")

UCI_DATASET_ID = 863

# Faixas fisiologicamente plausíveis (inclusivas). Valores fora disso são descartados.
# BodyTemp está em Fahrenheit e BS (blood sugar) em mmol/L, como no dataset original.
FAIXAS_PLAUSIVEIS: dict[str, tuple[float, float]] = {
    "Age": (10, 70),
    "SystolicBP": (70, 200),
    "DiastolicBP": (40, 130),
    "BS": (3, 30),
    "BodyTemp": (95, 107),
    "HeartRate": (40, 130),
}

_MAPA_RISCO = {
    "low risk": "low",
    "low": "low",
    "mid risk": "mid",
    "mid": "mid",
    "medium": "mid",
    "high risk": "high",
    "high": "high",
}


def normalizar_risco(valor: object) -> str | None:
    """Normaliza o rótulo de risco para ``low``/``mid``/``high`` (ou None se inválido)."""
    if valor is None:
        return None
    chave = str(valor).strip().lower()
    return _MAPA_RISCO.get(chave)


def limpar(df):
    """Limpa o DataFrame de sinais vitais (função pura, sem IO).

    - coage colunas numéricas;
    - descarta linhas com valores fora das faixas plausíveis ou faltantes;
    - normaliza ``RiskLevel`` para ``low``/``mid``/``high``;
    - remove duplicatas.
    """
    import pandas as pd

    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    for col in FAIXAS_PLAUSIVEIS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "RiskLevel" in df.columns:
        df["RiskLevel"] = df["RiskLevel"].map(normalizar_risco)

    colunas_presentes = [c for c in FAIXAS_PLAUSIVEIS if c in df.columns]
    df = df.dropna(subset=[*colunas_presentes, "RiskLevel"])

    for col in colunas_presentes:
        baixo, alto = FAIXAS_PLAUSIVEIS[col]
        df = df[(df[col] >= baixo) & (df[col] <= alto)]

    return df.drop_duplicates().reset_index(drop=True)


def selecionar_amostras(df, n: int = 5):
    """Seleciona ao menos ``n`` amostras, estratificando por ``RiskLevel`` quando possível."""
    if len(df) <= n:
        return df.reset_index(drop=True)

    classes = df["RiskLevel"].unique()
    por_classe = max(1, n // max(1, len(classes)))
    partes = [
        grupo.head(por_classe) for _, grupo in df.groupby("RiskLevel", sort=False)
    ]
    import pandas as pd

    amostra = pd.concat(partes)
    if len(amostra) < n:
        restantes = df.drop(amostra.index)
        amostra = pd.concat([amostra, restantes.head(n - len(amostra))])
    return amostra.reset_index(drop=True)


def baixar_dataset():
    """Baixa o Maternal Health Risk via ``ucimlrepo``. Levanta erro claro se indisponível."""
    try:
        from ucimlrepo import fetch_ucirepo
    except ImportError as exc:
        raise RuntimeError(
            "Pacote 'ucimlrepo' não instalado. Rode: "
            "pip install -r scripts/requirements-data.txt"
        ) from exc

    LOG.info("Baixando Maternal Health Risk (UCI id %s)...", UCI_DATASET_ID)
    repo = fetch_ucirepo(id=UCI_DATASET_ID)
    df = repo.data.features.copy()
    df["RiskLevel"] = repo.data.targets.iloc[:, 0].values
    return df


def main() -> int:
    saida = data_dir("sinais_vitais")
    try:
        bruto = baixar_dataset()
    except Exception as exc:
        LOG.error("Não foi possível baixar o dataset: %s", exc)
        LOG.error(
            "Baixe manualmente de https://archive.ics.uci.edu/dataset/863 e salve em %s", saida
        )
        return 1

    limpo = limpar(bruto)
    write_csv(limpo, saida / "maternal_clean.csv")
    LOG.info("CSV limpo salvo: %d linhas", len(limpo))

    amostras = selecionar_amostras(limpo, n=5)
    write_csv(amostras, saida / "maternal_amostras.csv")
    LOG.info("Amostras (%d) salvas para o caso sintético", len(amostras))
    return 0


if __name__ == "__main__":
    sys.exit(main())
