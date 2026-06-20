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

from .common import data_dir, get_logger, write_json

LOG = get_logger("audio")

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
    """Infere a categoria a partir do nome do arquivo (ou None se não reconhecer)."""
    base = nome_arquivo.lower()
    for chave, categoria in PALAVRAS_CATEGORIA.items():
        if chave in base:
            return categoria
    return None


def listar_audios(pasta: Path) -> list[Path]:
    """Lista todos os arquivos de áudio na pasta (qualquer nome, extensões conhecidas)."""
    return sorted(p for p in pasta.iterdir() if p.suffix.lower() in AUDIO_EXTS)


def transcrever_whisper(caminho, modelo: str = "base") -> str:
    """Transcreve um áudio com Whisper local."""
    import whisper

    model = whisper.load_model(modelo)
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
            "Nenhum arquivo de áudio (%s) em %s. Adicione gravações/TTS — ver data/README.md.",
            "/".join(AUDIO_EXTS), pasta,
        )
        return 1

    registros = []
    sem_rotulo = []
    for caminho in audios:
        categoria = inferir_categoria(caminho.name) or "nao_rotulado"
        if categoria == "nao_rotulado":
            sem_rotulo.append(caminho.name)
        LOG.info("Transcrevendo %s (%s)...", caminho.name, categoria)
        try:
            texto = transcrever(caminho)
        except Exception as exc:
            LOG.warning("Transcrição de %s falhou (%s); registrando sem texto.", caminho.name, exc)
            texto = ""
        registros.append(
            {"arquivo": caminho.name, "transcricao": texto, "categoria": categoria}
        )

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
