"""Classificação de risco em áudio a partir da transcrição (função pura).

Abordagem determinística por **palavras-chave** sobre a transcrição, devolvendo a evidência
padronizada ``{categoria, confianca}`` (contrato §3). A confiança cresce com o nº de termos
encontrados; a fusão (Fase 3) usa o limiar de 0.7 para decidir o peso do sinal.

Categorias (prioridade de desempate): violencia > depressao_pos_parto > ansiedade > fadiga > neutro.
"""

from __future__ import annotations

import unicodedata

from app.schemas import evidencia_audio

# Ordem = prioridade de desempate (mais grave primeiro).
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
    """Classifica a categoria de risco de uma transcrição (função pura)."""
    norm = _normalizar(transcricao or "")
    contagem = {
        cat: sum(1 for termo in termos if termo in norm) for cat, termos in TERMOS.items()
    }
    melhor = max(TERMOS, key=lambda c: contagem[c])  # ordem do dict desempata
    if contagem[melhor] == 0:
        return evidencia_audio("neutro", 0.5)
    return evidencia_audio(melhor, _confianca(contagem[melhor]))


def inferir(caminho) -> dict:
    """Transcreve o áudio (Fase 1) e classifica a categoria de risco → evidência padronizada."""
    from app.audio.transcricao import transcrever

    return classificar(transcrever(caminho))
