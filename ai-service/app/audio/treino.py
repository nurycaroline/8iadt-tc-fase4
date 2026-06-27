"""Treino do classificador **acústico** de violência da Fase 8 (dataset ``Hemg``).

Extrai features acústicas (MFCC via ``librosa`` — ver ``app.audio.features``) dos áudios listados em
``data/audio/fase8/violencia/manifest.csv`` (``caminho,label``, 1 = violência) e treina um
classificador ``scikit-learn`` (StandardScaler + LogisticRegression). Salva o artefato em
``ai-service/models/audio/violencia_acustico.joblib`` e as métricas em
``models/audio/metrics_violencia_acustico.json``.

Filosofia mini-dataset: funciona com poucas amostras (avalia in-sample quando o conjunto é pequeno).

Uso (a partir de ``ai-service/``)::

    python -m app.audio.treino
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from app.common import data_dir, get_logger, models_dir, salvar_matriz_confusao, salvar_metricas

LOG = get_logger("audio_treino")


def construir_pipeline():
    """StandardScaler + LogisticRegression para o vetor de features acústicas."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    return Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )


def treinar_acustico(
    features, labels: list[int]
) -> tuple[Any, dict[str, Any], list[int], list[int]]:
    """Treina o pipeline acústico → ``(pipeline, metricas, y_teste, y_pred)``."""
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.model_selection import train_test_split

    y = [int(v) for v in labels]
    pipeline = construir_pipeline()
    pode_dividir = len(set(y)) > 1 and len(y) >= 8
    if pode_dividir:
        x_tr, x_te, y_tr, y_te = train_test_split(
            features, y, test_size=0.25, random_state=42, stratify=y
        )
    else:
        x_tr, x_te, y_tr, y_te = features, features, y, y

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


def _carregar_dataset(manifest: Path):
    """Lê o manifest e extrai as features de cada áudio (pula os que falharem)."""
    import numpy as np
    import pandas as pd

    from app.audio.features import extrair_features

    df = pd.read_csv(manifest)
    base = manifest.parent
    feats, labels = [], []
    for _, linha in df.iterrows():
        caminho = base / str(linha["caminho"])
        if not caminho.exists():
            continue
        try:
            feats.append(extrair_features(caminho))
            labels.append(int(linha["label"]))
        except Exception as exc:
            LOG.warning("Falha ao extrair features de %s (%s); pulando.", caminho, exc)
    if not feats:
        return None, None
    return np.vstack(feats), labels


def treinar_e_salvar() -> dict[str, Any] | None:
    """Treina o classificador acústico de violência e salva artefato + métricas."""
    import joblib

    manifest = data_dir("audio") / "fase8" / "violencia" / "manifest.csv"
    if not manifest.exists():
        LOG.error(
            "Manifest %s ausente. Rode: python -m scripts.data_prep.fase8_datasets --apenas audio.",
            manifest,
        )
        return None
    features, labels = _carregar_dataset(manifest)
    if features is None:
        LOG.error("Nenhuma feature extraída (áudios ausentes?). Veja docs/datasets.md.")
        return None

    if len(set(int(v) for v in labels)) < 2:
        LOG.error(
            "Dataset acústico tem uma única classe (%d amostras). Regenere o manifest balanceado: "
            "remova %s e rode `python -m scripts.data_prep.fase8_datasets --apenas audio`.",
            len(labels),
            manifest,
        )
        return None

    pipeline, metricas, y_te, y_pred = treinar_acustico(features, labels)
    metricas.update({"modelo": "violencia_acustico", "algoritmo": "mfcc+logreg"})

    destino = models_dir("audio") / "violencia_acustico.joblib"
    joblib.dump({"pipeline": pipeline}, destino)
    # metrics.json (versionado pela política do repo) num subdiretório por modelo.
    salvar_metricas(models_dir("audio") / "violencia_acustico" / "metrics.json", metricas)
    try:
        salvar_matriz_confusao(
            y_te, y_pred, [0, 1],
            models_dir("audio") / "violencia_acustico" / "matriz.png",
            titulo="Áudio — violência acústica",
        )
    except Exception:  # pragma: no cover - a matriz já está no metrics.json
        pass
    LOG.info("Modelo acústico salvo em %s (F1 macro=%.3f).", destino, metricas["f1_macro"])
    return metricas


def main() -> int:
    return 0 if treinar_e_salvar() else 1


if __name__ == "__main__":
    sys.exit(main())
