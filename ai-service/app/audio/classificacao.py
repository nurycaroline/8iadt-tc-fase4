"""Análise de áudio da Fase 8 — **dupla**: classificador acústico + transcrição→texto unificado.

``inferir(caminho)`` roda duas trilhas independentes e devolve a evidência de áudio unificada
(contrato §3, Fase 8):

1. **Acústico** — classificador de violência no *som* (features MFCC + modelo ``scikit-learn``
   treinado no dataset ``Hemg``). Carregamento **tolerante** (DD10): sem o modelo, a trilha acústica
   fica ``neutro`` e a violência ainda é captada pela trilha de texto.
2. **Transcrição → texto unificado** — transcreve o áudio (Whisper local) e reanalisa como texto
   (``app.texto.nlp.analisar``: depressão ML + violência ML + keywords de infecção/complicação).

A categoria legada (``categoria``/``confianca``) é **derivada** dessas trilhas em
``schemas.evidencia_audio_unificada`` (compatibilidade com a fusão/relatório). A função pura
``classificar(transcricao)`` (palavras-chave) é mantida para o baseline/compat.
"""

from __future__ import annotations

import unicodedata
from typing import Any

from app.common import get_logger
from app.ml_utils import carregar_modelo
from app.schemas import evidencia_audio, evidencia_audio_unificada

LOG = get_logger("audio")

# Ordem = prioridade de desempate (mais grave primeiro). Usado só pela função legada classificar().
TERMOS: dict[str, tuple[str, ...]] = {
    "violencia": (
        "me bateu", "bateu em mim", "apanhei", "agrediu", "me agride", "ameaca",
        "ameacou", "tenho medo dele", "me empurrou", "violencia", "me machucou",
    ),
    "depressao_pos_parto": (
        "tristeza", "vontade de chorar", "choro o tempo todo", "nao sinto prazer",
        "sem vontade", "vazio", "desanimo", "nao consigo cuidar", "me sinto culpada",
        "nao tenho vinculo", "anedonia",
    ),
    "ansiedade": (
        "ansiedade", "ansiosa", "coracao acelerado", "preocupada", "nervosa",
        "aflita", "panico", "angustia", "medo constante",
    ),
    "fadiga": (
        "cansada", "exausta", "sem energia", "esgotada", "nao durmo", "cansaco",
        "muito cansada", "sem forcas",
    ),
}


def _normalizar(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _confianca(n: int) -> float:
    """Confiança crescente com o nº de termos (saturando perto de 1)."""
    return min(0.5 + 0.2 * n, 0.95)


def classificar(transcricao: str) -> dict:
    """Classifica a categoria **legada** de uma transcrição por palavras-chave (função pura).

    Mantida para o baseline (``app.baseline``) e compatibilidade; a inferência principal usa
    :func:`inferir` (análise dupla).
    """
    norm = _normalizar(transcricao or "")
    contagem = {
        cat: sum(1 for termo in termos if termo in norm) for cat, termos in TERMOS.items()
    }
    melhor = max(TERMOS, key=lambda c: contagem[c])  # ordem do dict desempata
    if contagem[melhor] == 0:
        return evidencia_audio("neutro", 0.5)
    return evidencia_audio(melhor, _confianca(contagem[melhor]))


def classificar_acustico(caminho) -> tuple[str, float]:
    """Classifica violência no **som** via modelo ``scikit-learn`` (ou fallback neutro tolerante).

    Sem o modelo treinado (``models/audio/violencia_acustico.joblib``), ou se a extração de features
    falhar, devolve ``("neutro", 0.5)`` — a violência ainda é captada pela trilha de texto (DD10).
    """
    bundle = carregar_modelo("audio", "violencia_acustico")
    if bundle is None:
        return "neutro", 0.5
    try:
        from app.audio.features import extrair_features

        pipeline = bundle["pipeline"]
        features = extrair_features(caminho).reshape(1, -1)
        classes = list(pipeline.classes_)
        proba = pipeline.predict_proba(features)[0]
        idx_pos = classes.index(1) if 1 in classes else classes.index("violencia")
        conf_pos = float(proba[idx_pos])
    except Exception as exc:
        LOG.warning("Classificador acústico falhou (%s); trilha acústica neutra.", exc)
        return "neutro", 0.5
    if conf_pos >= 0.5:
        return "violencia", round(conf_pos, 4)
    return "neutro", round(1.0 - conf_pos, 4)


def _transcrever_seguro(caminho) -> str:
    """Transcreve o áudio (Whisper local); degrada para vazio se o ASR estiver indisponível."""
    from app.audio.transcricao import transcrever

    try:
        return transcrever(caminho)
    except Exception as exc:
        LOG.warning("Transcrição indisponível (%s); seguindo só com a trilha acústica.", exc)
        return ""


def inferir(caminho) -> dict[str, Any]:
    """Análise dupla do áudio → evidência unificada (acústico + transcrição→texto unificado)."""
    from app.texto.nlp import analisar

    transcricao = _transcrever_seguro(caminho)
    texto_evid = analisar(transcricao)
    rotulo, confianca = classificar_acustico(caminho)
    return evidencia_audio_unificada((rotulo, confianca), transcricao, texto_evid)
