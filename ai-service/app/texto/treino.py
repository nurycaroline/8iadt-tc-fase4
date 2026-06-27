"""Treino dos classificadores de **texto** PT-BR da Fase 8 (depressão e violência).

Baseline leve e local: **TF-IDF + LogisticRegression** (`scikit-learn`), seguindo a filosofia
mini-dataset do repo ("se rodar com 5, roda com 500"). Lê os CSVs preparados por
``scripts.data_prep.fase8_datasets`` (``data/texto_clinico/fase8/<nome>_pt.csv`` com colunas
``texto,label``), treina, **salva o artefato** (``ai-service/models/texto/<nome>.joblib``) e
registra **métricas** (F1, matriz de confusão) em ``models/texto/metrics_<nome>.json``.

Uso (a partir de ``ai-service/``)::

    python -m app.texto.treino                 # treina depressão e violência
    python -m app.texto.treino --nome violencia
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from app.common import data_dir, get_logger, models_dir, salvar_matriz_confusao, salvar_metricas

LOG = get_logger("texto_treino")

# Classificadores PT a treinar: nome do artefato → CSV de origem.
ALVOS = ("depressao", "violencia")


def construir_pipeline():
    """Pipeline TF-IDF + LogisticRegression (baseline local, rápido em CPU)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline

    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=20000)),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )


def treinar_texto(
    textos: list[str], labels: list[int]
) -> tuple[Any, dict[str, Any], list[int], list[int]]:
    """Treina o pipeline → ``(pipeline, metricas, y_teste, y_pred)``. Aceita poucas amostras."""
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.model_selection import train_test_split

    y = [int(v) for v in labels]
    pipeline = construir_pipeline()

    # Com poucas amostras (ou classe única), treina e avalia no próprio conjunto (smoke honesto).
    pode_dividir = len(set(y)) > 1 and len(y) >= 8
    if pode_dividir:
        x_tr, x_te, y_tr, y_te = train_test_split(
            textos, y, test_size=0.25, random_state=42, stratify=y
        )
    else:
        x_tr, x_te, y_tr, y_te = textos, textos, y, y

    pipeline.fit(x_tr, y_tr)
    y_pred = [int(v) for v in pipeline.predict(x_te)]
    rep = classification_report(y_te, y_pred, output_dict=True, zero_division=0)
    metricas = {
        "n_treino": len(y_tr),
        "n_teste": len(y_te),
        "avaliacao": "holdout" if pode_dividir else "in-sample (poucas amostras)",
        "f1_macro": round(float(rep["macro avg"]["f1-score"]), 4),
        "f1_positivo": round(float(rep.get("1", {}).get("f1-score", 0.0)), 4),
        "acuracia": round(float(rep["accuracy"]), 4),
        "matriz_confusao": confusion_matrix(y_te, y_pred, labels=[0, 1]).tolist(),
    }
    return pipeline, metricas, list(y_te), y_pred


def _ler_csv(caminho: Path) -> tuple[list[str], list[int]] | None:
    import pandas as pd

    if not caminho.exists():
        LOG.error(
            "CSV %s ausente. Rode: python -m scripts.data_prep.fase8_datasets (docs/datasets.md).",
            caminho,
        )
        return None
    df = pd.read_csv(caminho).dropna(subset=["texto", "label"])
    if df.empty:
        LOG.error("CSV %s vazio.", caminho)
        return None
    return df["texto"].astype(str).tolist(), df["label"].astype(int).tolist()


def treinar_e_salvar(nome: str) -> dict[str, Any] | None:
    """Treina o classificador ``nome`` a partir do CSV preparado e salva artefato + métricas."""
    import joblib

    csv = data_dir("texto_clinico") / "fase8" / f"{nome}_pt.csv"
    dados = _ler_csv(csv)
    if dados is None:
        return None
    textos, labels = dados

    pipeline, metricas, y_te, y_pred = treinar_texto(textos, labels)
    metricas.update({"modelo": nome, "fonte": str(csv), "algoritmo": "tfidf+logreg"})

    destino = models_dir("texto") / f"{nome}.joblib"
    joblib.dump({"pipeline": pipeline, "rotulo_positivo": nome}, destino)
    # metrics.json (versionado pela política do repo) num subdiretório por modelo.
    salvar_metricas(models_dir("texto") / nome / "metrics.json", metricas)
    try:
        salvar_matriz_confusao(
            y_te, y_pred, [0, 1],
            models_dir("texto") / nome / "matriz.png", titulo=f"Texto — {nome}",
        )
    except Exception:  # pragma: no cover - a matriz já está no metrics.json
        pass
    LOG.info(
        "Modelo de %s salvo em %s (F1 macro=%.3f).", nome, destino, metricas["f1_macro"]
    )
    return metricas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Treino dos classificadores de texto (Fase 8).")
    parser.add_argument("--nome", choices=ALVOS, help="treina apenas um classificador")
    args = parser.parse_args(argv)

    nomes = (args.nome,) if args.nome else ALVOS
    feitos = 0
    for nome in nomes:
        if treinar_e_salvar(nome):
            feitos += 1
    if not feitos:
        LOG.error("Nenhum classificador treinado. Prepare os dados da Fase 8 primeiro.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
