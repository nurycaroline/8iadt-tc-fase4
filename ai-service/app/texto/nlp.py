"""Texto clínico (NLP) — análise **unificada** da Fase 8 (local/offline).

Combina três sinais numa única evidência (contrato §3, Fase 8):

- ``achado`` — infecção da cicatriz / complicação obstétrica / neutro, por **palavras-chave**
  determinísticas (preservadas das fases anteriores);
- ``depressao`` — classificador **ML** (TF-IDF + LogisticRegression treinado em PT-BR);
- ``violencia`` — classificador **ML** (idem), com geração de negativos no pipeline de dados.

A depressão deixou de cair em ``complicacao`` (keyword): agora vive no sinal ``depressao`` para
evitar dupla contagem na fusão. Se os modelos ML não estiverem presentes (pesos não versionados), a
detecção de depressão/violência **degrada para palavras-chave** (DD10), sem quebrar.
"""

from __future__ import annotations

import sys
import unicodedata
from typing import Any

from app.common import data_dir, get_logger
from app.ml_utils import carregar_modelo
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

# Termos de **complicações obstétricas** (pré-eclâmpsia, hipertensão, convulsão). A depressão saiu
# daqui na Fase 8 (passou para o classificador ML em ``depressao``).
TERMOS_COMPLICACAO = (
    "proteinuria",
    "cefaleia",
    "escotomas",
    "pre-eclampsia",
    "pressao alta",
    "hipertensao",
    "convulsao",
)

# Fallback por palavras-chave do classificador de **depressão** (quando o modelo ML falta).
TERMOS_DEPRESSAO = (
    "tristeza",
    "tristeza persistente",
    "vontade de chorar",
    "choro o tempo todo",
    "nao sinto prazer",
    "sem vontade",
    "vazio",
    "desanimo",
    "nao consigo cuidar",
    "me sinto culpada",
    "nao tenho vinculo",
    "anedonia",
    "depressao",
    "ideacao suicida",
    "sem esperanca",
)

# Fallback por palavras-chave do classificador de **violência** (quando o modelo ML falta).
TERMOS_VIOLENCIA = (
    "me bateu",
    "bateu em mim",
    "apanhei",
    "agrediu",
    "me agride",
    "ameaca",
    "ameacou",
    "tenho medo dele",
    "me empurrou",
    "violencia",
    "me machucou",
    "agressao",
    "abuso",
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


def _achado_keywords(texto: str, norm: str) -> tuple[str, str]:
    """Achado clínico por keywords: infecção (precede) > complicação > neutro."""
    for termo in TERMOS_INFECCAO:
        if _termo_presente(norm, termo):
            return "sinal_infeccao", _frase_do_termo(texto, termo)
    for termo in TERMOS_COMPLICACAO:
        if _termo_presente(norm, termo):
            return "complicacao", _frase_do_termo(texto, termo)
    return "neutro", ""


def _classificar_ml(texto: str, nome: str, rotulo_positivo: str) -> tuple[str, float] | None:
    """Classifica binário via modelo ML salvo (``models/texto/<nome>.joblib``) ou ``None``."""
    bundle = carregar_modelo("texto", nome)
    if bundle is None:
        return None
    try:
        pipeline = bundle["pipeline"]
        classes = list(pipeline.classes_)
        proba = pipeline.predict_proba([texto])[0]
        idx_pos = classes.index(1) if 1 in classes else classes.index(rotulo_positivo)
        conf_pos = float(proba[idx_pos])
    except Exception as exc:  # pragma: no cover - robustez de ambiente
        LOG.warning("Inferência ML (%s) falhou (%s); usando fallback por keywords.", nome, exc)
        return None
    if conf_pos >= 0.5:
        return rotulo_positivo, conf_pos
    return "neutro", round(1.0 - conf_pos, 4)


def _classificar_keywords(
    norm: str, termos: tuple[str, ...], rotulo_positivo: str
) -> tuple[str, float]:
    """Fallback determinístico: confiança cresce com o nº de termos encontrados."""
    n = sum(1 for termo in termos if _termo_presente(norm, termo))
    if n == 0:
        return "neutro", 0.0
    return rotulo_positivo, round(min(0.55 + 0.15 * n, 0.9), 4)


def _detectar(
    texto: str, norm: str, nome: str, termos: tuple[str, ...], rotulo_positivo: str
) -> tuple[str, float]:
    """Tenta o classificador ML; se ausente, cai no fallback por palavras-chave."""
    ml = _classificar_ml(texto, nome, rotulo_positivo)
    if ml is not None:
        return ml
    return _classificar_keywords(norm, termos, rotulo_positivo)


def analisar(texto: str) -> dict[str, Any]:
    """Analisa um texto clínico e devolve a evidência unificada da Fase 8 (função pura)."""
    texto = texto or ""
    norm = _normalizar(texto)
    achado, trecho = _achado_keywords(texto, norm)
    depressao = _detectar(texto, norm, "depressao", TERMOS_DEPRESSAO, "depressao")
    violencia = _detectar(texto, norm, "violencia", TERMOS_VIOLENCIA, "violencia")
    return evidencia_texto(achado, trecho, depressao=depressao, violencia=violencia)


def analisar_arquivo(caminho) -> dict[str, Any]:
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
        LOG.info(
            "%s -> achado=%s depressao=%s violencia=%s",
            arq.name,
            evid["achado"],
            evid["depressao"]["rotulo"],
            evid["violencia"]["rotulo"],
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
