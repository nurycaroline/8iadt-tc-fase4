"""Utilidades compartilhadas pelo serviço de IA da Fase 2.

Mantém os módulos de cada modalidade pequenos:
- resolução de caminhos para ``data/`` (insumo da Fase 1) e ``ai-service/models/`` (saída);
- IO idempotente de métricas (``metrics.json``);
- gráfico da matriz de confusão (matplotlib);
- logging estruturado (JSON) com ``case_id`` (mesma convenção da Fase 1).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

# Modalidades de dados (saídas da Fase 1, em data/).
DATA_MODALIDADES = (
    "sinais_vitais",
    "video_cicatriz",
    "audio",
    "texto_clinico",
    "casos",
)

# Modalidades de modelo (saídas da Fase 2, em ai-service/models/).
MODELO_MODALIDADES = (
    "sinais_vitais",
    "cicatriz",
    "audio",
    "texto",
)


def project_root() -> Path:
    """Raiz do repositório (três níveis acima: ai-service/app/common.py)."""
    return Path(__file__).resolve().parents[2]


def data_dir(modalidade: str | None = None) -> Path:
    """Resolve (e cria) o caminho sob ``data/`` (insumo da Fase 1)."""
    base = project_root() / "data"
    if modalidade is None:
        base.mkdir(parents=True, exist_ok=True)
        return base
    if modalidade not in DATA_MODALIDADES:
        raise ValueError(
            f"Modalidade de dados desconhecida: {modalidade!r}. Use uma de {DATA_MODALIDADES}."
        )
    path = base / modalidade
    path.mkdir(parents=True, exist_ok=True)
    return path


def models_dir(modalidade: str | None = None) -> Path:
    """Resolve (e cria) o caminho sob ``ai-service/models/`` (pesos/métricas)."""
    base = project_root() / "ai-service" / "models"
    if modalidade is None:
        base.mkdir(parents=True, exist_ok=True)
        return base
    if modalidade not in MODELO_MODALIDADES:
        raise ValueError(
            f"Modalidade de modelo desconhecida: {modalidade!r}. Use uma de {MODELO_MODALIDADES}."
        )
    path = base / modalidade
    path.mkdir(parents=True, exist_ok=True)
    return path


def salvar_metricas(path: str | Path, metricas: dict[str, Any]) -> Path:
    """Escreve métricas como JSON (UTF-8, indentado) de forma idempotente."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(metricas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path


def carregar_metricas(path: str | Path) -> dict[str, Any]:
    """Lê um ``metrics.json`` salvo por :func:`salvar_metricas`."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def salvar_matriz_confusao(
    y_true: list[Any],
    y_pred: list[Any],
    labels: list[Any],
    path: str | Path,
    *,
    titulo: str = "Matriz de confusão",
) -> Path:
    """Plota e salva a matriz de confusão como PNG (matplotlib + scikit-learn)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    matriz = confusion_matrix(y_true, y_pred, labels=labels)
    disp = ConfusionMatrixDisplay(confusion_matrix=matriz, display_labels=labels)
    fig, ax = plt.subplots(figsize=(4, 4))
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(titulo)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


class _CaseIdFilter(logging.Filter):
    def __init__(self, case_id: str | None) -> None:
        super().__init__()
        self.case_id = case_id or "-"

    def filter(self, record: logging.LogRecord) -> bool:
        record.case_id = getattr(record, "case_id", self.case_id)
        return True


def get_logger(name: str = "ai_service", case_id: str | None = None) -> logging.Logger:
    """Logger com saída JSON simples incluindo ``case_id`` (observabilidade da stack)."""
    logger = logging.getLogger(f"{name}:{case_id or '-'}")
    if logger.handlers:
        return logger
    handler = logging.StreamHandler()
    fmt = (
        '{"level":"%(levelname)s","logger":"%(name)s",'
        '"case_id":"%(case_id)s","msg":"%(message)s"}'
    )
    handler.setFormatter(logging.Formatter(fmt))
    handler.addFilter(_CaseIdFilter(case_id))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
