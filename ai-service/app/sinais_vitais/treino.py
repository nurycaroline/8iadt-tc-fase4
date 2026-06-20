"""Treino do modelo de sinais vitais (Random Forest) sobre o Maternal Health Risk.

Lê ``data/sinais_vitais/maternal_clean.csv`` (saída da Fase 1), treina um
``RandomForestClassifier`` para prever ``RiskLevel`` (``low``/``mid``/``high``), avalia com
acurácia, F1 (macro) e matriz de confusão, e persiste o modelo + métricas em
``ai-service/models/sinais_vitais/``.

Uso (a partir de ai-service/):
    python -m app.sinais_vitais.treino
"""

from __future__ import annotations

import sys

from app.common import (
    data_dir,
    get_logger,
    models_dir,
    salvar_matriz_confusao,
    salvar_metricas,
)

LOG = get_logger("sinais_vitais")

FEATURES = ["Age", "SystolicBP", "DiastolicBP", "BS", "BodyTemp", "HeartRate"]
ALVO = "RiskLevel"
CLASSES = ["low", "mid", "high"]


def carregar_dataset(path=None):
    """Lê o CSV limpo de sinais vitais (Fase 1)."""
    import pandas as pd

    if path is None:
        path = data_dir("sinais_vitais") / "maternal_clean.csv"
    df = pd.read_csv(path)
    faltando = [c for c in [*FEATURES, ALVO] if c not in df.columns]
    if faltando:
        raise ValueError(f"Colunas ausentes em {path}: {faltando}")
    return df


def _dividir(X, y):
    """Divisão treino/validação robusta a amostras pequenas.

    Usa split estratificado quando há dados suficientes; caso contrário treina e avalia no mesmo
    conjunto (smoke), registrando a limitação.
    """
    from sklearn.model_selection import train_test_split

    contagem = y.value_counts()
    if len(y) >= 20 and contagem.min() >= 2:
        return train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    LOG.warning(
        "Amostra pequena (n=%d, menor classe=%d): avaliando no conjunto de treino (smoke).",
        len(y), int(contagem.min()),
    )
    return X, X, y, y


def treinar(df):
    """Treina o Random Forest e devolve ``(modelo, metricas, (y_true, y_pred))``."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, classification_report, f1_score

    X = df[FEATURES]
    y = df[ALVO].astype(str)

    X_tr, X_te, y_tr, y_te = _dividir(X, y)
    modelo = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
    modelo.fit(X_tr, y_tr)
    y_pred = modelo.predict(X_te)

    labels = [c for c in CLASSES if c in set(y)]
    metricas = {
        "modelo": "RandomForestClassifier",
        "n_amostras": int(len(df)),
        "n_treino": int(len(X_tr)),
        "n_validacao": int(len(X_te)),
        "acuracia": round(float(accuracy_score(y_te, y_pred)), 4),
        "f1_macro": round(float(f1_score(y_te, y_pred, average="macro", labels=labels)), 4),
        "relatorio": classification_report(
            y_te, y_pred, labels=labels, output_dict=True, zero_division=0
        ),
        "labels": labels,
    }
    return modelo, metricas, (list(y_te), list(y_pred))


def main() -> int:
    import joblib

    try:
        df = carregar_dataset()
    except FileNotFoundError:
        LOG.error(
            "maternal_clean.csv não encontrado. Rode a Fase 1: "
            "python -m scripts.data_prep.sinais_vitais"
        )
        return 1

    modelo, metricas, (y_true, y_pred) = treinar(df)
    saida = models_dir("sinais_vitais")
    joblib.dump({"modelo": modelo, "features": FEATURES}, saida / "modelo.joblib")
    salvar_metricas(saida / "metrics.json", metricas)
    salvar_matriz_confusao(
        y_true, y_pred, metricas["labels"], saida / "matriz_confusao.png",
        titulo="Sinais vitais — matriz de confusão",
    )
    LOG.info(
        "Modelo salvo. Acurácia=%.3f F1(macro)=%.3f", metricas["acuracia"], metricas["f1_macro"]
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
