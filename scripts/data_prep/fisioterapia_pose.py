"""Fisioterapia / recuperação — preparação para YOLOv8-pose (P3).

Prepara amostras de exercícios de reabilitação (UCO PhyRehab / IntelliRehabDS) para estimativa de
pose, reaproveitando os keypoints fornecidos quando existirem, e rotula repetições como
``correto``/``incorreto``. Grava ``data/video_fisioterapia/metadados.json``.

Uso:
    python -m scripts.data_prep.fisioterapia_pose
"""

from __future__ import annotations

import sys

from .common import data_dir, ffmpeg_disponivel, get_logger, write_json

LOG = get_logger("fisioterapia")

EXECUCOES = ("correto", "incorreto")


def validar_execucao(rotulo: str) -> str:
    if rotulo not in EXECUCOES:
        raise ValueError(f"Execução inválida: {rotulo!r}. Use uma de {EXECUCOES}.")
    return rotulo


def montar_metadado(arquivo: str, exercicio: str, execucao: str, keypoints_ref: str | None) -> dict:
    """Monta um registro de metadado de uma amostra de fisioterapia (função pura)."""
    validar_execucao(execucao)
    return {
        "arquivo": arquivo,
        "exercicio": exercicio,
        "execucao": execucao,
        "keypoints_ref": keypoints_ref,
    }


def extrair_frames(video, destino, fps: int = 2):
    """Extrai frames de um vídeo curto via OpenCV (intervalo por ``fps``)."""
    import cv2

    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise FileNotFoundError(f"Vídeo não encontrado/ilegível: {video}")
    destino.mkdir(parents=True, exist_ok=True)
    taxa = cap.get(cv2.CAP_PROP_FPS) or 30
    passo = max(1, int(taxa // max(1, fps)))
    i = salvos = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i % passo == 0:
            cv2.imwrite(str(destino / f"frame_{salvos:04d}.jpg"), frame)
            salvos += 1
        i += 1
    cap.release()
    return salvos


def main() -> int:
    pasta = data_dir("video_fisioterapia")
    LOG.info(
        "Baixe amostras de exercícios (UCO PhyRehab/IntelliRehabDS) para %s — ver data/README.md.",
        pasta,
    )
    if not ffmpeg_disponivel():
        LOG.info("ffmpeg não encontrado: extração de frames usará OpenCV.")

    videos = sorted([*pasta.glob("*.mp4"), *pasta.glob("*.avi")])
    registros = []
    for video in videos:
        keypoints = video.with_suffix(".json")
        registros.append(
            montar_metadado(
                arquivo=video.name,
                exercicio=video.stem,
                execucao="correto",
                keypoints_ref=keypoints.name if keypoints.exists() else None,
            )
        )

    write_json(pasta / "metadados.json", registros)
    if not registros:
        LOG.error("Nenhuma amostra de fisioterapia encontrada em %s.", pasta)
        return 1
    LOG.info("metadados.json escrito com %d amostras.", len(registros))
    return 0


if __name__ == "__main__":
    sys.exit(main())
