"""Cicatriz da cesárea — conversão de amostra para o formato YOLOv8.

Funções puras de conversão (testáveis sem IO) + rotina de visualização das anotações.
Classes: ``ferida_ok`` (0) e ``ferida_alerta`` (1, sinal de infecção).

Uso:
    python -m scripts.data_prep.cicatriz_yolo

Observação de domínio: o AZH Wound é uma base de *classificação*. Ao converter para detecção,
geramos uma caixa por imagem cobrindo a ferida (decisão documentada em data/README.md).
"""

from __future__ import annotations

import sys

from .common import data_dir, get_logger

LOG = get_logger("cicatriz_yolo")

CLASSES = ["ferida_ok", "ferida_alerta"]


def bbox_para_yolo(
    x: float, y: float, w: float, h: float, img_w: int, img_h: int, class_id: int
) -> str:
    """Converte uma bounding box absoluta (x,y,w,h em pixels, canto superior esquerdo)
    para uma linha no formato YOLO: ``class cx cy w h`` normalizados em [0,1].
    """
    if img_w <= 0 or img_h <= 0:
        raise ValueError("Dimensões da imagem devem ser positivas.")
    if w < 0 or h < 0:
        raise ValueError("Largura/altura da caixa não podem ser negativas.")

    cx = (x + w / 2) / img_w
    cy = (y + h / 2) / img_h
    nw = w / img_w
    nh = h / img_h

    valores = [cx, cy, nw, nh]
    if any(v < 0 or v > 1 for v in valores):
        raise ValueError("Caixa fora dos limites da imagem após normalização.")

    return f"{class_id} " + " ".join(f"{v:.6f}" for v in valores)


def caixa_imagem_inteira(img_w: int, img_h: int, class_id: int, margem: float = 0.0) -> str:
    """Gera uma caixa cobrindo (quase) toda a imagem, com ``margem`` relativa opcional.

    Usado quando a fonte é de classificação (sem bbox): a imagem inteira é a ferida.
    """
    if not 0 <= margem < 0.5:
        raise ValueError("margem deve estar em [0, 0.5).")
    x = img_w * margem
    y = img_h * margem
    w = img_w * (1 - 2 * margem)
    h = img_h * (1 - 2 * margem)
    return bbox_para_yolo(x, y, w, h, img_w, img_h, class_id)


def montar_data_yaml(caminho_base: str, classes: list[str] | None = None) -> dict:
    """Monta o dicionário ``data.yaml`` no formato Ultralytics (paths + classes)."""
    classes = classes or CLASSES
    return {
        "path": caminho_base,
        "train": "images",
        "val": "images",
        "nc": len(classes),
        "names": {i: nome for i, nome in enumerate(classes)},
    }


def escrever_data_yaml(caminho_base, classes: list[str] | None = None):
    """Escreve o ``data.yaml`` em ``data/video_cicatriz/data.yaml``."""
    import yaml

    destino = data_dir("video_cicatriz") / "data.yaml"
    conteudo = montar_data_yaml(str(caminho_base), classes)
    destino.write_text(yaml.safe_dump(conteudo, sort_keys=False, allow_unicode=True), "utf-8")
    return destino


def visualizar(img_path, label_path, destino):
    """Desenha as caixas YOLO de ``label_path`` sobre ``img_path`` e salva em ``destino``."""
    import cv2

    img = cv2.imread(str(img_path))
    if img is None:
        raise FileNotFoundError(f"Imagem não encontrada/ilegível: {img_path}")
    h, w = img.shape[:2]

    for linha in open(label_path, encoding="utf-8"):
        partes = linha.split()
        if len(partes) != 5:
            continue
        cls, cx, cy, bw, bh = partes
        cx, cy, bw, bh = float(cx) * w, float(cy) * h, float(bw) * w, float(bh) * h
        x1, y1 = int(cx - bw / 2), int(cy - bh / 2)
        x2, y2 = int(cx + bw / 2), int(cy + bh / 2)
        cor = (0, 0, 255) if cls == "1" else (0, 200, 0)
        cv2.rectangle(img, (x1, y1), (x2, y2), cor, 2)
        cv2.putText(img, CLASSES[int(cls)], (x1, max(0, y1 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor, 2)

    cv2.imwrite(str(destino), img)
    return destino


def main() -> int:
    LOG.info("Conversão de cicatriz para YOLOv8.")
    LOG.info(
        "Baixe 1 amostra do AZH Wound (ver data/README.md) para %s e rode a conversão.",
        data_dir("video_cicatriz") / "images",
    )
    caminho = escrever_data_yaml(data_dir("video_cicatriz"))
    LOG.info("data.yaml escrito em %s", caminho)
    return 0


if __name__ == "__main__":
    sys.exit(main())
