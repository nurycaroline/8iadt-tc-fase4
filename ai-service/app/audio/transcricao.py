"""Transcrição de áudio (ASR) — **local/offline** (Fase 8), reusando a implementação da Fase 1.

Whisper local por padrão (``openai-whisper``); ``faster-whisper`` como alternativa selecionável. A
lógica (incl. fallback via ``soundfile`` sem ffmpeg) vive em
``scripts/data_prep/audio_transcrever.py`` e é reusada aqui para não duplicar código.
"""

from __future__ import annotations

from app.common import get_logger

LOG = get_logger("audio")


def transcrever(caminho) -> str:
    """Transcreve um áudio reusando o transcritor da Fase 1 (Whisper/Azure)."""
    try:
        from scripts.data_prep.audio_transcrever import transcrever as _transcrever
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Transcritor da Fase 1 indisponível. Instale as deps de áudio: "
            "pip install -r ai-service/requirements.txt"
        ) from exc
    return _transcrever(caminho)
