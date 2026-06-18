"""Cicatriz da cesárea — download de amostra do AZH Wound e conversão para o formato YOLOv8.

Baixa o ``Test.zip`` do AZH Wound (~4 MB), extrai algumas amostras, converte para o formato YOLOv8
e gera uma imagem com as anotações sobrepostas. Funções de conversão são puras (testáveis sem IO).

Classes (proxy documentado): ``ferida_ok`` (0) <- pele normal (pasta ``N``);
``ferida_alerta`` (1) <- ferida cirúrgica visível (pasta ``S``).

Uso:
    python -m scripts.data_prep.cicatriz_yolo

Observação de domínio: o AZH Wound é uma base de *classificação* por tipo de ferida e não rotula
infecção. Para o mini-dataset usamos ``N`` (sem ferida) vs ``S`` (ferida cirúrgica) como proxy de
``ferida_ok``/``ferida_alerta``, gerando uma caixa por imagem. Limitação registrada no README.
"""

from __future__ import annotations

import sys
import zipfile

from .common import data_dir, download, get_logger

LOG = get_logger("cicatriz_yolo")

CLASSES = ["ferida_ok", "ferida_alerta"]

AZH_ZIP_URL = (
    "https://raw.githubusercontent.com/uwm-bigdata/"
    "wound-classification-using-images-and-locations/main/dataset/Test.zip"
)
# Pasta da classe no zip -> (nome da nossa classe, id). Demais pastas (BG/D/P/V) são ignoradas.
MAPA_CLASSES_AZH: dict[str, tuple[str, int]] = {
    "N": ("ferida_ok", 0),
    "S": ("ferida_alerta", 1),
}


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
        "names": dict(enumerate(classes)),
    }


def escrever_data_yaml(caminho_base, classes: list[str] | None = None):
    """Escreve o ``data.yaml`` em ``data/video_cicatriz/data.yaml``."""
    import yaml

    destino = data_dir("video_cicatriz") / "data.yaml"
    conteudo = montar_data_yaml(str(caminho_base), classes)
    destino.write_text(yaml.safe_dump(conteudo, sort_keys=False, allow_unicode=True), "utf-8")
    return destino


def baixar_amostras(n_por_classe: int = 3, overwrite: bool = False) -> list[tuple]:
    """Baixa o Test.zip do AZH Wound e extrai ``n_por_classe`` imagens de N e S.

    Retorna uma lista de ``(caminho_imagem, class_id, nome_classe)``.
    """
    base = data_dir("video_cicatriz")
    img_dir = base / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    zip_path = base / "_azh_test.zip"
    LOG.info("Baixando amostra do AZH Wound (Test.zip ~4 MB)...")
    download(AZH_ZIP_URL, zip_path, overwrite=overwrite)

    extraidas: list[tuple] = []
    with zipfile.ZipFile(zip_path) as zf:
        nomes = [n for n in zf.namelist() if not n.startswith("__MACOSX")]
        for pasta, (nome_classe, class_id) in MAPA_CLASSES_AZH.items():
            imgs = sorted(
                n for n in nomes
                if n.startswith(f"Test/{pasta}/") and n.lower().endswith((".jpg", ".jpeg", ".png"))
            )[:n_por_classe]
            for i, origem in enumerate(imgs, start=1):
                destino = img_dir / f"{nome_classe}_{i:02d}.jpg"
                with zf.open(origem) as src, open(destino, "wb") as out:
                    out.write(src.read())
                extraidas.append((destino, class_id, nome_classe))

    LOG.info("Extraídas %d amostras para %s", len(extraidas), img_dir)
    return extraidas


def converter_amostras(amostras: list[tuple]) -> list:
    """Gera os rótulos YOLO (.txt) para cada amostra extraída (1 caixa = imagem inteira)."""
    from PIL import Image

    base = data_dir("video_cicatriz")
    label_dir = base / "labels"
    label_dir.mkdir(parents=True, exist_ok=True)

    labels = []
    for caminho, class_id, _nome in amostras:
        with Image.open(caminho) as im:
            w, h = im.size
        linha = caixa_imagem_inteira(w, h, class_id, margem=0.02)
        destino = label_dir / (caminho.stem + ".txt")
        destino.write_text(linha + "\n", encoding="utf-8")
        labels.append(destino)
    return labels


def visualizar(img_path, label_path, destino):
    """Desenha as caixas YOLO de ``label_path`` sobre ``img_path`` e salva em ``destino``."""
    from PIL import Image, ImageDraw

    im = Image.open(img_path).convert("RGB")
    w, h = im.size
    draw = ImageDraw.Draw(im)
    for linha in label_path.read_text(encoding="utf-8").splitlines():
        partes = linha.split()
        if len(partes) != 5:
            continue
        cls, cx, cy, bw, bh = partes
        cx, cy, bw, bh = float(cx) * w, float(cy) * h, float(bw) * w, float(bh) * h
        x1, y1, x2, y2 = cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2
        cor = (255, 0, 0) if cls == "1" else (0, 200, 0)
        draw.rectangle([x1, y1, x2, y2], outline=cor, width=3)
        draw.text((x1 + 4, max(0, y1 + 2)), CLASSES[int(cls)], fill=cor)
    im.save(destino)
    return destino


def main() -> int:
    base = data_dir("video_cicatriz")
    try:
        amostras = baixar_amostras()
    except Exception as exc:
        LOG.error("Falha no download/extração do AZH Wound: %s", exc)
        return 1

    if not amostras:
        LOG.error("Nenhuma amostra extraída do AZH Wound.")
        return 1

    converter_amostras(amostras)
    # Caminho relativo no data.yaml para portabilidade (versionado).
    caminho_yaml = escrever_data_yaml("data/video_cicatriz")
    LOG.info("Rótulos YOLO + %s escritos.", caminho_yaml.name)

    # Visualiza a primeira amostra de alerta (ou a primeira disponível).
    alerta = next((a for a in amostras if a[1] == 1), amostras[0])
    img = alerta[0]
    preview = base / f"preview_{img.stem}.jpg"
    try:
        visualizar(img, base / "labels" / (img.stem + ".txt"), preview)
        LOG.info("Visualização salva em %s", preview)
    except Exception as exc:
        LOG.error("Não foi possível gerar a visualização: %s", exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
