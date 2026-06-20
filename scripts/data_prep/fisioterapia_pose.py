"""Fisioterapia / recuperação — preparação do IntelliRehabDS para análise de pose (P3).

Detecta amostras em ``data/video_fisioterapia/`` em três formatos:
- **sequências de imagens de profundidade** (DepthImages): cada *pasta de gesto* com frames
  ``.png``/``.jpg`` vira UMA amostra;
- **esqueletos/keypoints** do IntelliRehabDS (``.csv``/``.txt``, pastas RawData/Simplified);
- **vídeos** (``.mp4``/``.avi``/...).

A execução (``correto``/``incorreto``) e demais metadados são extraídos do nome no padrão
IntelliRehabDS ``SubjectID_DateID_GestureLabel_RepetitionNumber_CorrectLabel_Position``
(``CorrectLabel`` 1=correto, 2=incorreto). Grava ``metadados.json``.

Uso:
    python -m scripts.data_prep.fisioterapia_pose
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from .common import data_dir, ffmpeg_disponivel, get_logger, write_json

LOG = get_logger("fisioterapia")

EXECUCOES = ("correto", "incorreto")

VIDEO_EXTS = (".mp4", ".avi", ".mov", ".mkv", ".webm")
SKELETON_EXTS = (".csv", ".txt", ".json")
IMG_EXTS = (".png", ".jpg", ".jpeg", ".bmp")


def validar_execucao(rotulo: str) -> str:
    if rotulo not in EXECUCOES:
        raise ValueError(f"Execução inválida: {rotulo!r}. Use uma de {EXECUCOES}.")
    return rotulo


def parse_intellirehab(nome_base: str) -> dict | None:
    """Parseia o nome no padrão IntelliRehabDS (ou None se não casar).

    Padrão: ``SubjectID_DateID_GestureLabel_RepetitionNumber_CorrectLabel_Position``.
    """
    tokens = nome_base.split("_")
    if len(tokens) >= 6 and tokens[4] in ("1", "2"):
        return {
            "subject": tokens[0],
            "date": tokens[1],
            "gesture": tokens[2],
            "repeticao": tokens[3],
            "correct_label": tokens[4],
            "position": "_".join(tokens[5:]),
        }
    return None


def inferir_execucao(nome_arquivo: str) -> str:
    """Infere a execução: usa o CorrectLabel do padrão IntelliRehabDS; senão palavras-chave."""
    info = parse_intellirehab(Path(nome_arquivo).name)
    if info:
        return "correto" if info["correct_label"] == "1" else "incorreto"
    base = nome_arquivo.lower()
    if "incorr" in base or "errad" in base or "_inc" in base:
        return "incorreto"
    return "correto"


def montar_metadado(
    arquivo: str,
    exercicio: str,
    execucao: str,
    keypoints_ref: str | None,
    *,
    extras: dict | None = None,
) -> dict:
    """Monta um registro de metadado de uma amostra de fisioterapia (função pura)."""
    validar_execucao(execucao)
    registro = {
        "arquivo": arquivo,
        "exercicio": exercicio,
        "execucao": execucao,
        "keypoints_ref": keypoints_ref,
    }
    if extras:
        registro.update(extras)
    return registro


def _extras_intellirehab(nome_base: str) -> dict:
    """Extras (subject/gesture/position/repeticao) quando o nome segue o padrão IntelliRehabDS."""
    info = parse_intellirehab(nome_base)
    if not info:
        return {}
    return {
        "subject": info["subject"],
        "gesture": info["gesture"],
        "repeticao": info["repeticao"],
        "position": info["position"],
    }


def coletar_amostras(pasta: Path) -> list[dict]:
    """Varre a pasta (recursiva) e monta um metadado por amostra (sequência/esqueleto/vídeo)."""
    registros: list[dict] = []
    for root, _dirs, files in os.walk(pasta):
        rootp = Path(root)
        nomes = [f for f in files if not f.startswith(".")]
        imgs = [f for f in nomes if Path(f).suffix.lower() in IMG_EXTS]
        skeletons = [
            f for f in nomes
            if Path(f).suffix.lower() in SKELETON_EXTS and f != "metadados.json"
        ]
        videos = [f for f in nomes if Path(f).suffix.lower() in VIDEO_EXTS]

        # 1) Pasta de gesto com frames de profundidade -> 1 amostra (sequência).
        if imgs and rootp != pasta:
            rel = rootp.relative_to(pasta).as_posix()
            registros.append(
                montar_metadado(
                    arquivo=rel,
                    exercicio=rootp.name,
                    execucao=inferir_execucao(rootp.name),
                    keypoints_ref=None,
                    extras={"tipo": "sequencia_depth", "n_frames": len(imgs),
                            **_extras_intellirehab(rootp.name)},
                )
            )

        # 2) Esqueletos/keypoints (RawData/Simplified) -> 1 amostra por arquivo.
        for f in skeletons:
            rel = (rootp / f).relative_to(pasta).as_posix()
            registros.append(
                montar_metadado(
                    arquivo=rel,
                    exercicio=Path(f).stem,
                    execucao=inferir_execucao(f),
                    keypoints_ref=rel,
                    extras={"tipo": "esqueleto", **_extras_intellirehab(Path(f).stem)},
                )
            )

        # 3) Vídeos -> 1 amostra por arquivo.
        for f in videos:
            rel = (rootp / f).relative_to(pasta).as_posix()
            registros.append(
                montar_metadado(
                    arquivo=rel,
                    exercicio=Path(f).stem,
                    execucao=inferir_execucao(f),
                    keypoints_ref=None,
                    extras={"tipo": "video", **_extras_intellirehab(Path(f).stem)},
                )
            )

    registros.sort(key=lambda r: r["arquivo"])
    return registros


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

    registros = coletar_amostras(pasta)
    if not registros:
        LOG.error(
            "Nenhuma amostra (sequência de imagens, esqueleto %s ou vídeo %s) em %s. "
            "Adicione dados do IntelliRehabDS (Zenodo) — ver data/README.md.",
            "/".join(SKELETON_EXTS), "/".join(VIDEO_EXTS), pasta,
        )
        _diagnostico_pasta(pasta)
        return 1

    write_json(pasta / "metadados.json", registros)
    n_seq = sum(1 for r in registros if r.get("tipo") == "sequencia_depth")
    LOG.info("metadados.json escrito com %d amostra(s) (%d sequências de imagem).",
             len(registros), n_seq)
    return 0


if __name__ == "__main__":
    sys.exit(main())
