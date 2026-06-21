"""Treino do detector de cicatriz (YOLOv8) + extração de métricas.

Faz fine-tuning de um YOLOv8n sobre ``data/video_cicatriz/data.yaml`` (Fase 1; classes
``ferida_ok``/``ferida_alerta``), avalia (mAP@0.5, precisão, recall) e salva o melhor peso +
``metrics.json`` em ``ai-service/models/cicatriz/``.

Uso (a partir de ai-service/):
    python -m app.cicatriz.treino --epochs 20 --imgsz 320
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from app.common import data_dir, get_logger, models_dir, salvar_metricas

LOG = get_logger("cicatriz")

MODELO_BASE = "yolov8n.pt"


def extrair_metricas(results_csv) -> dict:
    """Extrai mAP@0.5, precisão e recall (agregados) do ``results.csv`` do Ultralytics."""
    import pandas as pd

    df = pd.read_csv(results_csv)
    df.columns = [c.strip() for c in df.columns]
    ultima = df.iloc[-1]

    def _busca(*chaves):
        for chave in chaves:
            if chave in df.columns:
                return round(float(ultima[chave]), 4)
        return None

    return {
        "mAP50": _busca("metrics/mAP50(B)", "metrics/mAP_0.5"),
        "precisao": _busca("metrics/precision(B)", "metrics/precision"),
        "recall": _busca("metrics/recall(B)", "metrics/recall"),
        "epocas": int(ultima.get("epoch", len(df))),
    }


def _data_yaml_absoluto(data_yaml: Path) -> Path:
    """Reescreve o ``data.yaml`` com ``path`` absoluto (o Ultralytics resolve relativo ao CWD)."""
    import yaml

    cfg = yaml.safe_load(data_yaml.read_text(encoding="utf-8"))
    base = data_dir("video_cicatriz")
    cfg["path"] = str(base)
    destino = base / "data_abs.yaml"
    destino.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return destino


def treinar(data_yaml=None, *, epochs: int = 20, imgsz: int = 320, modelo: str = MODELO_BASE):
    """Treina o YOLOv8 e devolve ``(caminho_best_pt, metricas, metricas_por_classe)``."""
    from ultralytics import YOLO

    if data_yaml is None:
        data_yaml = data_dir("video_cicatriz") / "data.yaml"
    data_yaml = Path(data_yaml)
    if not data_yaml.exists():
        raise FileNotFoundError(
            f"{data_yaml} não encontrado. Rode a Fase 1: python -m scripts.data_prep.cicatriz_yolo"
        )
    data_yaml = _data_yaml_absoluto(data_yaml)

    yolo = YOLO(modelo)
    resultados = yolo.train(
        data=str(data_yaml), epochs=epochs, imgsz=imgsz, project="runs_cicatriz", name="train",
        exist_ok=True, verbose=False,
    )
    save_dir = Path(resultados.save_dir)
    metricas = extrair_metricas(save_dir / "results.csv")

    # Métricas por classe (a partir da validação).
    val = yolo.val(data=str(data_yaml), imgsz=imgsz, verbose=False)
    nomes = val.names if hasattr(val, "names") else {}
    por_classe = {}
    try:
        for i, ap in zip(val.box.ap_class_index, val.box.maps, strict=False):
            por_classe[nomes.get(int(i), str(i))] = round(float(ap), 4)
    except Exception:  # pragma: no cover - depende da versão do ultralytics
        pass
    metricas["mAP_por_classe"] = por_classe
    return save_dir / "weights" / "best.pt", metricas, por_classe


def main() -> int:
    parser = argparse.ArgumentParser(description="Treino do detector de cicatriz (YOLOv8).")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--imgsz", type=int, default=320)
    args = parser.parse_args()

    try:
        best_pt, metricas, _ = treinar(epochs=args.epochs, imgsz=args.imgsz)
    except FileNotFoundError as exc:
        LOG.error("%s", exc)
        return 1
    except ImportError:
        LOG.error("ultralytics não instalado. Rode: pip install -r ai-service/requirements.txt")
        return 1

    saida = models_dir("cicatriz")
    if Path(best_pt).exists():
        shutil.copy2(best_pt, saida / "best.pt")
    salvar_metricas(saida / "metrics.json", metricas)
    LOG.info("Treino concluído. mAP50=%s precisão=%s recall=%s",
             metricas.get("mAP50"), metricas.get("precisao"), metricas.get("recall"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
