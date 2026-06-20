"""Áudio — transcrição e rotulação das amostras de consulta/relato.

Detecta **qualquer** arquivo de áudio presente em ``data/audio/`` (não exige nomes fixos),
transcreve com Whisper local (padrão) ou Azure Speech-to-Text (``AUDIO_BACKEND=azure``) e grava
``data/audio/metadados.json``. A categoria é inferida pelo nome do arquivo (ajustável depois).

Uso:
    python -m scripts.data_prep.audio_transcrever
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from .common import data_dir, ffmpeg_disponivel, get_logger, write_json

LOG = get_logger("audio")

# Formatos que o libsndfile (soundfile) lê sem ffmpeg.
SOUNDFILE_EXTS = (".wav", ".flac", ".ogg", ".aiff", ".aif")

# Categorias alinhadas ao contrato de API (docs/contrato-api.md).
CATEGORIAS = ["neutro", "ansiedade", "depressao_pos_parto", "violencia", "fadiga"]

# Extensões de áudio reconhecidas.
AUDIO_EXTS = (".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".opus", ".wma")

# Palavra-chave no nome do arquivo -> categoria (primeira que casar).
PALAVRAS_CATEGORIA: dict[str, str] = {
    "neutro": "neutro",
    "ansiedade": "ansiedade",
    "depress": "depressao_pos_parto",
    "pos_parto": "depressao_pos_parto",
    "violenc": "violencia",
    "fadiga": "fadiga",
}


def validar_categoria(categoria: str) -> str:
    if categoria not in CATEGORIAS:
        raise ValueError(f"Categoria inválida: {categoria!r}. Use uma de {CATEGORIAS}.")
    return categoria


def inferir_categoria(nome_arquivo: str) -> str | None:
    """Infere a categoria a partir do nome/caminho do arquivo (ou None se não reconhecer)."""
    base = nome_arquivo.lower().replace("\\", "/")
    for chave, categoria in PALAVRAS_CATEGORIA.items():
        if chave in base:
            return categoria
    # Androids Corpus: pasta "HC" = healthy control (saudável -> neutro).
    if "hc" in base.split("/"):
        return "neutro"
    return None


def listar_audios(pasta: Path) -> list[Path]:
    """Lista arquivos de áudio na pasta e subpastas (qualquer nome, extensões conhecidas)."""
    return sorted(
        p
        for p in pasta.rglob("*")
        if p.is_file() and p.suffix.lower() in AUDIO_EXTS and not p.name.startswith(".")
    )


def _diagnostico_pasta(pasta: Path, limite: int = 10) -> None:
    """Lista (no log) os arquivos realmente presentes, para ajudar a diagnosticar extensões."""
    presentes = [p for p in pasta.rglob("*") if p.is_file() and not p.name.startswith(".")]
    if not presentes:
        LOG.error("A pasta %s está vazia (nem subpastas com arquivos).", pasta)
        return
    LOG.error("Arquivos encontrados na pasta (%d), mas sem extensão de áudio:", len(presentes))
    for p in presentes[:limite]:
        LOG.error("  - %s", p.relative_to(pasta).as_posix())


def _carregar_audio_16k(caminho):
    """Decodifica um áudio para mono float32 a 16 kHz usando soundfile (sem ffmpeg)."""
    import numpy as np
    import soundfile as sf

    data, sr = sf.read(str(caminho), dtype="float32", always_2d=False)
    if getattr(data, "ndim", 1) > 1:
        data = data.mean(axis=1)
    if sr != 16000 and len(data) > 0:
        n = int(round(len(data) * 16000 / sr))
        x_antigo = np.linspace(0.0, 1.0, num=len(data), endpoint=False)
        x_novo = np.linspace(0.0, 1.0, num=n, endpoint=False)
        data = np.interp(x_novo, x_antigo, data).astype(np.float32)
    return np.ascontiguousarray(data, dtype=np.float32)


def transcrever_whisper(caminho, modelo: str = "base") -> str:
    """Transcreve um áudio com Whisper local.

    Whisper normalmente usa ffmpeg para decodificar. Se o ffmpeg não estiver disponível e o
    formato for legível pelo soundfile (wav/flac/ogg/aiff), decodifica via soundfile e passa o
    array ao Whisper — evitando a dependência do ffmpeg.
    """
    import whisper

    caminho = Path(caminho)
    model = whisper.load_model(modelo)
    if not ffmpeg_disponivel() and caminho.suffix.lower() in SOUNDFILE_EXTS:
        audio = _carregar_audio_16k(caminho)
        resultado = model.transcribe(audio)
    else:
        resultado = model.transcribe(str(caminho))
    return str(resultado.get("text", "")).strip()


def transcrever_azure(caminho) -> str:
    """Transcreve com Azure Speech-to-Text (requer SDK e credenciais via env)."""
    chave = os.environ.get("AZURE_SPEECH_KEY")
    regiao = os.environ.get("AZURE_SPEECH_REGION")
    if not (chave and regiao):
        raise RuntimeError(
            "AZURE_SPEECH_KEY/AZURE_SPEECH_REGION não definidos para o backend Azure."
        )
    import azure.cognitiveservices.speech as speechsdk  # pragma: no cover

    cfg = speechsdk.SpeechConfig(subscription=chave, region=regiao)  # pragma: no cover
    audio = speechsdk.AudioConfig(filename=str(caminho))  # pragma: no cover
    rec = speechsdk.SpeechRecognizer(speech_config=cfg, audio_config=audio)  # pragma: no cover
    return rec.recognize_once().text  # pragma: no cover


def transcrever(caminho) -> str:
    """Transcreve usando o backend configurado em ``AUDIO_BACKEND`` (whisper|azure)."""
    backend = os.environ.get("AUDIO_BACKEND", "whisper").lower()
    if backend == "azure":
        return transcrever_azure(caminho)
    return transcrever_whisper(caminho)


def main() -> int:
    pasta = data_dir("audio")
    audios = listar_audios(pasta)

    if not audios:
        LOG.error(
            "Nenhum arquivo de áudio (%s) em %s (busca recursiva). "
            "Adicione gravações/TTS — ver data/README.md.",
            "/".join(AUDIO_EXTS), pasta,
        )
        _diagnostico_pasta(pasta)
        return 1

    registros = []
    sem_rotulo = []
    for caminho in audios:
        rel = caminho.relative_to(pasta).as_posix()
        categoria = inferir_categoria(rel) or "nao_rotulado"
        if categoria == "nao_rotulado":
            sem_rotulo.append(rel)
        LOG.info("Transcrevendo %s (%s)...", rel, categoria)
        try:
            texto = transcrever(caminho)
        except Exception as exc:
            dica = ""
            if "ffmpeg" in str(exc).lower():
                dica = (
                    " Instale o ffmpeg (macOS: 'brew install ffmpeg') ou o pacote 'soundfile' "
                    "(pip install soundfile) para formatos wav/flac/ogg."
                )
            LOG.warning("Transcrição de %s falhou (%s); registrando sem texto.%s", rel, exc, dica)
            texto = ""
        registros.append({"arquivo": rel, "transcricao": texto, "categoria": categoria})

    write_json(pasta / "metadados.json", registros)
    LOG.info("metadados.json escrito com %d áudio(s).", len(registros))
    if sem_rotulo:
        LOG.warning(
            "Sem categoria inferida para: %s. Ajuste 'categoria' em metadados.json "
            "(use o nome do arquivo com a palavra-chave, ex.: relato_ansiedade.wav).",
            ", ".join(sem_rotulo),
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
