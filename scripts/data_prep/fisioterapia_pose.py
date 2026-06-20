"""Fisioterapia / recuperação — preparação para YOLOv8-pose (P3).

Detecta **qualquer** amostra presente em ``data/video_fisioterapia/``: vídeos de exercício
(``.mp4``, ``.avi``, ...) e/ou esqueletos/keypoints do IntelliRehabDS (``.txt``/``.csv``).
Rotula a execução (``correto``/``incorreto``) inferindo pelo nome e grava ``metadados.json``.

Uso:
    python -m scripts.data_prep.fisioterapia_pose
"""

from __future__ import annotations

import sys
from pathlib import Path

from .common import data_dir, ffmpeg_disponivel, get_logger, write_json

LOG = get_logger("fisioterapia")

EXECUCOES = ("correto", "incorreto")

VIDEO_EXTS = (".mp4", ".avi", ".mov", ".mkv", ".webm")
SKELETON_EXTS = (".txt", ".csv", ".json")


def validar_execucao(rotulo: str) -> str:
    if rotulo not in EXECUCOES:
        raise ValueError(f"Execução inválida: {rotulo!r}. Use uma de {EXECUCOES}.")
    return rotulo


def inferir_execucao(nome_arquivo: str) -> str:
    """Infere a execução pelo nome do arquivo (``incorreto`` se indicado; senão ``correto``)."""
    base = nome_arquivo.lower()
    if "incorr" in base or "errad" in base or "_inc" in base:
        return "incorreto"
    return "correto"


def montar_metadado(arquivo: str, exercicio: str, execucao: str, keypoints_ref: str | None) -> dict:
    """Monta um registro de metadado de uma amostra de fisioterapia (função pura)."""
    validar_execucao(execucao)
    return {
        "arquivo": arquivo,
        "exercicio": exercicio,
        "execucao": execucao,
        "keypoints_ref": keypoints_ref,
    }


def listar_amostras(pasta: Path) -> list[Path]:
    """Lista vídeos e esqueletos na pasta e subpastas (ignora metadados.json e ocultos)."""
    exts = VIDEO_EXTS + SKELETON_EXTS
    return sorted(
        p
        for p in pasta.rglob("*")
        if p.is_file()
        and p.suffix.lower() in exts
        and p.name != "metadados.json"
        and not p.name.startswith(".")
    )


def _diagnostico_pasta(pasta: Path, limite: int = 10) -> None:
    """Lista (no log) os arquivos realmente presentes, para diagnosticar extensões/subpastas."""
    presentes = [
        p
        for p in pasta.rglob("*")
        if p.is_file() and p.name != "metadados.json" and not p.name.startswith(".")
    ]
    if not presentes:
        LOG.error("A pasta %s está vazia (nem subpastas com arquivos).", pasta)
        return
    LOG.error("Arquivos encontrados na pasta (%d), mas sem extensão reconhecida:", len(presentes))
    for p in presentes[:limite]:
        LOG.error("  - %s", p.relative_to(pasta).as_posix())


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
    if not ffmpeg_disponivel():
        LOG.info("ffmpeg não encontrado: extração de frames (se necessária) usará OpenCV.")

    amostras = listar_amostras(pasta)
    if not amostras:
        LOG.error(
            "Nenhuma amostra (%s) em %s (busca recursiva). Adicione vídeos ou esqueletos do "
            "IntelliRehabDS (Zenodo) — ver data/README.md.",
            "/".join(VIDEO_EXTS + SKELETON_EXTS), pasta,
        )
        _diagnostico_pasta(pasta)
        return 1

    registros = []
    for caminho in amostras:
        rel = caminho.relative_to(pasta).as_posix()
        eh_skeleton = caminho.suffix.lower() in SKELETON_EXTS
        keypoints = None
        if eh_skeleton:
            keypoints = rel
        else:
            sidecar = caminho.with_suffix(".json")
            if not sidecar.exists():
                sidecar = caminho.with_suffix(".txt")
            keypoints = sidecar.relative_to(pasta).as_posix() if sidecar.exists() else None
        registros.append(
            montar_metadado(
                arquivo=rel,
                exercicio=caminho.stem,
                execucao=inferir_execucao(rel),
                keypoints_ref=keypoints,
            )
        )

    write_json(pasta / "metadados.json", registros)
    LOG.info("metadados.json escrito com %d amostra(s).", len(registros))
    return 0


if __name__ == "__main__":
    sys.exit(main())
