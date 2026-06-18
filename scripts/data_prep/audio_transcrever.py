"""Áudio — transcrição e rotulação das amostras de consulta/relato.

Transcreve 5 áudios curtos (categorias-alvo) com Whisper local (padrão) ou Azure Speech-to-Text
(se ``AUDIO_BACKEND=azure`` e credenciais via env) e grava ``data/audio/metadados.json``.

Uso:
    python -m scripts.data_prep.audio_transcrever
"""

from __future__ import annotations

import os
import sys

from .common import data_dir, get_logger, write_json

LOG = get_logger("audio")

# Categorias alinhadas ao contrato de API (docs/contrato-api.md).
CATEGORIAS = ["neutro", "ansiedade", "depressao_pos_parto", "violencia", "fadiga"]

# Áudios esperados (1 por categoria). O arquivo deve ser colocado em data/audio/ pelo usuário
# (gravação própria/TTS) ou obtido de Androids/DEPAC — ver data/README.md.
AMOSTRAS_ESPERADAS = {
    "consulta_neutro.wav": "neutro",
    "relato_ansiedade.wav": "ansiedade",
    "relato_depressao.wav": "depressao_pos_parto",
    "relato_violencia.wav": "violencia",
    "relato_fadiga.wav": "fadiga",
}


def validar_categoria(categoria: str) -> str:
    if categoria not in CATEGORIAS:
        raise ValueError(f"Categoria inválida: {categoria!r}. Use uma de {CATEGORIAS}.")
    return categoria


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
    registros = []
    faltando = []

    for arquivo, categoria in AMOSTRAS_ESPERADAS.items():
        caminho = pasta / arquivo
        validar_categoria(categoria)
        if not caminho.exists():
            faltando.append(arquivo)
            continue
        LOG.info("Transcrevendo %s (%s)...", arquivo, categoria)
        try:
            texto = transcrever(caminho)
        except Exception as exc:
            LOG.error("Falha ao transcrever %s: %s", arquivo, exc)
            continue
        registros.append({"arquivo": arquivo, "transcricao": texto, "categoria": categoria})

    if faltando:
        LOG.error(
            "Faltam %d áudios em %s: %s. Adicione gravações/TTS conforme data/README.md.",
            len(faltando), pasta, ", ".join(faltando),
        )

    write_json(pasta / "metadados.json", registros)
    LOG.info("metadados.json escrito com %d transcrições.", len(registros))
    return 0 if registros else 1


if __name__ == "__main__":
    sys.exit(main())
