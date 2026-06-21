"""Export do detector de cicatriz treinado para ONNX (fallback: mantém o ``.pt``).

Uso (a partir de ai-service/):
    python -m app.cicatriz.exportar
"""

from __future__ import annotations

import sys
from pathlib import Path

from app.common import get_logger, models_dir

LOG = get_logger("cicatriz")


def exportar(best_pt=None, *, formato: str = "onnx"):
    """Exporta o melhor peso para ``formato`` (ONNX por padrão). Retorna o caminho exportado."""
    from ultralytics import YOLO

    if best_pt is None:
        best_pt = models_dir("cicatriz") / "best.pt"
    best_pt = Path(best_pt)
    if not best_pt.exists():
        raise FileNotFoundError(
            f"{best_pt} não encontrado. Treine primeiro: python -m app.cicatriz.treino"
        )
    caminho = YOLO(str(best_pt)).export(format=formato)
    destino = models_dir("cicatriz") / f"best.{formato}"
    origem = Path(caminho)
    if origem.exists() and origem.resolve() != destino.resolve():
        origem.replace(destino)
    return destino


def main() -> int:
    try:
        destino = exportar()
    except FileNotFoundError as exc:
        LOG.error("%s", exc)
        return 1
    except ImportError:
        LOG.error("ultralytics não instalado. Rode: pip install -r ai-service/requirements.txt")
        return 1
    except Exception as exc:  # pragma: no cover - ambiente de export
        LOG.error("Falha no export ONNX (%s). Mantenha o best.pt como fallback.", exc)
        return 1
    LOG.info("Modelo exportado: %s", destino)
    return 0


if __name__ == "__main__":
    sys.exit(main())
