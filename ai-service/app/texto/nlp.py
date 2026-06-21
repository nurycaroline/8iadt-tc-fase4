"""Texto clínico (NLP) — análise por palavras-chave/regras → evidência padronizada (contrato §3).

Abordagem enxuta e **determinística** (offline, testável): procura termos de risco no texto e
classifica o achado em ``sinal_infeccao`` (sinais de infecção da cicatriz), ``complicacao`` (demais
complicações: pré-eclâmpsia, depressão, etc.) ou ``neutro``. Devolve também o trecho que disparou.

Opcional (não obrigatório): análise de sentimento via Azure Text Analytics, trocável por env var.
"""

from __future__ import annotations

import sys
import unicodedata

from app.common import data_dir, get_logger
from app.schemas import evidencia_texto

LOG = get_logger("texto")

# Termos de **infecção da cicatriz** (têm precedência: achado mais específico).
TERMOS_INFECCAO = (
    "febre",
    "dor na cicatriz",
    "secrecao",
    "purulenta",
    "hiperemia",
    "deiscencia",
    "calor local",
    "sinais flogisticos",
    "pus",
)

# Pistas de negação que precedem um termo (ex.: "sem sinais flogísticos", "nega febre").
NEGACOES = ("sem ", "nega", "ausencia", "ausente", "negativo", "negativa", "descarta")

# Termos de **outras complicações** (pré-eclâmpsia, saúde mental, etc.).
TERMOS_COMPLICACAO = (
    "proteinuria",
    "cefaleia",
    "escotomas",
    "pre-eclampsia",
    "pressao alta",
    "hipertensao",
    "tristeza persistente",
    "anedonia",
    "depressao",
    "ideacao suicida",
    "convulsao",
)


def _normalizar(texto: str) -> str:
    """Minúsculas + remoção de acentos (matching robusto)."""
    nfkd = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _frase_do_termo(texto: str, termo: str) -> str:
    """Retorna a primeira frase do texto original que contém o termo (normalizado)."""
    for frase in texto.replace("\n", " ").split("."):
        if termo in _normalizar(frase):
            return frase.strip()
    return termo


def _termo_presente(norm: str, termo: str) -> bool:
    """True se o termo aparece **não negado** (ex.: ignora 'sem sinais flogísticos')."""
    inicio = 0
    while True:
        idx = norm.find(termo, inicio)
        if idx == -1:
            return False
        janela = norm[max(0, idx - 25):idx]
        if not any(neg in janela for neg in NEGACOES):
            return True
        inicio = idx + len(termo)


def analisar(texto: str) -> dict:
    """Classifica o achado de risco de um texto clínico (função pura)."""
    norm = _normalizar(texto)
    for termo in TERMOS_INFECCAO:
        if _termo_presente(norm, termo):
            return evidencia_texto("sinal_infeccao", _frase_do_termo(texto, termo))
    for termo in TERMOS_COMPLICACAO:
        if _termo_presente(norm, termo):
            return evidencia_texto("complicacao", _frase_do_termo(texto, termo))
    return evidencia_texto("neutro", "")


def analisar_arquivo(caminho) -> dict:
    """Lê um arquivo de texto e analisa o achado."""
    from pathlib import Path

    return analisar(Path(caminho).read_text(encoding="utf-8"))


def main() -> int:
    """Analisa os documentos de ``data/texto_clinico/`` e imprime os achados."""
    pasta = data_dir("texto_clinico")
    arquivos = sorted(pasta.glob("*.txt"))
    if not arquivos:
        LOG.error(
            "Nenhum .txt em %s. Rode a Fase 1: python -m scripts.data_prep.texto_clinico", pasta
        )
        return 1
    for arq in arquivos:
        evid = analisar_arquivo(arq)
        LOG.info("%s -> %s", arq.name, evid["achado"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
